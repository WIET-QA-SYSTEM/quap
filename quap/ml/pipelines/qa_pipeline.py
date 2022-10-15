from typing import Union

from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from quap.data.models import DataCorpus
from quap.document_stores import DataCorpusStore
from quap.ml.nodes.retriever import IndexedBM25, IndexedDPR


class QAPipeline:
    def __init__(self, storage: DataCorpusStore,
                 retriever: Union[IndexedBM25, IndexedDPR], reader: FARMReader) -> None:
        self.storage = storage
        self.retriever = retriever
        self.reader = reader

    # TODO add params to the call?
    def __call__(self, corpus: DataCorpus, questions: Union[str, list[str]]):
        if isinstance(questions, str):
            questions = [questions]

        self.retriever.index(corpus, self.storage)

        pipeline = ExtractiveQAPipeline(self.reader, self.retriever)
        return pipeline.run_batch(questions, params={
            'Retriever': {'index': self.retriever.index_name(corpus)}
        })
