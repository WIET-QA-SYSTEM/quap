from huggingface_hub import list_models
from huggingface_hub.hf_api import ModelFilter

from huggingface_listing.model_types import ModelType

def get_model_list(model_type: ModelType):
    filter = ModelFilter(task=model_type.value)
    models = list_models(filter=filter, full=False)

    model_strings = [
        model.modelId for model in models
    ]

    return model_strings
