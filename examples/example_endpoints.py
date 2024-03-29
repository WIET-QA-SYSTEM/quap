import json
import logging
import uuid
from typing import Union, Any, Optional
from pathlib import Path
from uuid import UUID

from sqlalchemy import exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from haystack.nodes import FARMReader, PreProcessor
from haystack.document_stores.utils import eval_data_from_json

from quap.data import DataCorpus, Document, Dataset

from quap.data.orm import start_mappers, metadata
from quap.data.repository import DataCorpusRepository, DocumentRepository, DatasetRepository
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE

from quap.ml.pipelines import QAPipeline
from quap.ml.nodes import IndexedBM25, IndexedDPR

from quap.utils.dataset_downloader import DatasetDownloader
from quap.utils.persistent_cache import persistent_cache


logger = logging.getLogger('quap')


# Create a data corpus
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
metadata.create_all(engine)
session = sessionmaker(bind=engine, expire_on_commit=False)()

start_mappers()

corpus_repository = DataCorpusRepository(session)
dataset_repository = DatasetRepository(session)
document_repository = DocumentRepository(session)


bm25_retriever: Optional[IndexedBM25] = None
dpr_retriever: Optional[IndexedDPR] = None
farm_reader: Optional[FARMReader] = None


def _load_qa_models(
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        use_gpu: bool = False
) -> tuple[Union[IndexedDPR, IndexedBM25], FARMReader]:

    global bm25_retriever, dpr_retriever, farm_reader

    # setting up the retriever
    if retriever_type == 'bm25':
        bm25_retriever = bm25_retriever or IndexedBM25(ELASTICSEARCH_STORAGE)
        retriever = bm25_retriever
    elif retriever_type == 'dpr':

        if dpr_retriever is None \
                or dpr_retriever.passage_encoder.name != dpr_context_encoder \
                or dpr_retriever.query_encoder.name != dpr_question_encoder:
            dpr_retriever = IndexedDPR(
                document_store=ELASTICSEARCH_STORAGE,
                query_embedding_model=dpr_question_encoder,
                passage_embedding_model=dpr_context_encoder,
                use_gpu=use_gpu
            )

        retriever = dpr_retriever
    else:
        # TODO maybe better use fallback with some kind of warning?
        raise ValueError(f'unknown retriever type - {retriever_type}')

    # setting up the reader
    if farm_reader is None or farm_reader.name != reader_encoder:
        farm_reader = FARMReader(reader_encoder, use_gpu=use_gpu)

    return retriever, farm_reader


def get_data_corpora() -> list[dict[str, Any]]:
    corpora = []
    for corpus in corpus_repository.list():
        corpora.append({
            'id': corpus.id,
            'name': corpus.name,
            'document_names': [doc.name for doc in corpus.documents]
        })
    return corpora


def upload(paths: Union[list[str], str],
           data_corpus_id: Optional[UUID] = None,
           data_corpus_name: Optional[str] = None):

    if isinstance(paths, (str, Path)):
        paths = [paths]

    paths = [Path(path) for path in paths]

    try:
        if data_corpus_id is not None:
            corpus = corpus_repository.get(data_corpus_id)
        elif data_corpus_name is not None:
            corpus = DataCorpus(data_corpus_name)
        else:
            raise ValueError('either `data_corpus_id` or `data_corpus_name` must be passed')

        name2obj: dict[str, Document] = {document.name: document for document in corpus.documents}
        for path in paths:
            with path.open('r', encoding='utf-8') as f:
                text = f.read()

            if path.name in name2obj:
                existing_doc = name2obj[path.name]
                existing_doc.corpus = None
                document_repository.delete(existing_doc)

            doc = Document(path.name, 'en', corpus, text)
            ELASTICSEARCH_STORAGE.add_document(doc)

            # TODO remove file from disk in case of eventual endpoint?

        corpus_repository.add(corpus)
        corpus_repository.commit()

    except exc.SQLAlchemyError as ex:
        session.rollback()
        raise ex


def predict(
        corpus_id: UUID,
        questions: Union[list[str], str],
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        params: dict = None
) -> list[dict[str, Any]]:

    corpus = corpus_repository.get(corpus_id)
    retriever, reader = _load_qa_models(retriever_type, dpr_question_encoder, dpr_context_encoder, reader_encoder)

    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    answers = pipeline(corpus, questions)

    print(answers)
    # TODO what type answers are?


# @persistent_cache('evaluate')
def evaluate(
    dataset_id: Optional[UUID] = None,
    dataset_name: Optional[str] = None,
    retriever_type: str = 'dpr',
    dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
    dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
    reader_encoder: str = 'deepset/roberta-base-squad2',
):

    if dataset_id is not None:
        dataset = dataset_repository.get(dataset_id)
    elif dataset_name is not None:
        dataset_downloader = DatasetDownloader()
        if dataset_name == DatasetDownloader.NQ_KEY or dataset_name == 'natural_questions':
            dataset_path = dataset_downloader.download(DatasetDownloader.NQ_KEY)
        elif dataset_name == DatasetDownloader.SQUAD_KEY:
            dataset_path = dataset_downloader.download(DatasetDownloader.SQUAD_KEY)
        else:
            logger.warning(f"No such dataset key as '{dataset_name}'")
            raise ValueError(f"No such dataset key as '{dataset_name}'")

        original_docs, _ = eval_data_from_json(filename=str(dataset_path),
                                               max_docs=None,
                                               preprocessor=None)

        split_preprocessor = PreProcessor(split_by='word',
                                          split_length=200,
                                          split_overlap=0,
                                          split_respect_sentence_boundary=False,
                                          clean_empty_lines=False,
                                          clean_whitespace=False)

        preprocessed_docs, labels = eval_data_from_json(filename=str(dataset_path),
                                                        max_docs=None,
                                                        preprocessor=split_preprocessor)
        try:
            # check if already exists with such name - if not -> add uuid
            corpus = corpus_repository.get_by_name(dataset_name)  # is it working like it should?
            if corpus is not None:
                dataset_name += '_'
                dataset_name += str(uuid.uuid4())

            # Czy .add() i .commit() powinny być w tym miejscu, czy jakoś na końcu?

            corpus = DataCorpus(name=dataset_name)
            for original_doc in original_docs:
                Document(original_doc.meta['name'], 'en', corpus)

            dataset = Dataset(name=dataset_name, corpus=corpus)
            dataset_repository.add(dataset)
            dataset_repository.commit()

            ELASTICSEARCH_STORAGE.add_dataset(preprocessed_docs=preprocessed_docs,
                                              preprocessed_labels=labels,
                                              original_docs=original_docs,
                                              preprocessed_docs_index=corpus.contexts_index,
                                              preprocessed_labels_index=dataset.labels_index,
                                              original_docs_index=corpus.original_documents_index)

            # TODO remove file from disk in case of eventual endpoint?

        except exc.SQLAlchemyError as ex:
            session.rollback()
            raise ex
    else:
        raise ValueError("In order to evaluate a dataset pass `dataset_id` or `dataset_name`")



    retriever, reader = _load_qa_models(retriever_type, dpr_question_encoder, dpr_context_encoder, reader_encoder)

    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    metrics = pipeline.eval(dataset)

    print(metrics)
