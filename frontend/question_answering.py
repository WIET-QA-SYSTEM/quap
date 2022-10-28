import logging

import streamlit as st
from annotated_text import annotation
from iso639 import languages
from markdown import markdown

from api import (get_data_corpora,
                 get_model_languages,
                 predict_qa)
from model_selection.selected_models import SelectedModels

logger = logging.getLogger(__name__)


def draw_question_answering():
    st.markdown("## Question answering")

    corpus_objects = get_data_corpora()

    corpuses = [corpus['name'] for corpus in corpus_objects]
    corpus_to_id = {
        corpus['name']: corpus
        for corpus in corpus_objects
    }

    last_selected_corpus = st.session_state.get("last_selected_corpus")

    if last_selected_corpus in corpuses:
        default_corpus_index = corpuses.index(last_selected_corpus)
    else:
        default_corpus_index = 0

    corpus_selection = st.selectbox(
        "Select data corpus", corpuses, index=default_corpus_index)

    st.session_state['last_selected_corpus'] = str(corpus_selection).strip()

    with st.form("question-form"):
        st.session_state['questions_count'] = st.session_state.get('questions_count', 1)

        st.write("### Input the questions to the model")

        questions_container = st.container()

        st.markdown(
            """
            <style>
                div[data-testid="column"]:nth-of-type(2)
                {
                    text-align: end;
                }
            </style>
            """, unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            question_submit = st.form_submit_button("Ask!")
        with col2:
            add_question = st.form_submit_button('Add another question')
            if add_question:
                st.session_state['questions_count'] += 1
        with col3:
            remove_question = st.form_submit_button('Remove last question')
            if remove_question:
                st.session_state['questions_count'] = max(st.session_state['questions_count'] - 1, 1)

        with questions_container:
            questions = []
            for i in range(st.session_state['questions_count']):
                question_session_state_key = f'question_{i}'
                question_input = st.text_input("Input the question to the model",
                                               value=st.session_state.get(question_session_state_key, ""),
                                               key=question_session_state_key,
                                               label_visibility='collapsed')

                if not remove_question:
                    questions.append(question_input)

        if question_submit:
            selected_models: SelectedModels = st.session_state['selected_models']
            logging.info("Predicting on corpus: " +
                         str(corpus_to_id[corpus_selection]['id']))
            with st.spinner(f"Answering"):
                runtime_error = False
                try:
                    corpus_language = languages.get(alpha2=corpus_to_id[corpus_selection]['language']).name.lower()
                    model_languages = get_model_languages()
                    if selected_models.retriever_type.value == 'dpr':
                        query_encoder_language = model_languages['retriever']['query']
                        passage_encoder_language = model_languages['retriever']['passage']

                        if corpus_language != query_encoder_language:
                            st.warning(f'Query encoder\'s language ({query_encoder_language}) '
                                       f'is not the same as corpus\' ({corpus_language})')
                        if corpus_language != passage_encoder_language:
                            st.warning(f'Passage encoder\'s language ({passage_encoder_language}) '
                                       f'is not the same as corpus\' ({corpus_language})')

                    if corpus_language != model_languages['reader']['encoder']:
                        st.warning(f'Reader encoder\'s language ({model_languages["reader"]["encoder"]}) '
                                   f'is not the same as corpus\' ({corpus_language})')

                    answers = predict_qa(
                        corpus_id=corpus_to_id[corpus_selection]['id'],
                        questions=questions,
                        retriever_type=selected_models.retriever_type.value,
                        dpr_question_encoder=selected_models.dpr_query,
                        dpr_context_encoder=selected_models.dpr_context,
                        reader_encoder=selected_models.reader,
                        device=st.session_state.get('device', 'cpu')
                    )
                except RuntimeError as ex:
                    logger.error(str(ex))
                    st.error(str(ex))
                    st.info('If there are problems with CUDA - you can try to use CPU instead of GPU (toggle button)')
                    runtime_error = True

            if not runtime_error:
                st.write("### Answers:")
                for query, records in answers.items():

                    with st.expander(query):

                        for i, record in enumerate(records[:3]):
                            if i > 0:
                                st.markdown('---')

                            answer = record['answer']
                            score = record['answer_score']
                            document_name = record['document_name']
                            context = record['context']
                            start_idx = record['context_offset']
                            end_idx = start_idx + len(answer)

                            st.write(
                                markdown(
                                    context[:start_idx]
                                    + str(annotation(answer, "ANSWER", "#308896"))
                                    + context[end_idx:]
                                ),
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**Relevance:** {score:.4f} -  **Source:** {document_name}")

                        if not records:
                            st.info('Model is not certain what the answer to your question is. Try to reformulate it!')

