import os
from data_storage.schema import DataCorpus, Document
from data_storage.schema import BaseSession
from quap.utils.cache.indexation_cache import IndexationCache


def test_cache_persistence():
    # Create data corpus
    session = BaseSession()
    corpus = DataCorpus(name='sample_corpus')
    session.add(corpus)
    session.commit()

    corpus.cache_dpr_index(session, b'test_bytes')

    assert os.path.exists(corpus.dpr_cache[0].binary_index_path), "Cache binary file not present"

    session.delete(corpus)
    session.commit()

def test_cache_invalidation():
    # Create data corpus
    session = BaseSession()
    corpus = DataCorpus(name='sample_corpus')
    session.add(corpus)
    session.commit()

    corpus.cache_dpr_index(session, b'test_bytes')

    corpus.upload_document(
    session, "sample_document.pdf", "sample document_content")

    assert len(corpus.dpr_cache) == 0, "Cache not invalidated after update"

    session.delete(corpus)
    session.commit()
