def get_models_list() -> list[str]:  
    return [
        "Model 1",
        "Model 2", 
        "Model 3",
        "Model 4"
    ]

def get_model_datasets(model: str) -> list[str]:
    available_datasets = ["Dataset 1"]
    if model in ["Model 1", "Model 3"]:
        available_datasets.append("Dataset 2")
        available_datasets.append("Dataset 3")
    if model in ["Model 2", "Model 3"]:
        available_datasets.append("Dataset 4")
        available_datasets.append("Dataset 5")
    if model in ["Model 4"]:
        available_datasets.append("Dataset 5")
    return available_datasets
