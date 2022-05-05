from typing import List

import haystack as hs

from models_qa.dataset import PrefetchedDataset, Dataset

class QASystem:
    def __init__(self, model_name: str):
        self.reader = hs.reader.farm.FarmReader(model_name)
        
    def _prepare_pipeline(self, dataset: Dataset):
        retriever = hs.nodes.BM25Retriever(dataset._document_store)
        return hs.pipelines.ExtractiveQAPipeline(
            retriever=retriever,
            reader=self.reader
        )    

    def ask(self, dataset: Dataset, question: str):
        pipeline = self._prepare_pipeline(dataset)

        return pipeline.run(
            query=question,
            params={
                "Retriever": {
                    "top_k": 5
                },
                "Reader": {
                    "top_k": 1
                }
            }
        )

    def evaluate(self, dataset: PrefetchedDataset):
        pass