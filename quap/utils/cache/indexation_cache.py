from typing import Any
from data_storage.schema import DataCorpus, DPRCache, BaseSession
import pickle

class IndexationCache:
    def is_indexed(retriever: str, corpus: str) -> bool:
        raise NotImplementedError()

    def get_index(retriever: str, corpus: str) -> Any:
        if retriever.lower() == 'dpr':
            db_session = BaseSession()
            try:
                corpus_ref = db_session.query(DataCorpus).filter(DataCorpus.name == corpus).one()
            except:
                raise ValueError(f"Data corpus {corpus} not found.")

            cache_ref = corpus_ref.first()

            if len(cache_ref) == 0:
                # No cache for this retriever & corpus pair

                # Generate index
                index = b'placeholder'
                corpus_ref.cache_dpr_index(index)

                return index
            else:
                with open(cache_ref[0].binary_index_path, 'rb') as binary_index:
                    return pickle.load(binary_index)
                
        elif retriever.lower() == 'elasticsearch':
            pass

    def clear(retriver: str, corpus: str) -> None:
        pass