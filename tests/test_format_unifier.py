from pathlib import Path

import pytest
from helpers import TEST_DATA_PATH

from quap.utils.preprocessing.format_unifier import FormatUnifier


@pytest.mark.integration_test
@pytest.mark.parametrize(
    'filepath, segment',
    [
        (TEST_DATA_PATH / "samplepptx.pptx", "Sample PowerPoint"),
        (TEST_DATA_PATH / "sample.pdf", "small demonstration")
    ]
)
def test_extract_filepath(format_unifier: FormatUnifier, filepath: Path, segment: str):
    t = format_unifier.extract_text(filepath)
    assert segment in t


@pytest.mark.integration_test
@pytest.mark.parametrize(
    'filepath, segment',
    [
        (TEST_DATA_PATH / "samplepptx.pptx", "Sample PowerPoint"),
        (TEST_DATA_PATH / "sample.pdf", "small demonstration")
    ]
)
def test_extract_bytes_from_file(format_unifier: FormatUnifier, filepath: Path, segment: str):
    t = format_unifier.extract_text(filepath.read_bytes())
    assert segment in t


@pytest.mark.integration_test
@pytest.mark.parametrize(
    'binary, segment',
    [
        ('This chunk of text is really interesting'.encode('utf-8'), 'This chunk of text is really interesting'),
        ('This chunk of text is really interesting'.encode('ascii'), 'This chunk of text is really interesting')
    ]
)
def test_extract_bytes_from_file(format_unifier: FormatUnifier, binary: bytes, segment: str):
    t = format_unifier.extract_text(binary)
    assert segment in t


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
