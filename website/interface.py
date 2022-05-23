import logging

def get_answer_uploaded(model_name: str, uploaded_dataset_name: str, question: str) -> str:
    logging.info(f"""Requested answer with model {model_name}
                 on uploaded dataset {uploaded_dataset_name}:
                 {question}""")
    pass

def get_answer_prefetched(model_name: str, prefetched_dataset_name: str, question: str) -> str:
    logging.info(f"""Requested answer with model {model_name}
                on prefetched dataset {prefetched_dataset_name}:
                {question}""")
    pass

def get_evaluation_function(model_name: str, prefetched_dataset_name: str) -> callable:
    logging.info(f"""Requested evaluation with model {model_name}
            on prefetched dataset {prefetched_dataset_name}.""")
    pass