from uuid import uuid4, UUID

from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry, relationship

from .models import (
    DataCorpus,
    Dataset
)

metadata_obj = MetaData()
mapper_registry = registry(metadata_obj)

data_corpora = Table(
    'data_corpora',
    metadata_obj,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('dpr_uuid', UUID(as_uuid=True), nullable=True),
    Column('elasticsearch_uuid', UUID(as_uuid=True), nullable=True)
)

datasets = Table(
    'datasets',
    metadata_obj,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('data_corpus_id', Integer, ForeignKey('data_corpora.id'), nullable=False)
)


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
