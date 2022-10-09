import streamlit as st

def draw_data_corpuses():

    st.markdown("## Data corpuses")

    data_corpuses = ['Corpus 1', 'Corpus 2', 'Corpus 3']

    corpus_files = {
        'Corpus 1': {'File 1', 'File 2'},
        'Corpus 2': {'File 2', 'File 3'},
        'Corpus 3': {}
    }

    with st.expander("Add a new data corpus"):
        with st.form("corpus-adder-form"):
            corpus_name = st.text_input("New data corpus name")

            submit = st.form_submit_button("Add corpus")

            if submit:
                st.info("Adding corpus: " + corpus_name)

        
     
    with st.expander("Modify a data corpus"):
        corpus_selection = st.selectbox("Select a data corpus", data_corpuses)

        if corpus_files[corpus_selection] and len(corpus_files[corpus_selection]):
            st.markdown("***")
            st.write("Files in the data corpus: ")

            for file in corpus_files[corpus_selection]:
                col1, col2, = st.columns(2)

                with col1:
                    st.write(file)

                with col2:
                    del_btn = st.button("Delete", key=f"delete_{file}_{corpus_selection}")


        st.markdown("***")
        st.write("Upload new files to the data corpus")

        with st.form("upload_corpus_files"):
            uploader = st.file_uploader("Select files to upload", ['pdf', 'txt', 'pptx'])

            upload_btn = st.form_submit_button("Upload")

            if upload_btn:
                print("uploading files...")


    with st.expander("Remove a data corpus"):
        corpus_selection = st.selectbox("Select a data corpus for removal", data_corpuses)

        remove_btn = st.button("Remove")

        if remove_btn:
            st.warning("Corpus has been removed: " + str(corpus_selection))
            print("Removing corpus...")