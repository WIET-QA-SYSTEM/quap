from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, Union
from uuid import UUID, uuid4

from quap.utils.index_name import normalize_index_name


@dataclass
class DataCorpus:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    documents: list[Document] = field(default_factory=list, init=False)

    @property
    def language(self) -> str:
        counter = Counter([doc.language for doc in self.documents])
        return counter.most_common(1)[0][0] if counter else 'en'

    # TODO should we keep it here?
    # TODO if we move it somewhere else, then models.py will have no relation to any data storage
    @property
    def original_documents_index(self) -> str:
        return normalize_index_name(f'{self.id}-original')

    @property
    def contexts_index(self) -> str:
        return normalize_index_name(f'{self.id}-contexts')

    # def add_documents(self, documents: Union[Document, list[Document]]):
    #     if isinstance(documents, Document):
    #         documents = [documents]
    #     # TODO define __eq__ for models
    #     # if any(document.corpus != self for document in documents):
    #     #     raise ValueError('all Document objects must point to this corpus')
    #     for document in documents:
    #         self.documents.append(document)


@dataclass
class Dataset:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    corpus: DataCorpus


@dataclass
class Document:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    language: str
    corpus: DataCorpus
    _text: Optional[str] = field(default=None)

    # TODO this should load document from document store. Do we need this?
    # TODO maybe the repository should use document store to load the text itself?
    @cached_property
    def text(self) -> str:
        return self._text or ''


@dataclass
class Context:
    id: UUID = field(default_factory=uuid4, init=False)
    document: Document
    offset: int
    length: int

    def __len__(self) -> int:
        return self.length

    @property
    def text(self) -> str:
        return self.document.text[self.offset:self.offset + self.length]
