import pytest

from quap.data import Document, Context, DataCorpus
from quap.ml.preprocessing.passage_segmentation import PassageSegmentation


def test_passage_segmentation_wrong_language():
    with pytest.raises(ValueError):
        segmentation = PassageSegmentation(language='qq')


@pytest.mark.parametrize(
    'text, window_size, stride, expected_step, expected_passages',
    [
        ('Hello world! I have never been so pleased to see you all', 5, 0.6, 3,
         ['Hello world! I have', 'I have never been so', 'been so pleased to see', 'to see you all']),
        ('Hello world! I have never been so pleased to see you all', 15, 0.2, 3,
         ['Hello world! I have never been so pleased to see you all']),
        ('Hello world! I have never been so pleased to see you all', 7, 1.0, 7,
         ['Hello world! I have never been', 'so pleased to see you all']),
    ]
)
def test_passage_segmentation_split_spacy_tokens(text: str, window_size: int, stride: float,
                                                 expected_step: int, expected_passages: list[str]):

    segmentation = PassageSegmentation(split_strategy='spacy-tokens',
                                       window_size=window_size, stride=stride, language='en')
    assert segmentation.step == expected_step

    corpus = DataCorpus('test')
    doc = Document('document', 'en', corpus, text)
    contexts = segmentation.split(doc)
    assert [ctx.text for ctx in contexts] == expected_passages


@pytest.mark.parametrize(
    'text, window_size, stride, expected_step, expected_passages',
    [
        ('Hello world! I have never been so pleased to see you all', 100, 0.9, 90,
         ['Hello world! I have never been so pleased to see you all']),
    ]
)
def test_passage_segmentation_split_none(text: str, window_size: int, stride: float,
                                         expected_step: int, expected_passages: list[str]):

    segmentation = PassageSegmentation(split_strategy='none',
                                       window_size=window_size, stride=stride, language='en')
    assert segmentation.step == expected_step

    corpus = DataCorpus('test')
    doc = Document('document', 'en', corpus, text)
    contexts = segmentation.split(doc)
    assert [ctx.text for ctx in contexts] == expected_passages
