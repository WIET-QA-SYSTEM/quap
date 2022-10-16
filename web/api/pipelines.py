from pathlib import Path
from typing import Any, Optional, Union
from uuid import UUID

from haystack.nodes import FARMReader
from quap.data import DataCorpus, Document
from quap.data.orm import metadata, start_mappers
from quap.data.repository import DataCorpusRepository, DocumentRepository
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.nodes import IndexedBM25, IndexedDPR
from quap.ml.pipelines import QAPipeline
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from .db_access import corpus_repository
from .loader import load_qa_models


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
    retriever, reader = load_qa_models(retriever_type, dpr_question_encoder, dpr_context_encoder, reader_encoder, use_gpu)

    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    answers = pipeline(corpus, questions)

    return answers
    # TODO what type answers are?
