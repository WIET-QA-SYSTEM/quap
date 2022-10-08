from typing import Optional
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import os

from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Document
from sqlalchemy import event

from .types import RetrieverType

@dataclass
class DataCorpus:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    dpr_uuid: Optional[UUID] = field(default_factory=uuid4, init=False)
    elasticsearch_uuid: Optional[UUID] = field(default_factory=uuid4, init=False)

@dataclass
class StoredDocument:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    corpus: DataCorpus
    content_path: str

@event.listens_for(StoredDocument, 'after_delete')
def remove_file_from_storage(mapper, connection, target: StoredDocument):
    if os.path.exists(target.content_path):
        os.remove(target.content_path)
    else:
        print("Warning! Trying to remove a file that does not exist:", target.content_path)

@dataclass
class StoredDocumentFragment:
    id: UUID = field(default_factory=uuid4, init=False)
    document_offset: int
    length: int
    document: StoredDocument

@dataclass
class Dataset:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    corpus: DataCorpus
