import streamlit as st
from iso639 import languages

from api import get_model_languages
from model_selection.selected_models import SelectedModels


def language_incompatibility_warning(corpus_language: str, selected_models: SelectedModels) -> None:
    corpus_language = languages.get(alpha2=corpus_language).name.lower()
    model_languages = get_model_languages()
    if selected_models.retriever_type.value == 'dpr':
        query_encoder_language = model_languages['retriever']['query']
        passage_encoder_language = model_languages['retriever']['passage']

        if query_encoder_language is not None:
            query_encoder_language = languages.get(alpha2=query_encoder_language).name.lower()
        if passage_encoder_language is not None:
            passage_encoder_language = languages.get(alpha2=passage_encoder_language).name.lower()

        if corpus_language != query_encoder_language:
            st.warning(f'Query encoder\'s language ({query_encoder_language}) '
                       f'is not the same as corpus\' ({corpus_language})')
        if corpus_language != passage_encoder_language:
            st.warning(f'Passage encoder\'s language ({passage_encoder_language}) '
                       f'is not the same as corpus\' ({corpus_language})')

    reader_language = model_languages["reader"]["encoder"]
    if reader_language is not None:
        reader_language = languages.get(alpha2=reader_language).name.lower()

    if corpus_language != reader_language:
        st.warning(f'Reader encoder\'s language ({reader_language}) '
                   f'is not the same as corpus\' ({corpus_language})')
