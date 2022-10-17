from typing import Union
from pathlib import Path
import os, re

from quap.utils.preprocessing.tika_client import TikaClient


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FormatUnifier(metaclass=Singleton):
    def __init__(self) -> None:
        tika_hist = os.environ['TIKA_HOST']
        tika_port = os.environ['TIKA_PORT']
        self._tika_client = TikaClient(tika_hist, int(tika_port))

    def _replace_empty_lines(self, text: str) -> str:
        return re.sub(r'\n{2,}', '\n\n', text)

    def extract_text(self, file: Union[str, Path, bytes]) -> str:
        if not isinstance(file, bytes):
            path = Path(file)
            if not path.exists():
                raise FileNotFoundError

            file = path.read_bytes()

        content = self._tika_client.extract(file)
        return self._replace_empty_lines(content)

    def detect_language(self, text: str) -> str:
        return self._tika_client.detect_language(text)
