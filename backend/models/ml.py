from uuid import UUID

from pydantic import BaseModel, Field

from .state import RetrieverSpecification, ReaderSpecification, QuestionGeneratorSpecification


class Record(BaseModel):
    question: str
    answer: str
    answer_score: float
    document_name: str
    context: str
    context_offset: int = Field(ge=0)


# ============== question answering ==============
class QuestionAnsweringModelSpecificationsMixin(BaseModel):
    retriever_specification: RetrieverSpecification
    reader_specification: ReaderSpecification


# ==== inference ====
class QuestionAnsweringInferencePOSTRequest(QuestionAnsweringModelSpecificationsMixin, BaseModel):
    corpus_id: UUID
    questions: list[str] = Field(min_length=1)


class QuestionAnsweringInferencePOSTResponse(BaseModel):
    records: list[Record]


# ==== evaluation ====
class QuestionAnsweringEvaluationPOSTRequest(QuestionAnsweringModelSpecificationsMixin, BaseModel):
    dataset_id: UUID


class RetrieverMetrics(BaseModel):
    recall_multi_hit: float
    recall_single_hit: float
    precision: float
    map: float
    mrr: float
    ndcg: float


class ReaderMetrics(BaseModel):
    exact_match: float
    f1: float
    num_examples_for_eval: float


class QuestionAnsweringEvaluationPOSTResponse(BaseModel):
    retriever_metrics: RetrieverMetrics
    reader_metrics: ReaderMetrics


# ============== question generation ==============
class QuestionGenerationModelSpecificationsMixin(BaseModel):
    question_generator_specification: QuestionGeneratorSpecification
    reader_specification: ReaderSpecification


class QuestionGenerationPOSTRequest(QuestionGenerationModelSpecificationsMixin, BaseModel):
    corpus_id: UUID


class QuestionGenerationPOSTResponse(BaseModel):
    records: list[Record]
