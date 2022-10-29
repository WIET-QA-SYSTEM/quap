import logging

import streamlit as st

from api import get_datasets, evaluate
from api.utils import language_incompatibility_warning
from model_selection.selected_models import SelectedModels


logger = logging.getLogger('quap')


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

            for metric, value in eval[component].items():
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

    name_to_dataset = {
        dataset['name']: dataset
        for dataset in datasets
    }

    with st.form("evaluation-form"):    
        dataset_selection = st.selectbox("Select dataset for evaluation", name_to_dataset.keys())

        submitted = st.form_submit_button("Evaluate")

        if submitted:
            selected_models: SelectedModels = st.session_state['selected_models']
            with st.spinner("Selected pipeline is being evaluated"):
                runtime_error = False
                try:
                    corpus_language = name_to_dataset[dataset_selection]['corpus']['language']
                    language_incompatibility_warning(corpus_language, selected_models)

                    metrics = evaluate(
                        dataset_id=name_to_dataset[dataset_selection]['id'],
                        retriever_type=selected_models.retriever_type.value,
                        dpr_question_encoder=selected_models.dpr_query,
                        dpr_context_encoder=selected_models.dpr_context,
                        reader_encoder=selected_models.reader,
                        device=st.session_state.get('device', 'cpu')
                    )
                except RuntimeError as ex:
                    logger.error(str(ex))
                    st.error(str(ex))
                    st.info('If there are problems with CUDA - you can try to use CPU instead of GPU (toggle button)')
                    runtime_error = True

            if not runtime_error:
                show_evaluation(metrics)
            


