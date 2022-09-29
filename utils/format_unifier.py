from pathlib import Path
from pptx import Presentation


class FormatUnifier:
    def extract_text_from_document(self, path_to_file: str) -> bytes:
        path = Path(path_to_file)
        if not path.exists():
            raise FileExistsError
        if path.suffix == '.pdf':
            return path.read_bytes()
        elif path.suffix == '.pptx':
            return self.extract_from_pptx(path)

    @staticmethod
    def extract_from_pptx(pdf: Path) -> bytes:
        f = pdf.open("rb")
        prs = Presentation(f)
        text: str = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for t in paragraph.runs:
                        text += ' /n '
                        text += t.text
        return text.encode('utf-8')
