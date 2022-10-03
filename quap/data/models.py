from typing import Optional
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import os

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import DensePassageRetriever, ElasticsearchRetriever, BaseRetriever
from haystack import Document

from .types import RetrieverType


@dataclass
class DataCorpus:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    dpr_uuid: Optional[UUID] = field(default=None, init=False)
    elasticsearch_uuid: Optional[UUID] = field(default=None, init=False)

    def __post_init__(self):
        self._elasticsearch_config = {
            'scheme': os.environ['ELASTICSEARCH_SCHEME'],
            'host': os.environ['ELASTICSEARCH_HOST'],
            'port': os.environ['ELASTICSEARCH_PORT'],
            'update_existing_documents': True,
        }

    def get_storage(self, retriever_type: RetrieverType) -> ElasticsearchDocumentStore:
        if retriever_type == 'dpr':
            if self.dpr_uuid is None:
                raise ValueError('DPR index has not been created yet')
            return ElasticsearchDocumentStore(**self._elasticsearch_config, index=str(self.dpr_uuid))

        elif retriever_type == 'elasticsearch':
            if self.elasticsearch_uuid is None:
                raise ValueError('Elasticsearch index has not been created yet')
            return ElasticsearchDocumentStore(**self._elasticsearch_config, index=str(self.elasticsearch_uuid))

        else:
            raise ValueError(f'unknown retriever type: {retriever_type}')

    # TODO do we really want it to be here?
    def get_retriever(self, retriever_type: RetrieverType) -> BaseRetriever:  # another return type?
        if retriever_type == 'dpr':
            return DensePassageRetriever(self.get_storage(retriever_type))
        elif retriever_type == 'elasticsearch':
            return ElasticsearchRetriever(self.get_storage(retriever_type))
        else:
            raise ValueError(f'unknown retriever type: {retriever_type}')

    # TODO do we really want to keep all the embeddings updated?
    def add_document(self, document_name: str, document_text: str) -> None:
        dpr_storage = self.get_storage('dpr')
        elastic_search_storage = self.get_storage('elasticsearch')

        document_repr = Document(content=document_text, id=document_name, content_type='text')

        dpr_storage.write_documents(documents=[document_repr], index=self.dpr_uuid)
        dpr_storage.update_embeddings(self.get_retriever('dpr'))
        elastic_search_storage.write_documents(documents=[document_repr], index=self.elasticsearch_uuid)


@dataclass
class Dataset:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    corpus: DataCorpus
