from pathlib import Path
from typing import Any, Optional, Union
from uuid import UUID

from numpy import byte

from quap.data import DataCorpus, Document
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from sqlalchemy import exc

from .db_access import document_repository, corpus_repository, dataset_repository, session


def get_data_corpora() -> list[dict[str, Any]]:
    corpora = []
    for corpus in corpus_repository.list():
        corpora.append({
            'id': corpus.id,
            'name': corpus.name,
            'document_names': [doc.name for doc in corpus.documents]
        })
    return corpora


def get_datasets() -> list[dict[str, Any]]:
    datasets = []
    for dataset in dataset_repository.list():
        datasets.append({
            'id': dataset.id,
            'name': dataset.name,
            'corpus_id': dataset.corpus.id
        })
    return datasets


def upload(files: list[bytes],
           filenames: list[str],
           data_corpus_id: Optional[UUID] = None,
           data_corpus_name: Optional[str] = None):

    try:
        if data_corpus_id is not None:
            corpus = corpus_repository.get(data_corpus_id)
        elif data_corpus_name is not None:
            corpus = DataCorpus(data_corpus_name)
        else:
            raise ValueError(
                'either `data_corpus_id` or `data_corpus_name` must be passed')

        name2obj: dict[str, Document] = {
            document.name: document for document in corpus.documents}

        for file_content, filename in zip(files, filenames):
            # TODO check the type of file and extract text (assuming only txts for now)
            text = file_content.decode('utf-8')

            if filename in name2obj:
                existing_doc = name2obj[filename]
                existing_doc.corpus = None
                document_repository.delete(existing_doc)

            doc = Document(filename, 'en', corpus, text)  # TODO language detection
            ELASTICSEARCH_STORAGE.add_document(doc)

            # TODO remove file from disk in case of eventual endpoint?

        corpus_repository.add(corpus)
        corpus_repository.commit()

    except exc.SQLAlchemyError as ex:
        session.rollback()  # TODO should we move it to the repository?
        raise ex
