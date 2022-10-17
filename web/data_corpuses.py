import streamlit as st
from api import get_data_corpora, upload


def draw_data_corpuses():

    st.markdown("## Data corpuses")

    data_corpuses = get_data_corpora()

    name_to_files = {
        corpus['name']: corpus['document_names']
        for corpus in data_corpuses
    }

    name_to_id = {
        corpus['name']: corpus['id']
        for corpus in data_corpuses
    }

    with st.expander("Add a new data corpus"):
        with st.form("corpus-adder-form", clear_on_submit=True):
            corpus_name = st.text_input("New data corpus name")

            submit = st.form_submit_button("Add corpus")

            if submit:
                try:
                    corpus_name = str(corpus_name).strip()
                    if corpus_name in list(name_to_id.keys()):
                        st.warning("Corpus with this name already exists!")
                    else:
                        upload([], [], None, corpus_name)
                        st.info("Adding corpus: " + corpus_name)
                        st.experimental_rerun()
                except Exception as e:
                    # TODO do something with the exception?
                    st.warning("Corpus already exists " + str(e))

    with st.expander("Modify a data corpus"):
        corpus_selection = st.selectbox(
            "Select a data corpus", list(name_to_id.keys()))

        if corpus_selection is not None:

            if corpus_selection in name_to_files and len(name_to_files[corpus_selection]):
                st.markdown("***")
                st.write("Files in the data corpus: ")

                for file in name_to_files[corpus_selection]:
                    col1, col2, = st.columns(2)

                    with col1:
                        st.write(file)

                    with col2:
                        del_btn = st.button(
                            "Delete", key=f"delete_{file}_{corpus_selection}")

                    if del_btn:
                        # TODO file removal
                        pass

            st.markdown("***")
            st.write("Upload new files to the data corpus")

            with st.form("upload_corpus_files"):
                uploader = st.file_uploader("Select files to upload", [
                                            'pdf', 'txt', 'pptx'], accept_multiple_files=True)

                upload_btn = st.form_submit_button("Upload")

                if upload_btn:
                    print("uploading files...")

                    names_list = []
                    bytes_list = []

                    for uploaded_file in uploader:
                        bytes_data = uploaded_file.read()
                        names_list.append(uploaded_file.name)
                        bytes_list.append(bytes_data)

                    upload(bytes_list, names_list,
                           name_to_id[str(corpus_selection).strip()])
                        
                    st.experimental_rerun()

    with st.expander("Remove a data corpus"):
        corpus_selection = st.selectbox(
            "Select a data corpus for removal", name_to_id.keys())

        if corpus_selection != None:
            remove_btn = st.button("Remove")

            if remove_btn:
                st.warning("Corpus has been removed: " + str(corpus_selection))
                print("Removing corpus...")
