from typing import Optional
from copy import deepcopy

import streamlit as st
from huggingface_listing.model_types import ModelType
from huggingface_listing.model_listing import get_model_list

from model_selection.selected_models import SelectedModels


def _text_with_button_modal(text: str, button_content: str = "Change", on_click=lambda: None, key: Optional[str] = None):
    col1, col2 = st.columns(2)
    btn_key = key or text+"_"+button_content
    with col1:
        st.write(text)
    with col2:
        btn = st.button(label=button_content, key=btn_key)
    if btn:
        st.session_state["btn_active_"+btn_key] = True
        on_click()
    elif st.session_state.get("btn_active_"+btn_key, False):
        del st.session_state["btn_active_"+btn_key]
        on_click()

def _change_model(selected_models, model_type_name, model_type):
    with st.spinner("Fetching available models"):   
        models = get_model_list(model_type)

    with st.form("model-selection-form"):
        selectbox = st.selectbox("Select new model: ", options=models)

        col1, col2 = st.columns(2)
        with col1:
            cancelled = st.form_submit_button("Cancel")
        with col2:
            submitted = st.form_submit_button("Change model")

        if submitted:            
            st.session_state['selected_models'] = deepcopy(selected_models)
            setattr(st.session_state['selected_models'], model_type_name, selectbox)

            st.experimental_rerun()



def draw_model_selection(selected_models: SelectedModels):
    st.markdown("## Model selection")
    st.markdown("***")

    st.write("### DPR context embedding")
    _text_with_button_modal(
        f"Currently selected model: **{selected_models.dpr_context}**",
        on_click=lambda: _change_model(selected_models, "dpr_context", ModelType.DPR),
        key='btn_dpr_context_encoder'
    )
    st.markdown("***")

    st.write("### DPR query embedding")
    _text_with_button_modal(
        f"Currently selected model: **{selected_models.dpr_query}**",
        on_click=lambda: _change_model(selected_models, "dpr_query", ModelType.DPR),
        key='btn_dpr_query_encoder'
    )
    st.markdown("***")

    st.write("### Retriever type")
    st.selectbox("Retriever type", [
                 "Elastic search", "Dense passage retrieval"], label_visibility='hidden')
    st.markdown("***")

    st.write("### Reader model")
    _text_with_button_modal(
        f"Currently selected reader: **{selected_models.reader}**",
        on_click=lambda: _change_model(selected_models, "reader", ModelType.READER),
        key='btn_reader_encoder'
    )
    st.markdown("***")

    st.write("### Question generator")
    _text_with_button_modal(
        f"Currently selected question generator: **{selected_models.question_generator}**",
        on_click=lambda: _change_model(selected_models, "question_generator", ModelType.QUESTION_GENERATOR),
        key='btn_question_generator_encoder'
    )
