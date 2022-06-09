from pathlib import Path
from typing import List
import uuid
import os

from datasets import load_dataset

import haystack as hs
from haystack.document_stores import ElasticsearchDocumentStore

from .downloader import DatasetDownloader
from .utils import SquadData


class Dataset:
    @property
    def document_store(self):
        return self._document_store

    @property
    def data_dir(self) -> Path:
        return self._path

    def _configure_elasticsearch(self, index_name: str) -> None:
        self._document_store = ElasticsearchDocumentStore(
            host=os.getenv('ELASTICSEARCH_HOST', 'localhost'),
            port=int(os.getenv('ELASTICSEARCH_PORT', 9200)),
            scheme=os.getenv('ELASTICSEARCH_SCHEME', 'http'),
            index=index_name,
            label_index=index_name + '_labels'
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
        
        # if dataset_name not in ['squad', 'adversarial_qa']:
        #     try:
        #         dataset = load_dataset(dataset_name)
        #     except Exception as ex:
        #         raise ValueError('Dataset not supported') from ex
        
        if dataset_name == 'squad':
            # using https://github.com/deepset-ai/haystack/blob/master/haystack/utils/squad_data.py
            self._path = DatasetDownloader.download_squad()
            data = SquadData.from_file(self._path / 'train.json')

            docs = data.documents
            self._document_store.write_documents(docs)
            
            self._labels = data.to_label_objs()
            # self._document_store.write_labels(labels)


        elif dataset_name == 'adversarial_qa':
            self._path = DatasetDownloader.download_adversarial_qa()
            data = SquadData.from_file(self._path / 'combined' / 'train.json')

            docs = data.documents
            self._document_store.write_documents(docs)

            self._labels = data.to_label_objs()
        else:
            raise ValueError('Dataset not supported')

    @property
    def labels(self) -> List[hs.Label]:
        # return self._document_store.get_all_labels()
        return self._labels
