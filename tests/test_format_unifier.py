from utils.format_unifier import FormatUnifier
from utils.tika_client import TikaClient
from helpers import TEST_DATA_PATH
import pytest

format_unifier = FormatUnifier()


def test_extract_from_pptx():
    t = format_unifier.extract_text(TEST_DATA_PATH / "samplepptx.pptx")
    assert "Sample PowerPoint" in t, \
        "PowerPoint keyword should be in extracted string"


@pytest.mark.integration_test
def test_extract_from_pdf():
    t = format_unifier.extract_text(TEST_DATA_PATH / "sample.pdf")
    assert "small demonstration" in t, \
        "small demonstration keyword should be in extracted string"

