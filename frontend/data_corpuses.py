import streamlit as st
from api import get_data_corpora, upload_corpus, create_data_corpus


def draw_data_corpuses():

    st.markdown("## Data corpuses")

    data_corpuses = get_data_corpora()

    name2documents = {
        corpus['name']: corpus['documents']
        for corpus in data_corpuses
    }

    name2corpus = {
        corpus['name']: corpus
        for corpus in data_corpuses
    }

    with st.expander("Add a new data corpus"):
        with st.form("corpus-adder-form", clear_on_submit=True):
            corpus_name = st.text_input("New data corpus name")

            submit = st.form_submit_button("Add corpus")

            if submit:
                corpus_name = str(corpus_name).strip()
                if corpus_name in name2corpus:
                    st.warning("Corpus with this name already exists!")
                else:
                    create_data_corpus(corpus_name)
                    st.info("Adding corpus: " + corpus_name)
                    st.experimental_rerun()

    with st.expander("Modify a data corpus"):
        corpus_selection = st.selectbox(
            "Select a data corpus", list(name2corpus.keys()))

        if corpus_selection is not None:

            if corpus_selection in name2documents and name2documents[corpus_selection]:
                st.markdown("***")
                st.write("Files in the data corpus: ")

                for document in name2documents[corpus_selection]:
                    col1, col2, = st.columns(2)

                    with col1:
                        st.write(document['name'])

                    with col2:
                        del_btn = st.button(
                            "Delete", key=f"delete_{document['name']}_{corpus_selection}")

                    if del_btn:
                        # TODO file removal
                        pass

            st.markdown("***")
            st.write("Upload new files to the data corpus")

            with st.form("upload_corpus_files"):
                uploader = st.file_uploader(
                    "Select files to upload",
                    accept_multiple_files=True
                )

                upload_btn = st.form_submit_button("Upload")

                if upload_btn:
                    print("uploading files...")

                    upload_corpus(name2corpus[str(corpus_selection)]['id'], list(uploader))
                    st.experimental_rerun()

    with st.expander("Remove a data corpus"):
        corpus_selection = st.selectbox(
            "Select a data corpus for removal", name2corpus.keys())

        if corpus_selection != None:
            remove_btn = st.button("Remove")

            if remove_btn:
                # todo add corpus removal
                st.warning("Corpus has been removed: " + str(corpus_selection))
                print("Removing corpus...")
