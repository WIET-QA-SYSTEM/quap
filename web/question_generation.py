import streamlit as st

def draw_question_generation():
    st.markdown("## Question generation")
    
    corpuses = ["Corpus 1", "Corpus 2", "Corpus 3"]

    last_selected_corpus = st.session_state.get("last_selected_corpus")

    if last_selected_corpus in corpuses:
        default_corpus_index = corpuses.index(last_selected_corpus)
    else:
        default_corpus_index = 0

    corpus_selection = st.selectbox("Select data corpus", corpuses, index=default_corpus_index)

    st.session_state['last_selected_corpus'] = corpus_selection

    with st.form("generation-form"):
        question_submit = st.form_submit_button("Generate questions & answers!")

        if question_submit:
            with st.spinner(f"Generating questions & answers"):
                from time import sleep
                sleep(1)

            col1, col2 = st.columns(2)
            with col1: st.write("#### Question")
            with col2: st.write("#### Answer")

            for _ in range(10):
                col1, col2 = st.columns(2)

                with col1: st.write(f"Question {_}")
                with col2: st.write(f"Answer {_}")