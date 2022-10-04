from typing import Optional
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import os

from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Document

from .types import RetrieverType


@dataclass
class DataCorpus:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    dpr_uuid: Optional[UUID] = field(default_factory=uuid4, init=False)
    elasticsearch_uuid: Optional[UUID] = field(default_factory=uuid4, init=False)

    def add_document(self, storage, document_name: str, document_text: str) -> None:
        document_repr = Document(content=document_text, id=document_name, content_type='text')

        storage.write_documents(documents=[document_repr], index=str(self.elasticsearch_uuid))
        storage.write_documents(documents=[document_repr], index=str(self.dpr_uuid))

@dataclass
class Dataset:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    corpus: DataCorpus
