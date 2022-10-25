import streamlit as st
from iso639 import languages

from api import get_model_languages
from model_selection.selected_models import SelectedModels


def language_incompatibility_warning(corpus_language: str, selected_models: SelectedModels) -> None:
    corpus_language = languages.get(alpha2=corpus_language).name.lower()
    model_languages = get_model_languages()
    if selected_models.retriever_type.value == 'dpr':
        query_encoder_language = model_languages['retriever']['query']
        passage_encoder_language = model_languages['retriever']['context']

        if corpus_language != query_encoder_language:
            st.warning(f'Query encoder\'s language ({query_encoder_language}) '
                       f'is not the same as corpus\' ({corpus_language})')
        if corpus_language != passage_encoder_language:
            st.warning(f'Passage encoder\'s language ({passage_encoder_language}) '
                       f'is not the same as corpus\' ({corpus_language})')

    if corpus_language != model_languages['reader']['encoder']:
        st.warning(f'Reader encoder\'s language ({model_languages["reader"]["encoder"]}) '
                   f'is not the same as corpus\' ({corpus_language})')
