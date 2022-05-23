import uuid
import os

from datasets import load_dataset
import pandas as pd

import haystack as hs
from haystack.document_stores import ElasticsearchDocumentStore


class Dataset:
    @property
    def document_store(self):
        return self._document_store

    def _configure_elasticsearch(self, index_name: str) -> None:
        self._document_store = ElasticsearchDocumentStore(
            host=os.getenv('ELASTICSEARCH_HOST', 'localhost'),
            port=int(os.getenv('ELASTICSEARCH_PORT', 9200)),
            scheme=os.getenv('ELASTICSEARCH_SCHEME', 'http'),
            index=index_name
        )

    # def list_documents(self) -> List[str]:
    #     raise NotImplementedError('Not implemented for superclass')

    # def get_document_content(self, name: str) -> List[str]:
    #     raise NotImplementedError('Not implemented for superclass')


class UploadedDataset(Dataset):
    def __init__(self, directory: str) -> None:
        self._index_name = 'uploaded_' + str(uuid.uuid4())
        
        self._configure_elasticsearch(self._index_name)
        
        docs = hs.utils.preprocessing.convert_files_to_docs(directory)
        self._document_store.write_documents(docs, self._index_name)
   

class PrefetchedDataset(Dataset):
    def __init__(self, dataset_name: str) -> None:
        self._index_name = 'prefetched_' + dataset_name

        self._configure_elasticsearch(self._index_name)
        
        try:
            dataset = load_dataset(dataset_name)
        except Exception as ex:
            raise ValueError('Dataset not supported') from ex
        
        if dataset_name == 'squad':
            # using https://github.com/deepset-ai/haystack/blob/master/haystack/utils/squad_data.py

            dataset = pd.concat([
                dataset['train'].to_pandas(),
                dataset['validation'].to_pandas()
            ])

            docs = [hs.Document(text) for text in dataset['context'].unique()]
            data = dataset.to_dict('records')

            labels = [
                hs.Label(
                    query=rd['question'],
                    answer=hs.Answer(),
                    is_correct_answer=True,
                    is_correct_document=True,
                    id=rd['id'],
                    origin='gold-label'
                )
                for rd in data
            ]


        elif dataset_name == 'piqa':
            # parse piqa dataset
            pass
        else:
            raise ValueError('Dataset not supported')  
