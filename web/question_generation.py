import streamlit as st
import logging

from api import get_data_corpora, predict_qg
from markdown import markdown
from haystack import Answer
from annotated_text import annotation
from quap.ml.pipelines.qg_pipeline import QGResult
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
            logging.info(f"{n_questions} questions for each document")
            print(selected_models)

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
                    st.write("### Questions")

                with col2:
                    st.write("### Answers")

                for file_name, qg_results in questions_and_answers.items():
                    with st.expander(file_name):
                        for result in qg_results:
                            result: QGResult
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(result.question)

                            with col2:
                                for answer_obj in result.answers:
                                    answer_obj: Answer
                                    answer = answer_obj.answer
                                    context = answer_obj.context

                                    start_idx = answer_obj.offsets_in_context[0].start
                                    end_idx = answer_obj.offsets_in_context[0].end

                                    st.write(
                                        markdown(
                                            context[:start_idx] + str(annotation(answer, "ANSWER", "#308896")) + context[end_idx:]),
                                        unsafe_allow_html=True,
                                    )
                                    st.markdown(f"**Relevance:** {answer_obj.score:.4f}")
