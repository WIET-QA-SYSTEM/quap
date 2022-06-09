from pathlib import Path
import zipfile
import os

from urllib import request


PROJECT_DIR = Path(__file__).parent.parent


class DatasetDownloader:
    CACHE_DIR = PROJECT_DIR / '.cache'
    
    @classmethod
    def _prepare_cache(cls) -> None:
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def _check_cache(cls, dataset_name: str) -> bool:
        return (cls.CACHE_DIR / dataset_name).exists()

    @classmethod
    def download_squad(cls) -> Path:
        cls._prepare_cache()
        squad_path = cls.CACHE_DIR / 'squad'

        if cls._check_cache('squad'):
            return squad_path

        os.makedirs(squad_path, exist_ok=True)
        request.urlretrieve('https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json', squad_path / 'train.json')

        return squad_path

    @classmethod
    def download_adversarial_qa(cls) -> Path:
        cls._prepare_cache()
        advqa_path = cls.CACHE_DIR / 'adversarial_qa'

        if cls._check_cache('adversarial_qa'):
            return advqa_path
        
        os.makedirs(advqa_path, exist_ok=True)
        request.urlretrieve('https://adversarialqa.github.io/data/aqa_v1.0.zip', advqa_path / 'data.zip')

        zipf = zipfile.ZipFile(advqa_path / 'data.zip')
        zipf.extractall(advqa_path)
        
        return advqa_path
