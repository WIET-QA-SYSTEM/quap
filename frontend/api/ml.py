import requests
import os
from collections import defaultdict
from uuid import UUID
from typing import Union


def predict_qg(
    corpus_id=UUID,
    reader_encoder: str = 'deepset/roberta-base-squad2',
    generator: str = 'valhalla/t5-base-e2e-qg',
    device: str = 'cpu',
    params: dict = None,
    pairs_per_document=5,
    answers_per_pair=3
) -> dict[str, dict[str, list[dict[str, Union[str, int]]]]]:

    response = requests.post(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/ml/predict/qg',
        json={
            "corpus_id": str(corpus_id),
            "reader_specification": {
                "encoder": reader_encoder,
                "device": device
            },
            "question_generator_specification": {
                "encoder_decoder": generator,
                "device": device
            }
        }
    )

    if not response.ok:
        pass  # todo do something?

    records = response.json()['records']
    filename2queries2records = defaultdict(lambda: defaultdict(list))
    for record in records:
        filename2queries2records[record['document_name']][record['question']].append(record)

    # casting back to normal dicts
    filename2queries2records = {key: dict(val) for key, val in filename2queries2records.items()}

    return dict(filename2queries2records)


def predict_qa(
        corpus_id: UUID,
        questions: Union[list[str], str],
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        device: str = 'cpu',
        params: dict = None
) -> dict[str, list[dict[str, Union[str, int]]]]:

    if isinstance(questions, str):
        questions = [questions]

    response = requests.post(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/ml/predict/qa',
        json={
            "corpus_id": str(corpus_id),
            "questions": questions,
            "retriever_specification": {
                "retriever_type": retriever_type,
                "query_encoder": dpr_question_encoder,
                "passage_encoder": dpr_context_encoder,
                "device": device
            },
            "reader_specification": {
                "encoder": reader_encoder,
                "device": device
            }
        }
    )

    if not response.ok:
        print(response.text)
        pass  # todo do something?

    records = response.json()['records']
    question2records = defaultdict(list)
    for record in records:
        question2records[record['question']].append(record)

    return dict(question2records)


def evaluate(
    dataset_id: UUID,
    retriever_type: str = 'dpr',
    dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
    dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
    reader_encoder: str = 'deepset/roberta-base-squad2',
    device: str = 'cpu',
    params: dict = None
) -> dict[str, dict[str, float]]:

    response = requests.post(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/ml/evaluate/qa',
        json={
            "dataset_id": str(dataset_id),
            "retriever_specification": {
                "retriever_type": retriever_type,
                "query_encoder": dpr_question_encoder,
                "passage_encoder": dpr_context_encoder,
                "device": device
            },
            "reader_specification": {
                "encoder": reader_encoder,
                "device": device
            }
        }
    )

    if not response.ok:
        print(response.text)
        pass  # todo do something?

    response_json = response.json()

    return {
        'Retriever': response_json['retriever_metrics'],
        'Reader': response_json['reader_metrics']
    }
