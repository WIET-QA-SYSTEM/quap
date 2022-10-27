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
class QuestionAnsweringPOSTRequest(BaseModel):
    corpus_id: UUID
    questions: list[str] = Field(min_length=1)
    retriever_specification: RetrieverSpecification
    reader_specification: ReaderSpecification


class QuestionAnsweringPOSTResponse(BaseModel):
    records: list[Record]


# ============== question generation ==============
class QuestionGenerationPOSTRequest(BaseModel):
    corpus_id: UUID
    question_generator_specification: QuestionGeneratorSpecification
    reader_specification: ReaderSpecification


class QuestionGenerationPOSTResponse(BaseModel):
    records: list[Record]
