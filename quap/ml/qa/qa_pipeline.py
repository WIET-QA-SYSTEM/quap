from sympy import comp
from quap.data.models import DataCorpus
from typing import Union
from quap.ml.indexed_retrievers import IndexedBM25, IndexedDPR
from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Pipeline

class QAPipeline:
    def __init__(self, storage: ElasticsearchDocumentStore, retriever: Union[IndexedBM25, IndexedDPR], reader):
        self.storage = storage
        self.retriever = retriever
        self.reader = reader

    def __call__(self, corpus: DataCorpus, questions):
        if isinstance(self.retriever, IndexedDPR):
            self.storage.update_embeddings(self.retriever, update_existing_embeddings=False, index=corpus.dpr_uuid)
        
            self.retriever.set_index(corpus.dpr_uuid)
        elif isinstance(self.retriever, IndexedBM25):
            self.retriever.set_index(corpus.elasticsearch_uuid)

        pipeline = Pipeline()
        pipeline.add_node(component=self.retriever, name="Retriever", inputs=["Query"])
        pipeline.add_node(component=self.reader, name="Reader", inputs=["Retriever"])

        return [
            pipeline.run(query=question) for question in questions
        ]

        

        