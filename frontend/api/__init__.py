from .state import get_model_languages, is_cuda_available, load_qa_models, load_qg_models

from .data import (
    upload_corpus,
    download_dataset,
    get_data_corpora,
    get_datasets,
    create_data_corpus,
    delete_corpus,
    delete_file_from_corpus)

from .ml import predict_qa, predict_qg, evaluate
