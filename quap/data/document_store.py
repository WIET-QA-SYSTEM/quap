from .fragmented_store import CorpusFragmentedStore
import os

elasticsearch_config = {
    'scheme': os.environ['ELASTICSEARCH_SCHEME'],
    'host': os.environ['ELASTICSEARCH_HOST'],
    'port': os.environ['ELASTICSEARCH_PORT'],
}

ELASTIC_SEARCH_STORAGE = CorpusFragmentedStore(**elasticsearch_config, index='default')