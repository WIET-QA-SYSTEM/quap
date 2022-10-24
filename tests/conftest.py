import contextlib
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker, Session
from sqlalchemy.engine import Engine

from quap.data.orm import metadata, start_mappers
from quap.utils.preprocessing.format_unifier import FormatUnifier


@pytest.fixture
def postgresql_connection_string() -> str:
    host = os.environ['POSTGRESQL_HOST']
    port = os.environ['POSTGRESQL_PORT']
    db = os.environ['POSTGRESQL_DB']
    user = os.environ['POSTGRESQL_USER']
    password = os.environ['POSTGRESQL_PASSWORD']
    return f'postgresql://{user}:{password}@{host}:{port}/{db}'


@pytest.fixture
def engine(postgresql_connection_string: str) -> Engine:
    engine = create_engine(postgresql_connection_string)
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
