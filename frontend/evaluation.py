import logging

import streamlit as st

from api import get_datasets


def show_evaluation(eval):

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
    
    with st.expander("Evaluation results", expanded=True):
        for component in eval.keys():
            
            st.markdown("#### {}".format(component))
            
            for metric, value in eval['Retriever'].items():
                if metric not in eval_names:
                    logging.warning(
                        "Metric name {} not found in translations and will not be displayed (interface.py)".format(metric)
                    )
                    continue
                metric_name = eval_names[metric]
                
                metric_value = "{:.2f}%".format(value*100)
                
                st.markdown("###### {} - {}".format(metric_name, metric_value))
                st.progress(value)


def draw_evaluation():

    st.write("## Model evaluation")

    datasets = get_datasets()

    name_to_id = {
        dataset['name']: dataset['id']
        for dataset in datasets
    }

    with st.form("evaluation-form"):    
        st.selectbox("Select dataset for evaluation", name_to_id.keys())

        submitted = st.form_submit_button("Evaluate")

        if submitted:
            with st.spinner("Selected pipeline is being evaluated"):

                from time import sleep
                sleep(3)

            show_evaluation({'Retriever': {'recall_multi_hit': 0.8, 'precision': 0.3}})
            


