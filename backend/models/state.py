from typing import Optional, Any

from pydantic import BaseModel, Field, root_validator


# todo the whole validation class can be created
# todo https://stackoverflow.com/questions/71767536/pydantic-reusable-validation-for-dictionarys-keys-and-values


# ============== languages ==============
Language = Field(min_length=2, max_length=2)


class RetrieverLanguagesGETResponse(BaseModel):
    query: Optional[str] = Language
    passage: Optional[str] = Language


class ReaderLanguagesGETResponse(BaseModel):
    encoder: Optional[str] = Language


class QuestionGeneratorLanguagesGETResponse(BaseModel):
    encoder_decoder: Optional[str] = Language


class ModelsLanguagesGETResponse(BaseModel):
    retriever: RetrieverLanguagesGETResponse
    reader: ReaderLanguagesGETResponse
    question_generator: QuestionGeneratorLanguagesGETResponse


# ============== model specifications ==============
DeviceField = Field(regex=r'cpu|gpu')


class RetrieverSpecification(BaseModel):
    retriever_type: str = Field(regex=r'bm25|dpr')
    query_encoder: str
    passage_encoder: str
    device: str = DeviceField


class ReaderSpecification(BaseModel):
    encoder: str
    device: str = DeviceField


class QuestionGeneratorSpecification(BaseModel):
    encoder_decoder: str
    device: str = DeviceField


class ModelsSpecification(BaseModel):
    mode: str = Field('qa', regex=r'qa|qg')
    retriever_specification: Optional[RetrieverSpecification] = Field(None)
    reader_specification: Optional[ReaderSpecification] = Field(None)
    question_generator_specification: Optional[QuestionGeneratorSpecification] = Field(None)

    @root_validator
    def both_models_for_qa_or_qg_sent(cls, values: dict[str, Any]):
        qa = values['retriever_specification'] is not None \
            and values['reader_specification'] is not None \
            and values['question_generator_specification'] is None

        qg = values['retriever_specification'] is None \
            and values['reader_specification'] is not None \
            and values['question_generator_specification'] is not None

        if not (qa ^ qg):
            raise ValueError('either reader and retriever specification must be specified or reader and generator')

        values['mode'] = 'qa' if qa else 'qg'

        return values


# ============== cuda ==============

class CudaGETResponse(BaseModel):
    available: bool
