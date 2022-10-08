from utils.format_unifier import FormatUnifier
from utils.tika_client import TikaClient
from helpers import TEST_DATA_PATH
import pytest


def test_extract_from_pptx(format_unifier: FormatUnifier):
    t = format_unifier.extract_text(TEST_DATA_PATH / "samplepptx.pptx")
    assert "Sample PowerPoint" in t, \
        "PowerPoint keyword should be in extracted string"


@pytest.mark.integration_test
def test_extract_from_pdf(format_unifier: FormatUnifier):
    t = format_unifier.extract_text(TEST_DATA_PATH / "sample.pdf")
    assert "small demonstration" in t, \
        "small demonstration keyword should be in extracted string"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    'text, expected_language',
    [
        ('Hello world, my name is John', 'en'),
        ('La parte continentale, delimitata dallarco alpino, confina a nord, da ovest a est, con Francia, Svizzera, Austria e Slovenia; il resto del territorio, circondato dai mari Ligure, Tirreno, Ionio e Adriatico, si protende nel mar Mediterraneo', 'it'),
        ('Cześć świecie, mam na imię Marcin', 'pl'),
        (' Dans ce petit texte de phrases simples, on ne peut pas vraiment', 'fr'),
        ('Die beiden Schüler aus Paris besuchen es und lernen viel über die Geschichte der Stadt', 'de')
    ]
)
def test_detect_language(format_unifier: FormatUnifier, text: str, expected_language: str):
    t = format_unifier.detect_language(text)
    assert t == expected_language
