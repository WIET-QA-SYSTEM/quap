import requests


def load_qa_models(
    retriever_type: str = 'dpr',
    dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
    dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
    reader_encoder: str = 'deepset/roberta-base-squad2',
    device: str = 'cpu'
) -> None:

    response = requests.put('http://localhost:9100/state/models', json={
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
    })

    if not response.ok:
        print(response.text)
        pass  # todo do something?


def load_qg_models(
    reader_encoder: str = 'deepset/roberta-base-squad2',
    generator: str = 'valhalla/t5-base-e2e-qg',
    device: str = 'cpu'
) -> None:

    response = requests.put('http://localhost:9100/state/models', json={
        "reader_specification": {
            "encoder": reader_encoder,
            "device": device
        },
        "question_generator_specification": {
            "encoder_decoder": generator,
            "device": device
        }
    })

    if not response.ok:
        print(response.text)
        pass  # todo do something?


def get_model_languages() -> dict[str, dict[str, str]]:
    response = requests.get('http://localhost:9100/state/models/languages')
    if not response.ok:
        pass  # todo do something?
    return response.json()


def is_cuda_available() -> bool:
    response = requests.get('http://localhost:9100/state/cuda')
    if not response.ok:
        pass  # todo do something?

    cuda_available: bool = response.json()['available']
    return cuda_available
