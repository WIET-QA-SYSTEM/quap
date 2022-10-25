from typing import Any, Optional, Union
from uuid import UUID
import logging

import torch
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.pipelines import QAPipeline
from quap.ml.pipelines.qg_pipeline import QGPipeline

from .repositories import corpus_repository, dataset_repository
from .memory import load_nlp_models


logger = logging.getLogger('quap')


def predict_qg(
    corpus_id: UUID,
    reader_encoder: str = 'deepset/roberta-base-squad2',
    generator: str = 'valhalla/t5-base-e2e-qg',
    use_gpu: bool = False,
    params: dict = None,
    pairs_per_document=5,
    answers_per_pair=3
):

    corpus = corpus_repository.get(corpus_id)
    _, reader, generator = load_nlp_models(reader_encoder=reader_encoder,
                                           generator=generator,
                                           use_gpu=use_gpu,
                                           load_generator=True,
                                           load_retriever=False)

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
    retriever, reader, _ = load_nlp_models(retriever_type=retriever_type,
                                           dpr_question_encoder=dpr_question_encoder,
                                           dpr_context_encoder=dpr_context_encoder,
                                           reader_encoder=reader_encoder,
                                           use_gpu=use_gpu,
                                           load_generator=False,
                                           load_retriever=True)

    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    answers = pipeline(corpus, questions)

    return answers
    # TODO what type answers are?


def evaluate(
    dataset_id: Optional[UUID] = None,
    retriever_type: str = 'dpr',
    dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
    dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
    reader_encoder: str = 'deepset/roberta-base-squad2',
    use_gpu: bool = False,
    params: dict = None
) -> dict[str, dict[str, float]]:

    dataset = dataset_repository.get(dataset_id)
    retriever, reader, _ = load_nlp_models(retriever_type=retriever_type,
                                           dpr_question_encoder=dpr_question_encoder,
                                           dpr_context_encoder=dpr_context_encoder,
                                           reader_encoder=reader_encoder,
                                           use_gpu=use_gpu,
                                           load_generator=False,
                                           load_retriever=True)

    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    metrics = pipeline.eval(dataset)

    return metrics


def is_cuda_available() -> bool:
    return torch.cuda.is_available()
