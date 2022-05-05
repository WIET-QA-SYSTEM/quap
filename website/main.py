from email.policy import default
import streamlit as st
from settings import SETTINGS
from mockups import get_models_list, get_model_datasets

def main() -> None:

    # Initialize session states
    default_session_values = {
        'model_selected': False,
        'custom_dataset_selected': False,
        'existing_dataset_selected': False,
        'compute_metrics_selected': False,
        'insert_query_selected': False,
        'files_uploaded': False
    }

    # Each time a value is changed, everything that depends on it
    # is set to it's default value.
    session_dependency = {
        'model_selected': ['custom_dataset_selected', 'existing_dataset_selected'],
        'existing_dataset_selected': ['compute_metrics_selected', 'insert_query_selected'],
        'custom_dataset_selected' : ['files_uploaded']
    }

    def reset_dependencies(dependency):
        nonlocal session_dependency, default_session_values
        if dependency not in session_dependency:
            return
        for following_dependency in session_dependency[dependency]:
            st.session_state[following_dependency] = default_session_values.get(
                following_dependency, False
            )
            reset_dependencies(following_dependency)
            

    for key, value in default_session_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
            reset_dependencies(key)

    st.write('Welcome to ' + SETTINGS["app_codename"])

    progress_bar = st.progress(0)

    st.write("## Select the model You would like to try out")

    selected_model = st.selectbox(
        label="Model selection",
        options=get_models_list(),
        on_change=lambda: reset_dependencies("model_selected")
    )

    model_selection_button = st.button("Select this model")

    if model_selection_button:
        st.session_state['model_selected'] = True
        reset_dependencies('model_selected')


    if st.session_state['model_selected']:
        progress_bar.progress(20)
        st.write("Fetching the datasets for you...")

        available_datasets = get_model_datasets(selected_model)
        
        st.write(f"{len(available_datasets)} datasets are available for evaluation of this model")

        st.write("### Would You like to evaluate one of the predefined datasets?")
        
        existing_dataset_button = st.button('Evaluate on an existing dataset')
        custom_dataset_button = st.button('Custom dataset')

        if existing_dataset_button:
            st.session_state['existing_dataset_selected'] = True
            st.session_state['custom_dataset_selected'] = False
            reset_dependencies('existing_dataset_selected')
        
        if custom_dataset_button:
            st.session_state['custom_dataset_selected'] = True
            st.session_state['existing_dataset_selected'] = False
            reset_dependencies('custom_dataset_selected')

        if st.session_state['custom_dataset_selected'] or \
            st.session_state['existing_dataset_selected']:

            progress_bar.progress(40)

        if st.session_state['existing_dataset_selected']:
            st.write("### Select the dataset and action to perform!")
            selected_dataset = st.selectbox(
                label="Dataset selection",
                options=available_datasets,
                on_change=lambda: reset_dependencies('existing_dataset_selected')
            )

            compute_metrics_button = st.button('Compute validation metrics')
            enter_query_button = st.button('Enter a query')

            if compute_metrics_button:
                st.session_state['compute_metrics_selected'] = True
                st.session_state['insert_query_selected'] = False
                reset_dependencies('insert_query_selected')
            if enter_query_button:
                st.session_state['insert_query_selected'] = True
                st.session_state['compute_metrics_selected'] = False
                reset_dependencies('compute_metrics_selected')

            if st.session_state['compute_metrics_selected']:
                st.write("### Model evaluation result")
                progress_bar.progress(100)
                st.write("<Metrics result for the selected model & dataset>")
                st.balloons()
            elif st.session_state['insert_query_selected']:
                st.write("### Ask the model a question!")
                progress_bar.progress(80)
                question = st.text_input("Your question")
                if st.button("Ask the model!") or question:
                    progress_bar.progress(100)
                    st.write("<Model's answer>")
                    st.balloons()

        elif st.session_state['custom_dataset_selected']:
            progress_bar.progress(60)
            st.write("### Let the model learn!")
            files = st.file_uploader(
                    "Upload You database (list of .PDF or .DOC files)",
                    accept_multiple_files=True,
                    on_change=lambda: reset_dependencies('custom_dataset_selected')
                )

            if files is not None and len(files):
                st.session_state['files_uploaded'] = True
            else:
                st.session_state['files_uploaded'] = False

            if st.session_state['files_uploaded']:
                progress_bar.progress(80)
                st.write("### Ask the model a question!")
                question = st.text_input("Your question")
                if st.button("Ask the model!") or question:
                    progress_bar.progress(100)
                    st.write("<Model's answer>")
                    st.balloons()

                




if __name__ == "__main__":
    main()