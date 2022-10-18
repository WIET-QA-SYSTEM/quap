import streamlit as st
import logging

from api import get_data_corpora, predict_qg
from web.model_selection.selected_models import SelectedModels


def draw_question_generation():
    st.markdown("## Question generation")

    corpuses = ["Corpus 1", "Corpus 2", "Corpus 3"]
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

    st.session_state['last_selected_corpus'] = corpus_selection

    with st.form("generation-form"):
        n_questions = st.number_input(
            "Number of questions to generate per document", step=1, min_value=1, value=5, format='%d')

        generate_submit = st.form_submit_button(
            "Generate questions & answers!")

        if generate_submit:
            selected_models: SelectedModels = st.session_state['selected_models']
            logging.info("Generating on corpus: " +
                         str(corpus_to_id[corpus_selection]))

            with st.spinner(f"Generating questions & answers"):
                runtime_error = False
                try:
                    questions_and_answers = predict_qg(
                        corpus_id=corpus_to_id[corpus_selection],
                        reader_encoder=selected_models.reader,
                        generator=selected_models.question_generator,
                        use_gpu=st.session_state.get('device', 'cpu') == 'gpu',
                        pairs_per_document=int(n_questions)
                    )
                except RuntimeError as ex:
                    st.error('CUDA out of memory exception. Use a toggle button to use CPU instead of GPU')
                    runtime_error = True

            if not runtime_error:
                st.write("### Generated questons and answers")                

                generator_container = st.container()
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

                col1, col2 = st.columns(2)
                with col1:
                    st.write("#### Question")
                with col2:
                    st.write("#### Answer")

                for _ in range(10):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"Question {_}")
                    with col2:
                        st.write(f"Answer {_}")
