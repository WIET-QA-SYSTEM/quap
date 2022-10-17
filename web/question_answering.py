import logging

import streamlit as st

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
        question_input = st.text_input("Input the question to the model")

        question_submit = st.form_submit_button("Ask!")

        if question_submit:
            selected_models: SelectedModels = st.session_state['selected_models']
            logging.info("Predicting on corpus: " +
                         str(corpus_to_id[corpus_selection]))
            with st.spinner(f"Answering: {question_input}"):
                runtime_error = False
                try:
                    answers = predict_qa(
                        corpus_id=corpus_to_id[corpus_selection],
                        questions=[question_input],
                        retriever_type=selected_models.retriever_type.value,
                        dpr_question_encoder=selected_models.dpr_query,
                        dpr_context_encoder=selected_models.dpr_context,
                        reader_encoder=selected_models.reader,
                        use_gpu=st.session_state['device'] == 'gpu'
                    )
                except RuntimeError as ex:
                    st.error('CUDA out of memory exception. Use a toggle button to use CPU instead of GPU')
                    runtime_error = True

            if not runtime_error:
                st.write("### Model's answer:")
                for query, answers_list in zip(answers['queries'], answers['answers']):
                    for answer_obj in answers_list[:1]:
                        st.write(str(answer_obj.answer))
