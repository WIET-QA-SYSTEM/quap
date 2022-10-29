from fastapi import APIRouter
from torch.cuda import is_available

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

    return {
        'retriever': {
            'query': dpr_retriever.query_encoder.language if dpr_retriever is not None else None,
            'context': dpr_retriever.passage_encoder.language if dpr_retriever is not None else None,
        },
        'reader': {
            'encoder': reader.inferencer.model.language_model.language if reader is not None else None
        },
        'question_generator': {
            'encoder_decoder': None  # fixme how to get it? haven't found any trace of language :)
        }
    }

@router.get('/cuda')
async def is_cuda_available():
    return {'available': is_available()}
