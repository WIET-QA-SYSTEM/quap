import logging
import os
import shutil
import json
from pathlib import Path
from typing import Optional, Union

import requests
from haystack.utils import fetch_archive_from_http

from quap.utils.persistent_cache import persistent_cache


logger = logging.getLogger('quap')


def clean_directory(path: Union[str, Path]) -> None:
    path = Path(path)
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(f'{path} must be a directory')

    os.makedirs(path, exist_ok=True)
    shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


class DatasetDownloader:
    """Utility-class providing access to downloading datasets or getting their path if dataset already exists."""

    NQ_KEY = 'nq'
    SQUAD_KEY = 'squad'

    def __init__(self, datasets_dir: Union[str, Path] = '.cache/datasets') -> None:
        self.datasets_dir: Path = Path(datasets_dir).resolve()

    @persistent_cache('datasets')
    def download(self, dataset_name: str) -> Path:
        if dataset_name == DatasetDownloader.NQ_KEY:
            return self._fetch_natural_questions()
        elif dataset_name == DatasetDownloader.SQUAD_KEY:
            return self._fetch_squad()
        else:
            raise ValueError(f'unknown dataset name - {dataset_name}')

    def _fetch_natural_questions(self) -> Path:
        filename = 'nq_dev_subset_v2.json'
        url = 'https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/' + filename + '.zip'

        dataset_dir = self.datasets_dir / DatasetDownloader.NQ_KEY
        clean_directory(dataset_dir)

        if fetch_archive_from_http(url=url, output_dir=str(dataset_dir)):
            downloaded_file = dataset_dir / filename
            if not downloaded_file.exists() or not downloaded_file.is_file():
                logger.error("Natural Questions dataset has an incorrect filename")
                raise RuntimeError(f'downloaded item has an incorrect filename, should be {downloaded_file.name}')

            dataset_path = downloaded_file.rename(downloaded_file.parent / f"{DatasetDownloader.NQ_KEY}.json")
            return dataset_path

        raise RuntimeError('Natural Questions dataset downloading has failed')

    def _fetch_squad(self) -> Path:
        url = 'https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json'

        dataset_dir = self.datasets_dir / DatasetDownloader.SQUAD_KEY
        clean_directory(dataset_dir)

        squad_res = requests.get(url=url, headers={'Accept': 'application/json'})
        if squad_res.status_code != 200:
            logger.error("SQUAD dataset has not been downloaded correctly")
            raise RuntimeError(f'SQUAD dataset downloading has failed')

        filename = f"{DatasetDownloader.SQUAD_KEY}.json"
        dataset_path = dataset_dir / filename
        with open(dataset_path, mode='w') as file:
            json.dump(squad_res.json(), file, indent=2)

        return dataset_path
