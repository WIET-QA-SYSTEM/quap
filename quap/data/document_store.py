from haystack.document_stores import ElasticsearchDocumentStore
import os

elasticsearch_config = {
    'scheme': os.environ['ELASTICSEARCH_SCHEME'],
    'host': os.environ['ELASTICSEARCH_HOST'],
    'port': os.environ['ELASTICSEARCH_PORT'],
}

ELASTIC_SEARCH_STORAGE = ElasticsearchDocumentStore(**elasticsearch_config, index='default')