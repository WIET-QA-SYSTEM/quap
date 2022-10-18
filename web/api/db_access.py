from argparse import ArgumentError
import sqlalchemy
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError as AlchemyArgumentError

from quap.data.orm import metadata, start_mappers
from quap.data.repository import DataCorpusRepository, DocumentRepository, DatasetRepository

if not st.session_state.get('mappers_started', False):
    st.session_state['engine'] = create_engine(
        "postgresql://postgres:postgres@localhost:5432/postgres")
    metadata.create_all(st.session_state['engine'])

    try:
        start_mappers()
    except AlchemyArgumentError:
        # Silences errors in case session state was reset due to streamlit reload
        pass
    st.session_state['mappers_started'] = True
    st.session_state['session'] = sessionmaker(
        bind=st.session_state['engine'], expire_on_commit=False)()

session = st.session_state['session']

corpus_repository = DataCorpusRepository(session)
dataset_repository = DatasetRepository(session)
document_repository = DocumentRepository(session)
