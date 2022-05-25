from typing import List

def get_models_list() -> List[str]:  
    return [
        "deepset/roberta-base-squad2",
        "deepset/minilm-uncased-squad2",
        "ahotrod/albert_xxlargev1_squad2_512"
    ]

def get_dataset_list() -> List[str]:
    return [
        "squad"
    ]
