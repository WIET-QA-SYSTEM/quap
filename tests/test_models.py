import pytest

from quap.data import DataCorpus, Dataset


# TODO define the __eq__ and __hash__ rules
@pytest.mark.parametrize(
    'corpus1,corpus2,are_equal',
    [

    ]
)
def test_data_corpus_equality_and_hashing(corpus1: DataCorpus, corpus2: DataCorpus, are_equal: bool):
    assert (corpus1 == corpus2) == are_equal
    if are_equal:
        assert hash(corpus1) == hash(corpus2)


@pytest.mark.parametrize(
    'dataset1,dataset2,are_equal',
    [

    ]
)
def test_dataset_equality_and_hashing(dataset1: DataCorpus, dataset2: DataCorpus, are_equal: bool):
    assert (dataset1 == dataset2) == are_equal
    if are_equal:
        assert hash(dataset1) == hash(dataset2)
