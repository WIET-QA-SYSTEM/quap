from uuid import uuid4
import os

import pytest

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from quap.data import DataCorpus, Dataset
from quap.data.repository import DataCorpusRepository, DatasetRepository


@pytest.fixture(scope='module')
def engine() -> Engine:
    engine = create_engine(os.environ['POSTGRESQL_CONNECTION_STRING'])
    return engine


def test_data_corpus_repository_adding(engine: Engine):
    repo = DataCorpusRepository(engine)
    session = repo.session

    corpus = DataCorpus('sample_corpus')
    repo.add(corpus)
    repo.commit()

    rows = session.execute('SELECT name, dpr_uuid, elasticsearch_uuid FROM data_corpora')
    assert list(rows) == [('sample_corpus', None, None)]


def test_data_corpus_repository_getting(engine: Engine):
    repo = DataCorpusRepository(engine)
    session = repo.session

    data_corpus_id = uuid4()
    elasticsearch_uuid = uuid4()

    session.execute('INSERT INTO data_corpora (id, name, dpr_uuid, elasticsearch_uuid)'
                    f'VALUES ({data_corpus_id}, "another_corpus", null, {elasticsearch_uuid})')

    corpus = repo.get(data_corpus_id)

    assert corpus.id == data_corpus_id
    assert corpus.name == 'another_corpus'
    assert corpus.dpr_uuid is None
    assert corpus.elasticsearch_uuid == elasticsearch_uuid
