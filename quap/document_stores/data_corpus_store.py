import logging

from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Document as HaystackDocument

from quap.data.models import DataCorpus, Document, Context
from quap.ml.preprocessing import PassageSegmentation


logger = logging.getLogger('quap')


class DataCorpusStore(ElasticsearchDocumentStore):

    def __init__(self, host: str = "localhost", port: int = 9200, scheme: str = "http",
                 index: str = "document", label_index: str = "label"):
        super().__init__(host=host, port=port, scheme=scheme, index=index, label_index=label_index)

    def index_exists(self, index_name: str) -> bool:
        return self.client.indices.exists(index=index_name)

    def add_document(
            self,
            document: Document,
            split_strategy: str = 'spacy-tokens',
            window_size: int = 100,
            stride: float = 0.9
    ) -> None:

        """
        Adds document to the Elasticsearch store. Overwrites existing document.
        Even if the content hasn't changed -> the documents will still be overwritten.

        Assumes that document's name is uniquely identifying it.

        If the document with the same name exists, then it gets removed,
        and all the contexts in the contexts index related to that document
        get removed as well, and then new ones are inserted.

        This adding does not affect any existing model-specific indices with embeddings.
        Models should react themselves to the changes made here.

        todo parameters description
        :param document:
        :param split_strategy:
        :param window_size:
        :param stride:
        :return:
        """

        if self.index_exists(document.corpus.original_documents_index):
            haystack_doc = self.get_document_by_id(document.name, index=document.corpus.original_documents_index)
            if haystack_doc is not None:
                self.remove_document(document)

        self.write_documents([HaystackDocument(content=document.text, id=document.name)],
                             index=document.corpus.original_documents_index)

        # TODO do we need some kind of fallback for multilingual tokenizer or no tokenization? i suppose not for now :)
        segmentation = PassageSegmentation(split_strategy, window_size, stride, document.language)
        contexts = segmentation.split(document)

        haystack_docs = [
            HaystackDocument(context.text, id=str(context.id), meta={
                'document_name': document.name,
                'offset': context.offset
            })
            for context in contexts
        ]
        self.write_documents(haystack_docs, index=document.corpus.contexts_index)

    def remove_document(self, document: Document) -> None:
        """
        Removes the document itself from the original documents index, and all its
        contexts from the contexts index.

        This removal does not affect any existing model-specific indices with embeddings.
        Models should react themselves to the changes made here.

        todo parameters description
        :param document:
        :return:
        """

        # deletes all the contexts of the specified document
        self.delete_all_documents(index=document.corpus.contexts_index, filters={
            '$and': {'document_name': {'$eq': document.name}}
        })
        self.delete_documents(ids=[str(document.id)], index=document.corpus.original_documents_index)
