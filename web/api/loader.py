from dataclasses import dataclass
import streamlit as st
from typing import Union, Optional
from haystack.nodes import FARMReader
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.nodes import IndexedBM25, IndexedDPR

@dataclass
class StateRegistry:
    bm25_retriever: Optional[IndexedBM25] = st.session_state.get('global_bm25_retriever', None)
    dpr_retriever: Optional[IndexedDPR] = st.session_state.get('global_dpr_retriever', None)
    farm_reader: Optional[FARMReader] = st.session_state.get('global_farm_reader', None)

    def save(self):
        st.session_state['global_bm25_retriever'] = self.bm25_retriever
        st.session_state['global_dpr_retriever'] = self.dpr_retriever
        st.session_state['global_farm_reader'] = self.farm_reader

main_state_registry = StateRegistry()

def load_qa_models(
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        use_gpu: bool = False
) -> tuple[Union[IndexedDPR, IndexedBM25], FARMReader]:
    # setting up the retriever
    if retriever_type == 'bm25':
        main_state_registry.bm25_retriever = main_state_registry.bm25_retriever or IndexedBM25(ELASTICSEARCH_STORAGE)
        retriever = main_state_registry.bm25_retriever
    elif retriever_type == 'dpr':

        if main_state_registry.dpr_retriever is None \
                or main_state_registry.dpr_retriever.passage_encoder.name != dpr_context_encoder \
                or main_state_registry.dpr_retriever.query_encoder.name != dpr_question_encoder:
            main_state_registry.dpr_retriever = IndexedDPR(
                document_store=ELASTICSEARCH_STORAGE,
                query_embedding_model=dpr_question_encoder,
                passage_embedding_model=dpr_context_encoder,
                use_gpu=use_gpu
            )

        retriever = main_state_registry.dpr_retriever
    else:
        # TODO maybe better use fallback with some kind of warning?
        raise ValueError(f'unknown retriever type - {retriever_type}')

    try:
        current_reader_name = main_state_registry.farm_reader.inferencer.model.language_model.model.name_or_path
    except:
        current_reader_name = None

    # setting up the reader
    if main_state_registry.farm_reader is None or current_reader_name != reader_encoder: # FIXME go deeper
        main_state_registry.farm_reader = FARMReader(reader_encoder, use_gpu=use_gpu)

    main_state_registry.save()

    return retriever, main_state_registry.farm_reader