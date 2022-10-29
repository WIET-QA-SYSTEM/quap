import streamlit as st
from streamlit_option_menu import option_menu

from model_selection.selected_models import RetrieverType, SelectedModels
from api.ml import is_cuda_available


class Sidebar:
    @classmethod
    def make_sidebar(cls, selected_models: SelectedModels):
        obj = cls()

        obj.menu = Sidebar._build_sidebar_menu()
        
        Sidebar._build_model_info(selected_models)

        return obj

    def get_selection(self):
        return self.menu

    @staticmethod
    def _build_model_info(selected_models):
        # todo can try https://github.com/0phoff/st-btn-select for cpu/gpu switching
        with st.sidebar:
            st.markdown("***")

            col1, col2 = st.columns([5, 2])

            with col1:
                st.markdown("## Selected models")
            with col2:
                cuda_available = is_cuda_available()
                default_device = 'gpu' if cuda_available else 'cpu'
                device = st.select_slider('Device',
                                          options=['cpu', 'gpu'],
                                          value=default_device,
                                          disabled=not cuda_available,
                                          label_visibility='collapsed')

                st.session_state['device'] = device

            st.write("#### DPR context embedding")
            st.code(selected_models.dpr_context)
            st.write("#### DPR query embedding")
            st.code(selected_models.dpr_query)
            st.write("#### Retriever type")
            if selected_models.retriever_type == RetrieverType.DPR:
                st.code("Dense Passage Retrieval")
            else:
                st.code("Elasticsearch")
            st.write("#### Reader model")
            st.code(selected_models.reader)
            st.write("#### Question generation model")           
            st.code(selected_models.question_generator)


    @staticmethod
    def _build_sidebar_menu():
        with st.sidebar:
            menus = option_menu(None, [
                "Question answering",
                "Question generation",
                "Model evaluation",
                "Model selection",
                "Data corpuses"
            ], icons = [
                'question-circle',
                'brush',
                'bar-chart-line',
                'wrench',
                'folder'
            ], menu_icon='house',
            default_index=0,
            orientation='vertical')

        return menus
