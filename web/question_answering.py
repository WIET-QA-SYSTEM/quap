from uuid import uuid4
import logging

import streamlit as st
from haystack import Answer
from annotated_text import annotation
from markdown import markdown

from api import get_data_corpora, load_qa_models, predict_qa
from model_selection.selected_models import RetrieverType, SelectedModels


def draw_question_answering():
    st.markdown("## Question answering")

    corpus_objects = get_data_corpora()

    corpuses = [corpus['name'] for corpus in corpus_objects]
    corpus_to_id = {
        corpus['name']: corpus['id']
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
                         str(corpus_to_id[corpus_selection]))
            with st.spinner(f"Answering"):
                answers = predict_qa(
                    corpus_id=corpus_to_id[corpus_selection],
                    questions=questions,
                    retriever_type=selected_models.retriever_type.value,
                    dpr_question_encoder=selected_models.dpr_query,
                    dpr_context_encoder=selected_models.dpr_context,
                    reader_encoder=selected_models.reader,
                    use_gpu=True
                )

            st.write("### Answers:")
            for query, answers_list in zip(answers['queries'], answers['answers']):

                with st.expander(query):

                    for i, answer_obj in enumerate(answers_list[:3]):
                        if i > 0:
                            st.markdown('---')

                        answer_obj: Answer = answer_obj

                        answer = answer_obj.answer
                        context = answer_obj.context

                        start_idx = answer_obj.offsets_in_context[0].start
                        end_idx = answer_obj.offsets_in_context[0].end

                        document_name = answer_obj.meta['document_name']

                        st.write(
                            markdown(
                                context[:start_idx] + str(annotation(answer, "ANSWER", "#308896")) + context[end_idx:]),
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Relevance:** {answer_obj.score:.4f} -  **Source:** {document_name}")

                    if not answers_list:
                        st.info('Model is not certain what the answer to your question is. Try to reformulate it!')
