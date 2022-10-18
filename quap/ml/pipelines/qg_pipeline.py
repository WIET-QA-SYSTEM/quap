from haystack.nodes import FARMReader, QuestionGenerator
from haystack.pipelines import QuestionAnswerGenerationPipeline

from quap.data.models import DataCorpus
from quap.document_stores import DataCorpusStore
from typing import List
from haystack import Answer
from dataclasses import dataclass

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

        results = {}

        for idx, document in enumerate(self.storage.get_all_documents(index=corpus.contexts_index)):
            doc_result = pipeline.run(documents=[document])


            results[document.meta['document_name']] = []


            for query, answers in zip(doc_result['queries'], doc_result['answers'])[:pairs_per_document]:
                partial_result = QGResult(query, answers[:answers_per_pair])
            
                results[document.meta['document_name']].append(partial_result)

        return results