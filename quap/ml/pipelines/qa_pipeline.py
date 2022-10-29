from typing import Union
import logging

from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from quap.data.models import DataCorpus, Dataset
from quap.document_stores import DataCorpusStore
from quap.ml.nodes.retriever import IndexedBM25, IndexedDPR


logger = logging.getLogger('quap')


class QAPipeline:
    def __init__(self, storage: DataCorpusStore,
                 retriever: Union[IndexedBM25, IndexedDPR], reader: FARMReader) -> None:
        self.storage = storage
        self.retriever = retriever
        self.reader = reader

    # TODO add params to the call?
    def __call__(self, corpus: DataCorpus, questions: Union[str, list[str]]):
        """
        Returns dictionaries containing answers sorted by (desc.) score.
        Example:
         ```python
            |{
            |    'queries': ['Who is the father of Arya Stark?'],
            |    'answers': [[Answer(
            |                 'answer': 'Eddard,',
            |                 'context': "She travels with her father, Eddard, to King's Landing when he is",
            |                 'score': 0.9787139466668613,
            |                 'offsets_in_context': [Span(start=29, end=35],
            |                 'offsets_in_context': [Span(start=347, end=353],
            |                 'document_id': '88d1ed769d003939d3a0d28034464ab2'
            |                 ),...
            |              ]]
            |}

        # todo parameters description
        :param corpus:
        :param questions:
        :return:
        """

        if isinstance(questions, str):
            questions = [questions]

        logger.info('indexing started')
        self.retriever.index(corpus, self.storage)
        logger.info('indexing finished')

        pipeline = ExtractiveQAPipeline(self.reader, self.retriever)
        return pipeline.run_batch(questions, params={
            'Retriever': {'index': self.retriever.index_name(corpus)}
        })

    def eval(self, dataset: Dataset) -> dict[str, dict[str, float]]:
        corpus = dataset.corpus
        logger.info('indexing started')
        self.retriever.index(corpus, self.storage)
        logger.info('indexing finished')

        eval_labels = self.storage.get_all_labels_aggregated(index=dataset.labels_index,
                                                             drop_negative_labels=True,
                                                             drop_no_answers=True)

        pipeline = ExtractiveQAPipeline(self.reader, self.retriever)
        eval_result = pipeline.eval(labels=eval_labels, params={
            'Retriever': {'index': self.retriever.index_name(corpus)}
        })

        metrics = eval_result.calculate_metrics()
        return metrics
