from utils.format_unifier import FormatUnifier
from . import TEST_DATA_PATH
import pytest
tika_host = os.environ['TIKA_HOST']
tika_port = os.environ['TIKA_PORT']
format_unifier = FormatUnifier()


def test_extract_from_pptx():
    t = format_unifier.extract_bytes_from_document(TEST_DATA_PATH / "samplepptx.pptx")
    assert "Sample PowerPoint" in t, \
        "PowerPoint keyword should be in extracted string"


def test_extract_from_pdf():
    t = format_unifier.extract_bytes_from_document(TEST_DATA_PATH / "samplepptx.pptx")

