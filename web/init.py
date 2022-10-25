import streamlit as st

from api import upload_dataset, get_datasets
from model_selection.selected_models import SelectedModels, RetrieverType


def init():
    from api.repositories import session  # starting the DB connection

    if 'selected_models' not in st.session_state:
        # defaults
        st.session_state['selected_models'] = SelectedModels(
            "facebook/dpr-ctx_encoder-single-nq-base",
            "facebook/dpr-question_encoder-single-nq-base",
            RetrieverType.DPR,
            "distilbert-base-uncased-distilled-squad",
            "valhalla/t5-base-e2e-qg"
        )

    if 'init_uploaded_datasets' not in st.session_state:
        print('entered uploading datasets', 'init_uploaded_datasets' in st.session_state)
        st.session_state['init_uploaded_datasets'] = True
        datasets = get_datasets()
        datasets_names = set([dataset['name'] for dataset in datasets])

        # todo use SUPPORTED_DATASETS from DatasetDownloader
        # todo add try except so if something does not get downloaded we remove `init_uploaded_datasets` flag

        if 'natural-questions' not in datasets_names:
            upload_dataset('natural-questions')
        if 'squad' not in datasets_names:
            upload_dataset('squad')
