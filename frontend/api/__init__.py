from .state import get_model_languages, is_cuda_available

from .data import (
    upload_corpus,
    download_dataset,
    get_data_corpora,
    get_datasets,
    create_data_corpus,
    delete_corpus,
    delete_file_from_corpus)

from .ml import predict_qa, predict_qg, evaluate
