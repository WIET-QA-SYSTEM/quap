from typing import Union

from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from quap.data.models import DataCorpus, Dataset
from quap.document_stores import DataCorpusStore
from quap.ml.nodes.retriever import IndexedBM25, IndexedDPR


class QAPipeline:
    def __init__(self, storage: DataCorpusStore,
                 retriever: Union[IndexedBM25, IndexedDPR], reader: FARMReader) -> None:
        self.storage = storage
        self.retriever = retriever
        self.reader = reader

    # TODO add params to the call?
    def __call__(self, corpus: DataCorpus, questions: Union[str, list[str]]):  # todo what does it return??
        if isinstance(questions, str):
            questions = [questions]

        self.retriever.index(corpus, self.storage)

        pipeline = ExtractiveQAPipeline(self.reader, self.retriever)
        return pipeline.run_batch(questions, params={
            'Retriever': {'index': self.retriever.index_name(corpus)}
        })

    def eval(self, dataset: Dataset) -> dict[str, dict[str, float]]:
        corpus = dataset.corpus
        self.retriever.index(corpus, self.storage)

        eval_labels = self.storage.get_all_labels_aggregated(index=dataset.labels_index,
                                                             drop_negative_labels=True,
                                                             drop_no_answers=True)

        pipeline = ExtractiveQAPipeline(self.reader, self.retriever)
        eval_result = pipeline.eval(labels=eval_labels, params={
            'Retriever': {'index': self.retriever.index_name(corpus)}
        })

        metrics = eval_result.calculate_metrics()
        return metrics
