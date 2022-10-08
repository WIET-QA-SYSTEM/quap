from operator import index
from haystack.nodes import DensePassageRetriever, BM25Retriever, BaseRetriever

class IndexedDPR(DensePassageRetriever):
    def __init__(self, document_store, current_index='documents', *args, **kwargs):
        super().__init__(document_store=document_store, *args, **kwargs)
        self.current_index = current_index

    def set_index(self, index):
        self.current_index = index

    def retrieve(self, *args, **kwargs):       
        if 'index' in kwargs: 
            del kwargs['index']
        return super().retrieve(*args, index=self.current_index, **kwargs)

class IndexedBM25(BM25Retriever):
    def __init__(self, document_store, current_index='documents', *args, **kwargs):
        super().__init__(document_store=document_store, *args, **kwargs)
        self.current_index = current_index

    def set_index(self, index):
        self.current_index = index

    def retrieve(self, *args, **kwargs):        
        if 'index' in kwargs: 
            del kwargs['index']
        return super().retrieve(*args, index=self.current_index, **kwargs)