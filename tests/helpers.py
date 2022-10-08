from typing import List
import uuid, random, string
from pathlib import Path
from quap.data import DataCorpus, Dataset

TESTS_ROOT_PATH = Path(__file__).parent
TEST_DATA_PATH = TESTS_ROOT_PATH / 'data'

ENV_PATH = TEST_DATA_PATH.parent / '.env'


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def generate_random_name(length: int) -> str:
    chars = random.choices(string.ascii_letters, k=length)
    return ''.join(chars)


def generate_random_data_corpora(count: int) -> List[DataCorpus]:
    return [
        DataCorpus(generate_random_name(12))
        for _ in range(count)
    ]


def generate_random_datasets(count: int) -> List[Dataset]:
    return [
        Dataset(generate_random_name(12), generate_random_data_corpora(1)[0])
        for _ in range(count)
    ]
