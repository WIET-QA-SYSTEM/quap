from pathlib import Path
from uuid import uuid4
import json

import pytest
from helpers import rmtree

from quap.utils.dataset_downloader import DatasetDownloader


@pytest.fixture
def tmpdir():
    tmpdir_path = str(uuid4())
    yield Path(tmpdir_path).resolve()
    rmtree(tmpdir_path)


def test_downloading_nq(tmpdir: Path):
    downloader = DatasetDownloader(datasets_dir=tmpdir)
    nq_path = downloader.download(DatasetDownloader.NQ_KEY)

    assert nq_path.exists()

    with nq_path.open('r', encoding='utf-8') as f:
        dataset = json.load(f)

    assert 'data' in dataset
    assert len(dataset['data']) > 0
    assert 'title' in dataset['data'][0]
    assert 'paragraphs' in dataset['data'][0]


def test_downloading_squad(tmpdir: Path):
    downloader = DatasetDownloader(datasets_dir=tmpdir)
    nq_path = downloader.download(DatasetDownloader.SQUAD_KEY)

    assert nq_path.exists()

    with nq_path.open('r', encoding='utf-8') as f:
        dataset = json.load(f)

    assert 'data' in dataset
    assert len(dataset['data']) > 0
    assert 'title' in dataset['data'][0]
    assert 'paragraphs' in dataset['data'][0]
