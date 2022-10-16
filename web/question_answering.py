import streamlit as st

def draw_question_answering():
    st.markdown("## Question answering")
    
    corpuses = ["Corpus 1", "Corpus 2", "Corpus 3"]

    last_selected_corpus = st.session_state.get("last_selected_corpus")

    if last_selected_corpus in corpuses:
        default_corpus_index = corpuses.index(last_selected_corpus)
    else:
        default_corpus_index = 0

    corpus_selection = st.selectbox("Select data corpus", corpuses, index=default_corpus_index)

    st.session_state['last_selected_corpus'] = corpus_selection

    with st.form("question-form"):
        question_input = st.text_input("Input the question to the model")

        question_submit = st.form_submit_button("Ask!")

        if question_submit:
            with st.spinner(f"Answering: {question_input}"):
                from time import sleep
                sleep(1)
            st.write("### Model's answer:")
            st.write("Answer")