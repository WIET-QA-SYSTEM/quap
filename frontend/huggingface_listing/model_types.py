from enum import Enum

class ModelType(Enum):
    DPR = "dpr"
    READER = "question-answering"
    QUESTION_GENERATOR = "question-generation"
