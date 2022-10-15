from haystack.nodes import DensePassageRetriever, BM25Retriever

from quap.data import DataCorpus
from quap.document_stores import DataCorpusStore
from quap.utils.index_name import normalize_index_name


class IndexedDPR(DensePassageRetriever):
    def index_name(self, corpus: DataCorpus) -> str:
        index_name = f'{self.passage_encoder.model.config.name_or_path}-{corpus.id}'
        return normalize_index_name(index_name)

    def index(self, corpus: DataCorpus, document_store: DataCorpusStore) -> None:
        """
        Creates a new index for the specific encoder if it has not been created yet.

        Copies all the documents from the corpus' contexts index. If they are already copied,
        then it checks if any changes have been applied. Removes documents, that have been
        removed from the contexts index. Copies all the new ones and calculates embeddings
        for any document which is new or hasn't had embeddings before.

        todo parameters description
        :param corpus:
        :param document_store:
        :return:
        """

        """
        Implementation description:
        
        First we need to delete all the model contexts which are no more present in the contexts index,
        because their ids where updated on their content's update, so we can track this by comparing ids.
        After that we simply insert all the documents from context index skipping the duplicates.
        """

        model_index_name = self.index_name(corpus)

        documents = document_store.get_all_documents(corpus.contexts_index)
        if document_store.index_exists(model_index_name):
            model_documents = document_store.get_all_documents(model_index_name)

            documents_ids = set([doc.id for doc in documents])
            model_documents_ids = set([doc.id for doc in model_documents])

            deleted_ids = model_documents_ids - documents_ids
            document_store.delete_documents(ids=list(deleted_ids), index=model_index_name)

        document_store.write_documents(documents, index=model_index_name, duplicate_documents='skip')
        document_store.update_embeddings(self, index=model_index_name, update_existing_embeddings=False)


class IndexedBM25(BM25Retriever):
    def index_name(self, corpus: DataCorpus) -> str:
        return normalize_index_name(corpus.contexts_index)

    def index(self, corpus: DataCorpus, document_store: DataCorpusStore) -> None:
        pass
