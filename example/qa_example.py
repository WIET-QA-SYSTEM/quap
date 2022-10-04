import os
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker, Session
from sqlalchemy.engine import Engine

from dotenv import load_dotenv

from haystack.nodes import FARMReader
load_dotenv('../.env')


from quap.data.repository import DataCorpusRepository
from quap.data.models import DataCorpus
from quap.data.orm import start_mappers
from quap.data.document_store import ELASTIC_SEARCH_STORAGE
from quap.ml.indexed_retrievers import IndexedBM25, IndexedDPR
from quap.ml.qa.qa_pipeline import QAPipeline
from quap.data.orm import metadata

# Create a data corpus
engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
metadata.create_all(engine)
session = sessionmaker(bind=engine, expire_on_commit=False)()

start_mappers()

corpus_repository = DataCorpusRepository(session)
corpus = DataCorpus(name='test')#name='example_corpus_' + str(uuid4())[:32])

corpus_repository.add(corpus)
corpus_repository.commit()

with open('epic_of_gilgamesh.txt', 'r') as book:
    book_content = book.read()

ELASTIC_SEARCH_STORAGE.add_document(session, corpus, 'Epic of Gilgamesh', book_content)

with open('kubica.txt', 'r') as book:
    book_content = book.read()

ELASTIC_SEARCH_STORAGE.add_document(session, corpus, 'Robert Kubica', book_content)

# Create a reader & retriever

retriever = IndexedDPR(document_store=ELASTIC_SEARCH_STORAGE)
reader = FARMReader('deepset/roberta-base-squad2', num_processes=0, top_k=1)

# Assemble pipeline
pipeline = QAPipeline(ELASTIC_SEARCH_STORAGE, retriever, reader)

# Run the pipeline and return the result
results = pipeline(corpus, ['Who is Kubica?'])
print(results[0]['answers'])