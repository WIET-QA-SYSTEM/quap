from typing import Any, Optional, Union
from uuid import UUID

import torch
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.pipelines import QAPipeline
from quap.ml.pipelines.qg_pipeline import QGPipeline

from .db_access import corpus_repository
from .loader import load_nlp_models


def predict_qg(
    corpus_id=UUID,
    reader_encoder: str = 'deepset/roberta-base-squad2',
    generator: str = 'valhalla/t5-base-e2e-qg',
    use_gpu: bool = False,
    params: dict = None,
    pairs_per_document=5,
    answers_per_pair=3
):

    corpus = corpus_repository.get(corpus_id)
    _, reader, generator = load_nlp_models(generator=generator, reader_encoder=reader_encoder, use_gpu=use_gpu,
                                           load_generator=True, load_retriever=False)

    pipeline = QGPipeline(ELASTICSEARCH_STORAGE, generator, reader)
    answers = pipeline(corpus, pairs_per_document, answers_per_pair)

    return answers


def predict_qa(
        corpus_id: UUID,
        questions: Union[list[str], str],
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        use_gpu: bool = False,
        params: dict = None
) -> list[dict[str, Any]]:

    corpus = corpus_repository.get(corpus_id)
    retriever, reader, _ = load_nlp_models(retriever_type, dpr_question_encoder, dpr_context_encoder,
                                           reader_encoder, use_gpu, load_generator=False, load_retriever=True)

    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    answers = pipeline(corpus, questions)

    return answers
    # TODO what type answers are?


def is_cuda_available() -> bool:
    return torch.cuda.is_available()
