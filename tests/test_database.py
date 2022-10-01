from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from quap.data import DataCorpus, Dataset
from quap.data.repository import DataCorpusRepository, DatasetRepository

from helpers import generate_random_data_corpora, generate_random_datasets


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
    session.commit()

    corpus = repo.get(data_corpus_id)

    assert corpus.id == data_corpus_id
    assert corpus.name == 'another_corpus'
    assert corpus.dpr_uuid is None
    assert corpus.elasticsearch_uuid == elasticsearch_uuid


@pytest.mark.integration_test
def test_data_corpus_repository_listing(session: Session):
    repo = DataCorpusRepository(session)

    corpora = generate_random_data_corpora(10)
    for corpus in corpora:
        repo.add(corpus)
    repo.commit()

    assert repo.list() == corpora


@pytest.mark.integration_test
def test_dataset_repository_adding(session: Session):
    repo = DatasetRepository(session)

    corpus = DataCorpus('anabilitics')
    dataset = Dataset('anabilitics', corpus)

    repo.add(dataset)
    repo.commit()

    corpora_rows = session.execute('SELECT name, dpr_uuid, elasticsearch_uuid FROM data_corpora')
    assert list(corpora_rows) == [('anabilitics', None, None)]

    dataset_rows = session.execute('SELECT name, data_corpus_id FROM datasets')
    assert list(dataset_rows) == [('anabilitics', corpus.id)]


@pytest.mark.integration_test
def test_dataset_repository_getting(session: Session):
    repo = DatasetRepository(session)

    data_corpus_id = uuid4()
    dataset_id = uuid4()

    session.execute('INSERT INTO data_corpora (id, name, dpr_uuid, elasticsearch_uuid) '
                    'VALUES (:data_corpus_id, \'another_corpus\', null, null)',
                    {'data_corpus_id': data_corpus_id})

    session.execute('INSERT INTO datasets (id, name, data_corpus_id) '
                    'VALUES (:dataset_id, \'another_dataset\', :data_corpus_id)',
                    {'dataset_id': dataset_id, 'data_corpus_id': data_corpus_id})
    session.commit()

    dataset = repo.get(dataset_id)

    assert dataset.id == dataset_id
    assert dataset.name == 'another_dataset'

    assert dataset.corpus.id == data_corpus_id
    assert dataset.corpus.name == 'another_corpus'
    assert dataset.corpus.dpr_uuid is None
    assert dataset.corpus.elasticsearch_uuid is None


@pytest.mark.integration_test
def test_dataset_repository_listing(session: Session):
    repo = DatasetRepository(session)

    datasets = generate_random_datasets(10)
    for dataset in datasets:
        repo.add(dataset)
    repo.commit()

    assert repo.list() == datasets
