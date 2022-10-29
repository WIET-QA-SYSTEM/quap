from typing import Optional

from pydantic import BaseModel, Field


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
    retriever_type: str = Field(regex=r'elasticsearch|dpr')
    query_encoder: str
    passage_encoder: str
    device: str = DeviceField


class ReaderSpecification(BaseModel):
    encoder: str
    device: str = DeviceField


class QuestionGeneratorSpecification(BaseModel):
    encoder_decoder: str
    device: str = DeviceField
