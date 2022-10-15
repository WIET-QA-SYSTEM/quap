import os

from quap.document_stores.data_corpus_store import DataCorpusStore


elasticsearch_config = {
    'scheme': os.environ['ELASTICSEARCH_SCHEME'],
    'host': os.environ['ELASTICSEARCH_HOST'],
    'port': os.environ['ELASTICSEARCH_PORT'],
}

ELASTICSEARCH_STORAGE = DataCorpusStore(**elasticsearch_config, index='default')
