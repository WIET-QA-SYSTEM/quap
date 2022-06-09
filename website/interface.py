import logging
import streamlit as st
import os

from qa.dataset import PrefetchedDataset, UploadedDataset
from qa.system import QASystem

def get_cached_qa_system(model_name: str) -> QASystem:
    if 'current_model_name' not in st.session_state or \
        st.session_state['current_model_name'] != model_name:
            
        st.session_state['current_model_name'] = model_name
        st.session_state['current_model_instance'] = QASystem(model_name)
        return st.session_state['current_model_instance']
    else:
        return st.session_state['current_model_instance']

            

def get_answer_uploaded(model_name: str, uploaded_dataset_name: str, datasets_path: str, question: str) -> str:
    logging.info(f"""Requested answer with model {model_name}
                 on uploaded dataset {uploaded_dataset_name}:
                 {question}""")        
    qa = get_cached_qa_system(model_name)
    dataset = UploadedDataset(os.path.join(datasets_path, uploaded_dataset_name))

    answers = qa.ask(dataset, question)

    return answers[0]

def get_answer_prefetched(model_name: str, prefetched_dataset_name: str, question: str) -> str:
    logging.info(f"""Requested answer with model {model_name}
                on prefetched dataset {prefetched_dataset_name}:
                {question}""")
    qa = get_cached_qa_system(model_name)
    dataset = PrefetchedDataset(prefetched_dataset_name)

    answers = qa.ask(dataset, question)

    return answers[0]

def get_evaluation_function(model_name: str, prefetched_dataset_name: str) -> callable:
    logging.info(f"""Requested evaluation with model {model_name}
            on prefetched dataset {prefetched_dataset_name}.""")
        
    # eval = {'Retriever': {'recall_multi_hit': 1.0, 'recall_single_hit': 1.0, 'precision': 0.30999999999999994, 'map': 0.8806947200176367, 'mrr': 0.925, 'ndcg': 0.9277974990491151}, 'Reader': {'f1': 0.8366666666666667, 'exact_match': 0.75}}
    qa = get_cached_qa_system(model_name)
    dataset = PrefetchedDataset(prefetched_dataset_name)
    
    eval = qa.evaluate_reader(dataset)
    
    eval_names = {
        'recall_multi_hit': 'Multi-hit recall',
        'recall_single_hit': 'Single-hit recall',
        'precision': 'Precision',
        'map': 'Mean average precision',
        'mrr': 'Mean reciprocal rank',
        'ndcg': 'Normalised discounted cumulative gain',
        
        'f1': 'F1 score',
        'exact_match': 'Exact matches'
    }
    
    def show_evaluation():
        
        with st.expander("Evaluation results", expanded=True):
            for component in eval.keys():
                
                st.markdown("#### {}".format(component))
                
                for metric, value in eval['Retriever'].items():
                    if metric not in eval_names:
                        logging.warning(
                            "Metric name {} not found in translations and will not be displayed (interface.py)".format(metric_name)
                        )
                        continue
                    metric_name = eval_names[metric]
                    
                    metric_value = "{:.2f}%".format(value*100)
                    
                    st.markdown("###### {} - {}".format(metric_name, metric_value))
                    st.progress(value)
                    
        
        
    return show_evaluation
    
    