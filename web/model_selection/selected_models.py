from dataclasses import dataclass
from enum import Enum

class RetrieverType(Enum):
    DPR = "dpr"
    ELASTIC_SEARCH = "bm25"

@dataclass
class SelectedModels:
    dpr_context: str
    dpr_query: str
    retriever_type: RetrieverType
    reader: str
    question_generator: str

