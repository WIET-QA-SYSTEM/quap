from dataclasses import dataclass
from typing import List

from haystack import Answer
from haystack.nodes import FARMReader, QuestionGenerator
from haystack.pipelines import QuestionAnswerGenerationPipeline
from quap.data.models import DataCorpus
from quap.document_stores import DataCorpusStore


@dataclass
class QGResult:
    question: str
    answers: List[Answer]


class QGPipeline:
    def __init__(self, storage: DataCorpusStore,
                 generator: QuestionGenerator, reader: FARMReader) -> None:
        self.storage = storage
        self.generator = generator
        self.reader = reader

    def __call__(self, corpus: DataCorpus, pairs_per_document: int = 5, answers_per_pair: int = 3):
        pipeline = QuestionAnswerGenerationPipeline(
            self.generator, self.reader)

        results_for_document = {}

        if not self.storage.index_exists(index_name=corpus.contexts_index):
            # Storage is empty
            return {}

        for document in self.storage.get_all_documents(index=corpus.contexts_index):
            doc_result = pipeline.run(documents=[document])

            if document.meta['name'] not in results_for_document:
                results_for_document[document.meta['name']] = []

            for query, answers in zip(doc_result['queries'], doc_result['answers']):

                results_for_document[document.meta['name']].append(
                    (query, answers, max(answer.score for answer in answers))
                )

        for document, results in results_for_document.items():
            # sort by max achievable score
            results.sort(key=lambda query_tuple: query_tuple[2], reverse=True)
            results = results[:pairs_per_document]
            # Trim answers to the requested amount
            results = [QGResult(
                query_tuple[0], query_tuple[1][:answers_per_pair]
            ) for query_tuple in results]

            results_for_document[document] = results

        return results_for_document
