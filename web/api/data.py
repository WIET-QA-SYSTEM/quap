from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import exc
from haystack.nodes import PreProcessor
from haystack.document_stores import eval_data_from_json

from quap.data import DataCorpus, Document, Dataset
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.utils.preprocessing import FormatUnifier
from quap.utils.dataset_downloader import DatasetDownloader

from .repositories import document_repository, corpus_repository, dataset_repository, session


def get_data_corpora() -> list[dict[str, Any]]:
    corpora = []
    for corpus in corpus_repository.list():
        corpora.append({
            'id': corpus.id,
            'name': corpus.name,
            'language': corpus.language,
            'document_names': [doc.name for doc in corpus.documents]
        })
    return corpora


def get_datasets() -> list[dict[str, Any]]:
    datasets = []
    for dataset in dataset_repository.list():
        datasets.append({
            'id': dataset.id,
            'name': dataset.name,
            'corpus': {
                'id': dataset.corpus.id,
                'name': dataset.corpus.name,
                'language': dataset.corpus.language,
                'document_names': [doc.name for doc in dataset.corpus.documents]
            }
        })
    return datasets


def upload_corpus(files: list[bytes],
                  filenames: list[str],
                  data_corpus_id: Optional[UUID] = None,
                  data_corpus_name: Optional[str] = None):

    try:
        if data_corpus_id is not None:
            corpus = corpus_repository.get(data_corpus_id)
        elif data_corpus_name is not None:
            corpus = DataCorpus(data_corpus_name)
        else:
            raise ValueError('either `data_corpus_id` or `data_corpus_name` must be passed')

        name2obj: dict[str, Document] = {document.name: document for document in corpus.documents}
        format_unifier = FormatUnifier()

        for file_content, filename in zip(files, filenames):
            try:
                text = format_unifier.extract_text(file_content)
            except ValueError as ex:
                continue  # TODO show error?

            if not text:
                continue  # TODO show error?

            if filename in name2obj:
                existing_doc = name2obj[filename]
                existing_doc.corpus = None
                document_repository.delete(existing_doc)

            doc = Document(filename, format_unifier.detect_language(text), corpus, text)
            ELASTICSEARCH_STORAGE.add_document(doc)

            # TODO remove file from disk in case of eventual endpoint?

        corpus_repository.add(corpus)
        corpus_repository.commit()

    except exc.SQLAlchemyError as ex:
        session.rollback()  # TODO should we move it to the repository?
        raise ex


# TODO add uploading custom dataset?
def upload_dataset(dataset_name: str):
    format_unifier = FormatUnifier()
    dataset_downloader = DatasetDownloader()
    # todo should we handle this exception by displaying something on the website?
    dataset_path = dataset_downloader.download(dataset_name)

    original_docs, _ = eval_data_from_json(filename=str(dataset_path),
                                           max_docs=None,
                                           preprocessor=None)

    split_preprocessor = PreProcessor(split_by='word',
                                      split_length=200,
                                      split_overlap=0,
                                      split_respect_sentence_boundary=False,
                                      clean_empty_lines=False,
                                      clean_whitespace=False,
                                      progress_bar=False)

    preprocessed_docs, labels = eval_data_from_json(filename=str(dataset_path),
                                                    max_docs=None,
                                                    preprocessor=split_preprocessor)

    try:
        corpus = DataCorpus(name=dataset_name)
        for original_doc in original_docs:
            Document(original_doc.meta['name'], format_unifier.detect_language(original_doc.content), corpus)

        dataset = Dataset(name=dataset_name, corpus=corpus)
        dataset_repository.add(dataset)
        dataset_repository.commit()
    except exc.SQLAlchemyError as ex:
        session.rollback()
        raise ex

    ELASTICSEARCH_STORAGE.add_dataset(dataset=dataset,
                                      preprocessed_docs=preprocessed_docs,
                                      preprocessed_labels=labels,
                                      original_docs=original_docs)
