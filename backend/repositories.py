from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from quap.data.orm import metadata, start_mappers
from quap.data.repository import DataCorpusRepository, DocumentRepository, DatasetRepository

from settings import settings


engine = create_engine(settings.DATABASE_URL)
metadata.create_all(engine)

start_mappers()

session = sessionmaker(bind=engine, expire_on_commit=False)()

corpus_repository = DataCorpusRepository(session)
dataset_repository = DatasetRepository(session)
document_repository = DocumentRepository(session)
