from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from quap.data import DataCorpus, Dataset, Document
from quap.data.repository import DataCorpusRepository, DatasetRepository, DocumentRepository

from helpers import generate_random_data_corpora, generate_random_datasets


@pytest.mark.integration_test
def test_data_corpus_repository_adding(session: Session):
    repo = DataCorpusRepository(session)

    corpus = DataCorpus('sample_corpus')
    repo.add(corpus)
    repo.commit()

    rows = session.execute('SELECT name FROM data_corpora')
    assert list(rows) == [('sample_corpus',)]


@pytest.mark.integration_test
def test_data_corpus_repository_getting(session: Session):
    repo = DataCorpusRepository(session)

    data_corpus_id = uuid4()

    session.execute('INSERT INTO data_corpora (id, name) '
                    'VALUES (:data_corpus_id, \'another_corpus\')',
                    {'data_corpus_id': data_corpus_id})
    session.commit()

    corpus = repo.get(data_corpus_id)

    assert corpus.id == data_corpus_id
    assert corpus.name == 'another_corpus'

@pytest.mark.integration_test
def test_data_corpus_repository_listing(session: Session):
    repo = DataCorpusRepository(session)

    corpora = generate_random_data_corpora(10)
    for corpus in corpora:
        repo.add(corpus)
    repo.commit()

    assert repo.list() == corpora


@pytest.mark.integration_test
def test_data_corpus_repository_documents_modification(session: Session):
    repo = DataCorpusRepository(session)
    doc_repo = DocumentRepository(session)

    # initial position
    corpus = DataCorpus('sample')
    doc1 = Document('doc1', 'en', corpus, 'document 1 content')
    doc2 = Document('doc2', 'fr', corpus, 'documento 2 le content :)')
    doc3 = Document('doc3', 'pl', corpus, 'kontent z dokumentu 3')

    repo.add(corpus)
    repo.commit()

    # verifying if correctly added
    corpus = repo.get(corpus.id)
    assert [doc.name for doc in corpus.documents] == ['doc1', 'doc2', 'doc3']
    assert [doc.language for doc in corpus.documents] == ['en', 'fr', 'pl']

    # modifying corpus
    doc2.corpus = None
    doc_repo.delete(doc2)
    doc_repo.commit()

    docx2 = Document('doc2', 'uk', corpus, 'український документ номер 2')

    repo.add(corpus)
    repo.commit()

    # verifying if correctly modified
    corpus = repo.get(corpus.id)
    assert [doc.name for doc in corpus.documents] == ['doc1', 'doc3', 'doc2']
    assert [doc.language for doc in corpus.documents] == ['en', 'pl', 'uk']


@pytest.mark.integration_test
def test_dataset_repository_adding(session: Session):
    repo = DatasetRepository(session)

    corpus = DataCorpus('anabilitics')
    dataset = Dataset('anabilitics', corpus)

    repo.add(dataset)
    repo.commit()

    corpora_rows = session.execute('SELECT name FROM data_corpora')
    assert list(corpora_rows) == [('anabilitics',)]

    dataset_rows = session.execute('SELECT name, data_corpus_id FROM datasets')
    assert list(dataset_rows) == [('anabilitics', corpus.id)]


@pytest.mark.integration_test
def test_dataset_repository_getting(session: Session):
    repo = DatasetRepository(session)

    data_corpus_id = uuid4()
    dataset_id = uuid4()

    session.execute('INSERT INTO data_corpora (id, name) '
                    'VALUES (:data_corpus_id, \'another_corpus\')',
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


@pytest.mark.integration_test
def test_dataset_repository_listing(session: Session):
    repo = DatasetRepository(session)

    datasets = generate_random_datasets(10)
    for dataset in datasets:
        repo.add(dataset)
    repo.commit()

    assert repo.list() == datasets
