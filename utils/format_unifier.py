from pathlib import Path
from pptx import Presentation
from PyPDF2 import PdfFileReader
from tika import parser
from utils.tika_client import TikaClient
import os


class FormatUnifier:
    def __init__(self) -> None:
        tika_hist = os.environ['TIKA_HOST']
        tika_port = os.environ['TIKA_PORT']
        self._tika_client = TikaClient(tika_hist, tika_port)

    def extract_text(self, path_to_file: str) -> str:
        path = Path(path_to_file)
        if not path.exists():
            raise FileNotFoundError
        if path.suffix == '.pdf':
            with path.open("rb") as pdf:
                return self._tika_client.extract(pdf)
        elif path.suffix == '.pptx':
            return self.extract_from_pptx(path)

    @staticmethod
    def extract_from_pptx(pptx: Path) -> str:
        with pptx.open("rb") as f:
            prs = Presentation(f)
        text_fragments = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for t in paragraph.runs:
                        text_fragments.append(t.text)
        return "\n".join(text_fragments)
