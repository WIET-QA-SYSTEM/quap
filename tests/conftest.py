import contextlib
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker, Session
from sqlalchemy.engine import Engine

from helpers import rmtree

from quap.data.orm import metadata, start_mappers
from quap.utils.preprocessing.format_unifier import FormatUnifier


@pytest.fixture
def engine() -> Engine:
    engine = create_engine(os.environ['POSTGRESQL_CONNECTION_STRING'])
    metadata.create_all(engine)
    yield engine

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


@pytest.fixture
def session(engine: Engine) -> Session:
    start_mappers()
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    clear_mappers()

    # flushing all uncommitted changes
    # session.commit()
    #
    # for table in reversed(metadata.sorted_tables):
    #     session.execute(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE;")
    #
    # session.commit()


@pytest.fixture
def format_unifier() -> FormatUnifier:
    return FormatUnifier()


@pytest.fixture(scope='session', autouse=True)
def clear_cache():
    yield
    rmtree('.cache')
