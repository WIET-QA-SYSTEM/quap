from typing import List

import haystack as hs

from .dataset import PrefetchedDataset, Dataset

class QASystem:
    def __init__(self, model_name: str, device: str = 'cpu'):
        # FIXME had problem with num_processes not specified  https://stackoverflow.com/questions/67625238/get-error-nonetype-object-has-no-attribute-dumps-when-load-model-in-haystack
        self.reader = hs.nodes.FARMReader(model_name, use_gpu=(device!='cpu'), num_processes=0)
        
    def _prepare_pipeline(self, dataset: Dataset):
        retriever = hs.nodes.BM25Retriever(dataset._document_store)
        return hs.pipelines.ExtractiveQAPipeline(
            retriever=retriever,
            reader=self.reader
        )

    def ask(self, dataset: Dataset, question: str) -> List[hs.Answer]:
        pipeline = self._prepare_pipeline(dataset)

        result =  pipeline.run( 
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

        # FARMReader returns a dict with "query" and "answers" keys
        return result['answers']

    def evaluate(self, dataset: PrefetchedDataset):
        if not isinstance(dataset, PrefetchedDataset):
            raise ValueError('only prefetched dataset can be evaluated')