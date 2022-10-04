import os
from turtle import update

from haystack.document_stores import ElasticsearchDocumentStore
from matplotlib.pyplot import text
from sqlalchemy.orm import Session

from quap.data.models import DataCorpus, StoredDocument, StoredDocumentFragment
from quap.data.repository import StoredDocumentFragmentRepository, StoredDocumentRepository

from haystack import Document
from typing import Union, Optional
from uuid import uuid4


class CorpusFragmentedStore(ElasticsearchDocumentStore):

    def __init__(self, split_strategy='naive', split_size=250, storage_directory='documents',
                 host: str = "localhost", port: int = 9200, scheme: str = "http",
                 index: str = "document"):
        super().__init__(host=host, port=port, scheme=scheme, index=index)
        self.split_strategy = split_strategy
        self.split_size = split_size
        self.storage_directory = storage_directory

        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def add_document(self, db_session: Session, data_corpus: DataCorpus, document_name: str, document_content: str):
        if len(document_content) == 0:
            print("Warning! Empty document not saved")
            return

        doc_repository = StoredDocumentRepository(db_session)

        # If document exists remove all it's fragments from elastic search
        if doc_repository.exists_in_corpus(document_name, data_corpus):
            self.remove_document(db_session, data_corpus, document_name)

        if self.split_strategy == 'naive':
            fragments = [
                document_content[i*self.split_size:i *
                                 self.split_size+self.split_size]
                for i in range((len(document_content)-1) // self.split_size + 1)
            ]

            content_path = os.path.join(
                self.storage_directory, str(uuid4()) + '.txt')

            with open(content_path, 'w') as output_file:
                output_file.write(document_content)

            new_document = StoredDocument(
                document_name, data_corpus, content_path)
            doc_repository.add(new_document)
            doc_repository.commit()

            fragment_repository = StoredDocumentFragmentRepository(db_session)

            fragment_repr = [
                StoredDocumentFragment(
                    self.split_size*i, len(fragments[i]), new_document)
                for i in range(len(fragments))
            ]

            for stored_fragment, fragment_content in zip(fragment_repr, fragments):
                fragment_repository.add(stored_fragment)
                fragment_repository.commit()

                es_document_repr = Document(content=fragment_content, id=str(
                    stored_fragment.id), content_type='text')

                super().write_documents(
                    [es_document_repr],
                    index=str(data_corpus.dpr_uuid)
                )

                super().write_documents(
                    [es_document_repr],
                    index=str(data_corpus.elasticsearch_uuid)
                )
        else:
            raise ValueError(
                f"Unsupported split strategy: {self.split_strategy}")

    def remove_document(self, db_session: Session, data_corpus: DataCorpus, document_name: str):
        doc_repository = StoredDocumentRepository(db_session)
        doc_repository.remove_from_corpus(document_name, data_corpus)
        doc_repository.commit()
