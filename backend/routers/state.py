from fastapi import APIRouter, Response
from torch.cuda import is_available
from starlette import status
from iso639 import languages

from service.state import ModelState
from models.state import (
    ModelsLanguagesGETResponse,
    CudaGETResponse,
    ModelsSpecification
)


router = APIRouter(prefix='/state')
model_state = ModelState()


@router.put('/models')
async def load_models(specifications: ModelsSpecification):
    if specifications.mode == 'qa':
        retriever_spec = specifications.retriever_specification
        reader_spec = specifications.reader_specification
        use_gpu = retriever_spec.device == 'gpu' and reader_spec.device == 'gpu'

        await model_state.load_qa_models(
            retriever_type=retriever_spec.retriever_type,
            dpr_question_encoder=retriever_spec.query_encoder,
            dpr_context_encoder=retriever_spec.passage_encoder,
            reader_encoder=reader_spec.encoder,
            use_gpu=use_gpu
        )
    elif specifications.mode == 'qg':
        generator_spec = specifications.question_generator_specification
        reader_spec = specifications.reader_specification
        use_gpu = generator_spec.device == 'gpu' and reader_spec.device == 'gpu'

        await model_state.load_qg_models(
            generator=generator_spec.encoder_decoder,
            reader_encoder=reader_spec.encoder,
            use_gpu=use_gpu
        )
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/models/languages', response_model=ModelsLanguagesGETResponse)
async def model_languages():
    dpr_retriever = model_state.dpr_retriever
    reader = model_state.farm_reader
    question_generator = model_state.question_generator

    languages_response = {
        'retriever': {
            'query': languages.get(name=dpr_retriever.query_encoder.language.capitalize()).alpha2
                     if dpr_retriever is not None else None,
            'passage': languages.get(name=dpr_retriever.passage_encoder.language.capitalize()).alpha2
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


@router.get('/cuda', response_model=CudaGETResponse)
async def is_cuda_available():
    return {'available': is_available()}
