from interface import get_answer_uploaded, get_answer_prefetched, get_evaluation_function
import streamlit as st
import os
from mockups import get_dataset_list, get_models_list

DATASETS_PATH = 'uploaded_datasets'

with st.sidebar:
    st.markdown("Evaluation mode")
    evaluation_selectbox = st.selectbox(
        "",
        ('Prefetched dataset', 'Custom dataset')
    )
    
if evaluation_selectbox == 'Prefetched dataset':
    st.write("Prefetched dataset evaluation")
elif evaluation_selectbox == 'Custom dataset':
    st.write("Custom dataset evaluation")
    
model_selected = st.selectbox(
    "Select model",
    get_models_list()
)

if 'show_evaluation_result' not in st.session_state:
    st.session_state['show_evaluation_result'] = lambda: None

if 'selected_uploaded_dataset' not in st.session_state:
    st.session_state['selected_uploaded_dataset'] = None

if evaluation_selectbox == 'Prefetched dataset':
    dataset = st.selectbox(
        "Select dataset",
        get_dataset_list()
    )
    
    dataset_selected = st.button("Evaluate")
    
    if dataset_selected:
        with st.spinner("We are prepairing Your statistics..."):
            # Generate evaluation
            show_evaluation_result = get_evaluation_function(model_selected, dataset)
        st.success("Your evaluation is ready")
        
        show_evaluation_result()    

    
    st.markdown("""---""")
    question_input = st.text_input("Or enter Your question")
        
    asked_for_answer = st.button("Answer me!")
        
    if asked_for_answer:
        if len(question_input.strip()) == 0:
            st.warning("Question should not be empty")
        else:
            answer_data  = get_answer_prefetched(model_selected, dataset, question_input)
            answer = answer_data.answer
            context = answer_data.context
            st.write("This is the result")
            st.write(answer)
            with st.expander("Answer context"):
                st.write(context)
    
    
elif evaluation_selectbox == 'Custom dataset':    
    files = st.file_uploader(
        "Upload You database (list of .PDF or .DOC files)",
        accept_multiple_files=True
    )
    
    dataset_name = st.text_input("Dataset name")
    
    dataset_uploaded = st.button("Upload")
    
    if dataset_uploaded and len(files) == 0:
        st.warning("The dataset cannot be empty")
    elif dataset_uploaded and len(dataset_name.strip()) == 0:
        st.warning("You need to specify the dataset name")
    elif dataset_uploaded:
        if not os.path.exists(DATASETS_PATH):
            os.makedirs(DATASETS_PATH)
            
        dataset_path = os.path.join(DATASETS_PATH, dataset_name)
        
        st.session_state.selected_uploaded_dataset = dataset_name
            
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
            
        for file in files:
            name = file.name
            bytes = file.getvalue()
            
            with open(os.path.join(dataset_path, name), 'wb') as f:
                f.write(bytes)
                
    if st.session_state.selected_uploaded_dataset is not None:
        st.write("Using dataset ", st.session_state.selected_uploaded_dataset)
        
        question_input = st.text_input("Enter Your question")
        
        asked_for_answer = st.button("Answer me!")
        
        if asked_for_answer:
            if len(question_input.strip()) == 0:
                st.warning("Question should not be empty")
            else:
                with st.spinner("Searching for an answer..."):    
                    answer_data = get_answer_uploaded(
                        model_selected, st.session_state.selected_uploaded_dataset, DATASETS_PATH,
                        question_input)
                answer = answer_data.answer
                context = answer_data.context
                st.write("Answer:")
                st.write(answer)
                with st.expander("Answer context"):
                    st.write(context)
        