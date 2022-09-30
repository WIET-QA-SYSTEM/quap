from uuid import uuid4
import os

import pytest
from sqlalchemy.orm import Session

from quap.data import DataCorpus, Dataset
from quap.data.repository import DataCorpusRepository, DatasetRepository


@pytest.mark.integration_test
def test_data_corpus_repository_adding(session: Session):
    repo = DataCorpusRepository(session)

    corpus = DataCorpus('sample_corpus')
    repo.add(corpus)
    repo.commit()

    rows = session.execute('SELECT name, dpr_uuid, elasticsearch_uuid FROM data_corpora')
    assert list(rows) == [('sample_corpus', None, None)]


@pytest.mark.integration_test
def test_data_corpus_repository_getting(session: Session):
    repo = DataCorpusRepository(session)

    data_corpus_id = uuid4()
    elasticsearch_uuid = uuid4()

    session.execute('INSERT INTO data_corpora (id, name, dpr_uuid, elasticsearch_uuid) '
                    'VALUES (:data_corpus_id, \'another_corpus\', null, :elasticsearch_uuid)',
                    {'data_corpus_id': data_corpus_id, 'elasticsearch_uuid': elasticsearch_uuid})

    corpus = repo.get(data_corpus_id)

    assert corpus.id == data_corpus_id
    assert corpus.name == 'another_corpus'
    assert corpus.dpr_uuid is None
    assert corpus.elasticsearch_uuid == elasticsearch_uuid
