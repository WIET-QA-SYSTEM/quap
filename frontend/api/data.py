import requests
import io
import os
from uuid import UUID
from typing import Any


def get_data_corpora() -> list[dict[str, Any]]:
    response = requests.get(f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/corpora')
    if not response.ok:
        pass  # todo do something?
    return response.json()['corpora']


def create_data_corpus(name: str) -> None:
    response = requests.post(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/corpora',
        json={'name': name}
    )
    if not response.ok:
        pass  # todo do something?


def get_datasets() -> list[dict[str, Any]]:
    response = requests.get(f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/datasets')
    if not response.ok:
        pass  # todo do something?
    return response.json()['datasets']


def upload_corpus(corpus_id: UUID, files: list[io.BytesIO]) -> None:

    # todo refactor to send everything as a single request
    for file in files:
        response = requests.post(
            f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/corpora/{corpus_id}',
            files={'file': (file.name, file)}
        )
        if not response.ok:
            pass  # todo do something?

def delete_file_from_corpus(corpus_id: UUID, file_id: UUID) -> None:
    response = requests.delete(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/corpora/{corpus_id}/{file_id}'
    )
    if not response.ok:
        pass  # todo do something?

def delete_corpus(corpus_id: UUID) -> None:
    response = requests.delete(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/corpora/{corpus_id}'
    )
    if not response.ok:
        pass  # todo do something?

def download_dataset(dataset_name: str) -> None:
    response = requests.post(
        f'http://{os.environ["BACKEND_HOST"]}:{os.environ["BACKEND_PORT"]}/data/datasets/download',
        json={'name': dataset_name}
    )
    if not response.ok:
        pass  # todo do something?
