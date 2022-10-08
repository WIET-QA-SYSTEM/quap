from uuid import uuid4, UUID

from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry, relationship, backref

from .models import (
    DataCorpus,
    Dataset,
    StoredDocument,
    StoredDocumentFragment,
)

metadata = MetaData()
mapper_registry = registry(metadata)

data_corpora = Table(
    'data_corpora',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('dpr_uuid', UUID(as_uuid=True), nullable=True),
    Column('elasticsearch_uuid', UUID(as_uuid=True), nullable=True)
)

documents = Table(
    'documents',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(256), nullable=False),
    Column('data_corpus_id', UUID(as_uuid=True), ForeignKey('data_corpora.id', ondelete='CASCADE'), nullable=False),
    Column('content_path', String(256), nullable=False)
)

document_fragments = Table(
    'document_fragments',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('document_offset', Integer(), nullable=False),
    Column('length', Integer(), nullable=False),
    Column('document_id', UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
)

datasets = Table(
    'datasets',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('data_corpus_id', UUID(as_uuid=True), ForeignKey('data_corpora.id'), nullable=False)
)


def start_mappers():
    mapper_registry.map_imperatively(
        DataCorpus,
        data_corpora,
    )

    mapper_registry.map_imperatively(
        Dataset,
        datasets,
        properties={
            'corpus': relationship(DataCorpus)
        }
    )

    mapper_registry.map_imperatively(
        StoredDocument,
        documents,
        properties={
            'corpus': relationship(DataCorpus, backref=backref('documents', passive_deletes=True))
        }
    )

    mapper_registry.map_imperatively(
        StoredDocumentFragment,
        document_fragments,
        properties={
            'document': relationship(StoredDocument, backref=backref('document_fragments', passive_deletes=True))
        }
    )
