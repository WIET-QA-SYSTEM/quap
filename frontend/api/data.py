from typing import Any
from uuid import UUID
import io

import requests


def get_data_corpora() -> list[dict[str, Any]]:
    response = requests.get('http://localhost:9100/data/corpora')
    if not response.ok:
        pass  # todo do something?
    return response.json()['corpora']


def create_data_corpus(name: str) -> None:
    response = requests.post('http://localhost:9100/data/corpora', json={'name': name})
    if not response.ok:
        pass  # todo do something?


def get_datasets() -> list[dict[str, Any]]:
    response = requests.get('http://localhost:9100/data/datasets')
    if not response.ok:
        pass  # todo do something?
    return response.json()['datasets']


def upload_corpus(corpus_id: UUID, files: list[io.BytesIO]) -> None:

    # todo refactor to send everything as a single request
    for file in files:
        response = requests.post(f'http://localhost:9100/data/corpora/{corpus_id}',
                                 files={'file': (file.name, file)})
        if not response.ok:
            pass  # todo do something?

def delete_file_from_corpus(corpus_id: UUID, file_id: UUID) -> None:
    response = requests.delete(f'http://localhost:9100/data/corpora/{corpus_id}/{file_id}')
    if not response.ok:
        pass  # todo do something?

def delete_corpus(corpus_id: UUID) -> None:
    response = requests.delete(f'http://localhost:9100/data/corpora/{corpus_id}')
    if not response.ok:
        pass  # todo do something?

def download_dataset(dataset_name: str) -> None:
    response = requests.post('http://localhost:9100/data/datasets/download', json={'name': dataset_name})
    if not response.ok:
        pass  # todo do something?
