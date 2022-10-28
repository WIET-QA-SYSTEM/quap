from uuid import UUID

from fastapi import APIRouter, File, UploadFile, Response
from starlette import status
from sqlalchemy import exc

from quap.data import DataCorpus, Document
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.utils.preprocessing import FormatUnifier

# todo how to make these relative imports? always had a problem with that
from repositories import (
    session,
    dataset_repository,
    corpus_repository,
    document_repository
)
from models.data import (
    DataCorporaGETResponse,
    DatasetsGETResponse,
    CreateDataCorpusPOSTRequest
)


router = APIRouter(prefix='/data')
format_unifier = FormatUnifier()


@router.get('/corpora', response_model=DataCorporaGETResponse)
async def get_corpora():
    corpora = corpus_repository.list()
    datasets = dataset_repository.list()
    datasets_corpora_ids = set([dataset.id for dataset in datasets])

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
    response = [
        {'id': dataset.id, 'name': dataset.name, 'corpus_id': dataset.corpus.id}
        for dataset in datasets
    ]
    return {'datasets': response}
