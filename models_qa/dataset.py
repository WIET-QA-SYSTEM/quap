from typing import Dict, List
import uuid

from datasets import load_dataset
import haystack as hs


class Dataset:
    @property
    def document_store(self):
        return self._document_store

    # def list_documents(self) -> List[str]:
    #     raise NotImplementedError('Not implemented for superclass')

    # def get_document_content(self, name: str) -> List[str]:
    #     raise NotImplementedError('Not implemented for superclass')


class UploadedDataset(Dataset):
    def __init__(self, directory: str) -> None:
        index_name = "uploaded_" + str(uuid.uuid4())
        
        self._document_store = hs.document_stores.ElasticsearchDocumentStore()
        
        docs = hs.utils.preprocessing.convert_files_to_docs(directory)
        
        self._document_store.write_documents(docs, index_name)
            
   

class PrefetchedDataset(Dataset):
    def __init__(self, dataset_name: str) -> None:
        index_name = "prefetched_" + dataset_name
    
        self._document_store = hs.document_stores.ElasticsearchDocumentStore()
        
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            raise ValueError("Dataset not supported: " + str(e))
        
        if dataset_name == "squad":
            # parse squad dataset        
            pass
        elif dataset_name == "piqa":
            # parse piqa dataset
            pass
        else:
            raise ValueError("Dataset not supported")  
