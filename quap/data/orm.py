from uuid import uuid4, UUID

from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry, relationship, backref

from .models import (
    DataCorpus,
    Dataset,
    Document,
    Context,
)

metadata = MetaData()
mapper_registry = registry(metadata)

data_corpora = Table(
    'data_corpora',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False, unique=True, index=True),
)

documents = Table(
    'documents',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(256), nullable=False),
    Column('data_corpus_id', UUID(as_uuid=True), ForeignKey('data_corpora.id', ondelete='CASCADE'), nullable=False),
)

datasets = Table(
    'datasets',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False, unique=True),
    Column('data_corpus_id', UUID(as_uuid=True), ForeignKey('data_corpora.id'), nullable=False)
)


def start_mappers():
    mapper_registry.map_imperatively(
        DataCorpus,
        data_corpora,
        # properties={
        #     'documents': relationship(Document, viewonly=True)
        # }
    )

    mapper_registry.map_imperatively(
        Dataset,
        datasets,
        properties={
            'corpus': relationship(DataCorpus)
        }
    )

    # TODO using this for now :) not great actually, cause it won't work without database
    mapper_registry.map_imperatively(
        Document,
        documents,
        properties={
            'corpus': relationship(DataCorpus, backref=backref('documents', uselist=True))
        }
    )
