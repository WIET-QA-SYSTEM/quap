from fastapi import APIRouter, Response
from starlette import status
from sqlalchemy import exc

from quap.ml.pipelines import QAPipeline, QGPipeline
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE

# todo how to make these relative imports? always had a problem with that
from repositories import (
    session,
    dataset_repository,
    corpus_repository,
    document_repository
)
from models.ml import (
    QuestionAnsweringModelSpecificationsMixin,
    QuestionAnsweringInferencePOSTRequest,
    QuestionAnsweringInferencePOSTResponse,
    QuestionAnsweringEvaluationPOSTRequest,
    QuestionAnsweringEvaluationPOSTResponse,

    QuestionGenerationModelSpecificationsMixin,
    QuestionGenerationPOSTRequest,
    QuestionGenerationPOSTResponse,
)
from service.state import ModelState


router = APIRouter(prefix='/ml')
model_state = ModelState()


def create_qa_pipeline(specifications: QuestionAnsweringModelSpecificationsMixin) -> QAPipeline:
    # todo check if inference works i retriever and reader is on different devices?
    retriever_spec = specifications.retriever_specification
    reader_spec = specifications.reader_specification
    use_gpu = retriever_spec.device == 'gpu' and reader_spec.device == 'gpu'

    retriever, reader = model_state.load_qa_models(
        retriever_type=retriever_spec.retriever_type,
        dpr_question_encoder=retriever_spec.query_encoder,
        dpr_context_encoder=retriever_spec.passage_encoder,
        reader_encoder=reader_spec.encoder,
        use_gpu=use_gpu
    )

    pipeline = QAPipeline(ELASTICSEARCH_STORAGE, retriever, reader)
    return pipeline


def create_qg_pipeline(specifications: QuestionAnsweringEvaluationPOSTResponse) -> QGPipeline:
    # todo check if inference works if retriever and reader is on different devices?
    generator_spec = specifications.question_generator_specification
    reader_spec = specifications.reader_specification
    use_gpu = generator_spec.device == 'gpu' and reader_spec.device == 'gpu'

    generator, reader = model_state.load_qg_models(
        generator=generator_spec.encoder_decoder,
        reader_encoder=reader_spec.encoder,
        use_gpu=use_gpu
    )

    pipeline = QGPipeline(ELASTICSEARCH_STORAGE, generator, reader)
    return pipeline


@router.post('/predict/qa', response_model=QuestionAnsweringInferencePOSTResponse)
async def predict_qa(request: QuestionAnsweringInferencePOSTRequest):
    try:
        corpus = corpus_repository.get(request.corpus_id)
    except exc.NoResultFound:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pipeline = create_qa_pipeline(request)
    all_answers = pipeline(corpus, request.questions)

    records = []
    for query, answers in zip(all_answers['queries'], all_answers['answers']):
        for answer in answers:
            records.append({
                'question': query,
                'answer': answer.answer,
                'answer_score': answer.score,
                'document_name': answer.meta['name'],
                'context': answer.context,
                'context_offset': answer.offsets_in_context[0].start
            })

    return {'records': records}


@router.post('/predict/qg', response_model=QuestionGenerationPOSTResponse)
async def predict_qg(request: QuestionGenerationPOSTRequest):
    try:
        corpus = corpus_repository.get(request.corpus_id)
    except exc.NoResultFound:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pipeline = create_qg_pipeline(request)
    results = pipeline(corpus)

    records = []
    for document_name, qg_results in results.items():
        for qg_result in qg_results:
            for answer in qg_result.answers:
                records.append({
                    'question': qg_result.question,
                    'answer': answer.answer,
                    'answer_score': answer.score,
                    'document_name': answer.meta['name'],
                    'context': answer.context,
                    'context_offset': answer.offsets_in_context[0].start
                })

    return {'records': records}


@router.post('/evaluate/qa', response_model=QuestionAnsweringEvaluationPOSTResponse)
async def evaluate_qa(request: QuestionAnsweringEvaluationPOSTRequest):
    try:
        dataset = dataset_repository.get(request.dataset_id)
    except exc.NoResultFound:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    pipeline = create_qa_pipeline(request)
    # TODO how do we interrupt this? or interrupt evaluation?
    # TODO should this be another global thread? process? so we can send some signal to it?
    metrics = pipeline.eval(dataset)

    return {
        'retriever_metrics': metrics['Retriever'],
        'reader_metrics': metrics['Reader']
    }
