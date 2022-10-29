from fastapi import APIRouter
from iso639 import languages

from service.state import ModelState
from models.state import ModelsLanguagesGETResponse


router = APIRouter(prefix='/state')
model_state = ModelState()


# todo implement this if you want to provide the possibility to load models explicitly
# @router.put('/models')
# async def load_models():
#     pass


@router.get('/models/languages', response_model=ModelsLanguagesGETResponse)
async def model_languages():
    dpr_retriever = model_state.dpr_retriever
    reader = model_state.farm_reader
    question_generator = model_state.question_generator

    languages_response = {
        'retriever': {
            'query': languages.get(name=dpr_retriever.query_encoder.language.capitalize()).alpha2
                     if dpr_retriever is not None else None,
            'context': languages.get(name=dpr_retriever.passage_encoder.language.capitalize()).alpha2
                       if dpr_retriever is not None else None,
        },
        'reader': {
            'encoder': languages.get(name=reader.inferencer.model.language_model.language.capitalize()).alpha2
                       if reader is not None else None
        },
        'question_generator': {
            'encoder_decoder': None  # fixme how to get it? haven't found any trace of language :)
        }
    }
    return languages_response
