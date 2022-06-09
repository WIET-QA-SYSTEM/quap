from typing import List

from haystack.nodes import FARMReader, BM25Retriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack import Answer

from .dataset import PrefetchedDataset, Dataset

class QASystem:
    def __init__(self, model_name: str, device: str = 'cpu'):
        # FIXME had problem with num_processes not specified  https://stackoverflow.com/questions/67625238/get-error-nonetype-object-has-no-attribute-dumps-when-load-model-in-haystack
        # self._reader = FARMReader(model_name, use_gpu=(device!='cpu'), num_processes=0)
        self._reader = FARMReader(model_name, use_gpu=True)
        # self._reader = FARMReader(model_name, use_gpu=False)
        
    def _prepare_pipeline(self, dataset: Dataset):
        retriever = BM25Retriever(dataset._document_store)
        return ExtractiveQAPipeline(
            retriever=retriever,
            reader=self._reader
        )

    def ask(self, dataset: Dataset, question: str) -> List[Answer]:
        pipeline = self._prepare_pipeline(dataset)

        result = pipeline.run( 
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

    def evaluate_reader(self, dataset: PrefetchedDataset):
        if not isinstance(dataset, PrefetchedDataset):
            raise ValueError('only prefetched dataset can be evaluated')

        # self._reader.eval()

        pipeline = self._prepare_pipeline(dataset)

        result = pipeline.eval(labels=dataset.labels[:5], add_isolated_node_eval=True)

        return result.calculate_metrics()

        # result = self._reader.eval_on_file(dataset.data_dir, 'train.json')

        # return result

    def evaluate_system(self):
        pass
