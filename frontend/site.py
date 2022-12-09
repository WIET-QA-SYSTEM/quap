import streamlit as st

from data_corpora import draw_data_corpora
from evaluation import draw_evaluation
from model_selection.model_selection import draw_model_selection
from model_selection.selected_models import SelectedModels
from question_answering import draw_question_answering
from question_generation import draw_question_generation
from sidebar import Sidebar
from init import init


init()

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
elif selection == "Data corpora":
    draw_data_corpora()
