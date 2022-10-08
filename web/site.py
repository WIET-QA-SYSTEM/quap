import streamlit as st
from sidebar import Sidebar
from model_selection.model_selection import draw_model_selection
from model_selection.selected_models import SelectedModels

selected_models = st.session_state.get('selected_models', SelectedModels( #defaults
    "facebook/dpr-ctx_encoder-single-nq-base",
    "facebook/dpr-question_encoder-single-nq-base",
    "elasticsearch",
    "distilbert-base-uncased-distilled-squad",
    "valhalla/t5-base-e2e-qg"
))

sidebar = Sidebar.make_sidebar(selected_models)

draw_model_selection(selected_models)