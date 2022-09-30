import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker, Session
from sqlalchemy.engine import Engine

from quap.data.orm import metadata, start_mappers


@pytest.fixture
def engine() -> Engine:
    engine = create_engine(os.environ['POSTGRESQL_CONNECTION_STRING'])
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine: Engine) -> Session:
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()

