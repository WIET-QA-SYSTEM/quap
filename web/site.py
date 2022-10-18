import streamlit as st

from sidebar import Sidebar
from evaluation import draw_evaluation
from model_selection.model_selection import draw_model_selection
from model_selection.selected_models import SelectedModels, RetrieverType
from data_corpuses import draw_data_corpuses
from question_answering import draw_question_answering
from question_generation import draw_question_generation


if 'selected_models' not in st.session_state:
    st.session_state['selected_models'] = SelectedModels(  # defaults
        "facebook/dpr-ctx_encoder-single-nq-base",
        "facebook/dpr-question_encoder-single-nq-base",
        RetrieverType.DPR,
        "distilbert-base-uncased-distilled-squad",
        "valhalla/t5-base-e2e-qg"
    )

selected_models: SelectedModels = st.session_state['selected_models']

sidebar = Sidebar.make_sidebar(selected_models)

selection = sidebar.get_selection()

if selection == "Question answering":
    draw_question_answering()
elif selection == "Question generation":
    draw_question_generation()
elif selection == "Model evaluation":
    draw_evaluation()
elif selection == 'Model selection':
    draw_model_selection(selected_models)
elif selection == "Data corpuses":
    draw_data_corpuses()
