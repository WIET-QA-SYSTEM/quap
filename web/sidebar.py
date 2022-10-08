import streamlit as st
from streamlit_option_menu import option_menu
from model_selection.selected_models import RetrieverType, SelectedModels

class Sidebar:
    @classmethod
    def make_sidebar(cls, selected_models: SelectedModels):
        cls.menu = Sidebar._build_sidebar_menu()
        
        Sidebar._build_model_info(selected_models)

        return cls

    @staticmethod
    def _build_model_info(selected_models):
        with st.sidebar:
            st.markdown("***")
            st.markdown("### Selected models")
            st.write("#### DPR context embedding")
            st.write(selected_models.dpr_context)
            st.write("#### DPR query embedding")
            st.write(selected_models.dpr_query)
            st.write("#### Retriever type")
            if selected_models.retriever_type == RetrieverType.DPR:
                st.write("Dense passage retrieval")
            else:
                st.write("Elastic search")
            st.write("#### Reader model")
            st.write(selected_models.reader)
            st.write("#### Question generation model")           
            st.write(selected_models.question_generator)


    @staticmethod
    def _build_sidebar_menu():
        with st.sidebar:
            menus = option_menu(None, [
                "Question answering",
                "Question generation",
                "Model evaluation",
                "Model selection"
            ], icons = [
                'question-circle',
                'brush',
                'bar-chart-line',
                'wrench'
            ], menu_icon='house',
            default_index=0,
            orientation='vertical')