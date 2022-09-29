import os

from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy import event
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import DensePassageRetriever, ElasticsearchRetriever
from haystack import Document

from .config import engine_path, documents_path, dpr_cache_path
from uuid import uuid4

Base = declarative_base()

def generate_uuid():
    return str(uuid4())

def get_storage_config():
    config = {
        'update_existing_documents': True,
        'host': os.environ['elastic_search_host'],
        'port': os.environ['elastic_search_port']
    }

    return config

class DataCorpus(Base):
    __tablename__ = 'data_corpus'

    id = Column(Integer, primary_key=True)
    # Name of the data corpus
    name = Column(String, nullable=False)
    
    # UID of the DPR embedding storage index
    dpr_uuid = Column(String, nullable=False, default=generate_uuid)

    # UID of the ElasticSearch embedding storage index
    elastic_search_uuid = Column(String, nullable=False, default=generate_uuid)

    def get_storage(self, retriever):
        if retriever == 'dpr':
            return ElasticsearchDocumentStore(**get_storage_config(), index=self.dpr_uuid)
        elif retriever == 'elastic_search':
            return ElasticsearchDocumentStore(**get_storage_config(), index=self.elastic_search_uuid)

    def get_retriever(self, retriever):
        if retriever == 'dpr':
            return DensePassageRetriever(self.get_storage('dpr'))
        elif retriever == 'elastic_saerch':
            return ElasticsearchRetriever(self.get_storage('elastic_search'))

    def add_document(self, document_name, document_text):
        dpr_storage = self.get_storage('dpr')  # ??
        elastic_search_storage = self.get_storage('elastic_search')

        document_repr = Document(content=document_text, id=document_name, content_type='text')

        dpr_storage.write_documents(documents=[document_repr], index=self.dpr_uuid)
        dpr_storage.update_embeddings(self.get_retriever('dpr'))
        elastic_search_storage.write_documents(documents=[document_repr], index=self.elastic_search_uuid)


class Dataset(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    # ID of the corresponding data corpus
    data_corpus_id = Column(Integer, ForeignKey('data_corpus.id'))
    data_corpus = relationship(DataCorpus)
    # Name of the dataset
    name = Column(String, nullable=False)

engine = create_engine(engine_path)

Base.metadata.create_all(engine)

BaseSession = sessionmaker(bind=engine)
