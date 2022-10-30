from uuid import UUID

from pydantic import BaseModel, Field


# ==================== GET data corpora ===================
class DocumentGETResponse(BaseModel):
    id: UUID
    name: str
    language: str


class DataCorpusGETResponse(BaseModel):
    id: UUID
    name: str
    language: str
    documents: list[DocumentGETResponse]
    frozen: bool = Field(default=False)


class DataCorporaGETResponse(BaseModel):
    corpora: list[DataCorpusGETResponse]


# ==================== GET datasets ===================
class DatasetGETResponse(BaseModel):
    id: UUID
    name: str
    corpus: DataCorpusGETResponse


class DatasetsGETResponse(BaseModel):
    datasets: list[DatasetGETResponse]


# ==================== POST data corpora ===================
class CreateDataCorpusPOSTRequest(BaseModel):
    name: str


# ==================== POST datasets ===================
class DownloadDatasetPOSTRequest(BaseModel):
    name: str
