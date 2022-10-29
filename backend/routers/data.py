from uuid import UUID

from fastapi import APIRouter, File, UploadFile, Response
from starlette import status
from sqlalchemy import exc

from haystack.nodes import PreProcessor
from haystack.document_stores import eval_data_from_json

from quap.data import DataCorpus, Document, Dataset
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.utils.preprocessing import FormatUnifier
from quap.utils.dataset_downloader import DatasetDownloader

# todo how to make these relative imports? always had a problem with that
from repositories import (
    session,
    dataset_repository,
    corpus_repository,
    document_repository
)
from models.data import (
    DataCorpusGETResponse,
    DataCorporaGETResponse,
    DatasetsGETResponse,
    CreateDataCorpusPOSTRequest,
    DownloadDatasetPOSTRequest
)


router = APIRouter(prefix='/data')
format_unifier = FormatUnifier()
dataset_downloader = DatasetDownloader()
split_preprocessor = PreProcessor(split_by='word', split_length=200, split_overlap=0,
                                  split_respect_sentence_boundary=False, clean_empty_lines=False,
                                  clean_whitespace=False, progress_bar=False)


@router.get('/corpora', response_model=DataCorporaGETResponse)
async def get_corpora():
    corpora = corpus_repository.list()
    datasets = dataset_repository.list()
    datasets_corpora_ids = set([dataset.corpus.id for dataset in datasets])

    response = []
    for corpus in corpora:
        response.append({
            'id': corpus.id,
            'name': corpus.name,
            'language': corpus.language,
            'documents': [
                {'id': document.id, 'name': document.name, 'language': document.language}
                for document in corpus.documents
            ],
            'frozen': corpus.id in datasets_corpora_ids
        })

    return {'corpora': response}


@router.post('/corpora')
async def create_corpus(request: CreateDataCorpusPOSTRequest):
    try:
        corpus = DataCorpus(request.name)
        corpus_repository.add(corpus)
        corpus_repository.commit()
    except exc.IntegrityError as ex:
        session.rollback()
        return Response(status_code=status.HTTP_409_CONFLICT)

    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/corpora/{corpus_id}')
async def upload_file_to_corpus(corpus_id: UUID, file: UploadFile = File(...)):
    try:
        corpus = corpus_repository.get(corpus_id)
    except exc.NoResultFound:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    datasets = dataset_repository.list()
    datasets_corpora_ids = set([dataset.corpus.id for dataset in datasets])
    if corpus.id in datasets_corpora_ids:
        # todo message - cannot modify frozen corpora
        return Response(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    filename = file.filename
    text = format_unifier.extract_text(await file.read())
    if not text:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    name2obj: dict[str, Document] = {document.name: document for document in corpus.documents}
    if filename in name2obj:
        existing_doc = name2obj[filename]
        existing_doc.corpus = None
        document_repository.delete(existing_doc)

    doc = Document(filename, format_unifier.detect_language(text), corpus, text)
    ELASTICSEARCH_STORAGE.add_document(doc)

    corpus_repository.add(corpus)
    corpus_repository.commit()


@router.get('/datasets', response_model=DatasetsGETResponse)
async def get_datasets():
    datasets = dataset_repository.list()

    response = []
    for dataset in datasets:
        corpus = dataset.corpus
        response.append({
            'id': dataset.id,
            'name': dataset.name,
            'corpus': {
                'id': corpus.id,
                'name': corpus.name,
                'language': corpus.language,
                'documents': [
                    {'id': document.id, 'name': document.name, 'language': document.language}
                    for document in corpus.documents
                ],
                'frozen': True
            }
        })

    return {'datasets': response}


# todo post for '/datasets' which creates a dataset, and '/datasets/{dataset_id}'
# todo for uploading squad files, return 409 conflict if used reserved name for dataset creation


@router.post('/datasets/download')
async def download_dataset(request: DownloadDatasetPOSTRequest):
    if not dataset_downloader.is_supported(request.name):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        dataset = dataset_repository.get_by_name(request.name)
        return Response(status_code=status.HTTP_200_OK)
    except exc.NoResultFound:
        pass

    dataset_path = dataset_downloader.download(request.name)

    original_docs, _ = eval_data_from_json(filename=str(dataset_path), preprocessor=None)
    preprocessed_docs, labels = eval_data_from_json(filename=str(dataset_path), preprocessor=split_preprocessor)

    try:
        corpus = DataCorpus(name=request.name)
        for original_doc in original_docs:
            Document(original_doc.meta['name'], format_unifier.detect_language(original_doc.content), corpus)

        dataset = Dataset(name=request.name, corpus=corpus)
        dataset_repository.add(dataset)
        dataset_repository.commit()
    except exc.SQLAlchemyError as ex:
        session.rollback()
        raise ex  # todo when can it be raised? is it caused by our fault or request params?

    ELASTICSEARCH_STORAGE.add_dataset(dataset=dataset,
                                      preprocessed_docs=preprocessed_docs,
                                      preprocessed_labels=labels,
                                      original_docs=original_docs)
