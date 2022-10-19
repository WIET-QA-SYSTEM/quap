from dataclasses import dataclass
from typing import Optional, Union
import logging

import streamlit as st
from haystack.nodes import FARMReader, QuestionGenerator
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.nodes import IndexedBM25, IndexedDPR


logger = logging.getLogger(__name__)


@dataclass
class StateRegistry:
    bm25_retriever: Optional[IndexedBM25] = st.session_state.get(
        'global_bm25_retriever', None)
    dpr_retriever: Optional[IndexedDPR] = st.session_state.get(
        'global_dpr_retriever', None)
    farm_reader: Optional[FARMReader] = st.session_state.get(
        'global_farm_reader', None)
    generator: Optional[QuestionGenerator] = st.session_state.get(
        'global_question_generator', None)
    use_gpu: bool = st.session_state.get('device', 'cpu') == 'gpu'

    def save(self): 
        st.session_state['global_bm25_retriever'] = self.bm25_retriever
        st.session_state['global_dpr_retriever'] = self.dpr_retriever
        st.session_state['global_farm_reader'] = self.farm_reader
        st.session_state['global_question_generator'] = self.generator
        st.session_state['device'] = 'gpu' if self.use_gpu else 'cpu'


main_state_registry = StateRegistry()


def load_nlp_models(
        retriever_type: str = 'dpr',
        dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
        dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
        reader_encoder: str = 'deepset/roberta-base-squad2',
        generator: str = 'valhalla/t5-base-e2e-qg',
        use_gpu: bool = False,
        load_generator: bool = False,
        load_retriever: bool = True,
        invalidate_unused: bool = True
) -> tuple[Union[IndexedDPR, IndexedBM25], FARMReader]:

    if invalidate_unused:
        if load_retriever == False:
            main_state_registry.dpr_retriever = None
            main_state_registry.bm25_retriever = None
            main_state_registry.save()
        if load_generator == False:
            main_state_registry.generator = None
            main_state_registry.save()

    # setting up the retriever
    if retriever_type == 'bm25':
        main_state_registry.bm25_retriever = main_state_registry.bm25_retriever or IndexedBM25(
            ELASTICSEARCH_STORAGE)
        retriever = main_state_registry.bm25_retriever
    elif retriever_type == 'dpr':
        if load_retriever:
            if main_state_registry.dpr_retriever is None \
                    or main_state_registry.dpr_retriever.passage_encoder.model.name_or_path != dpr_context_encoder \
                    or main_state_registry.dpr_retriever.query_encoder.model.name_or_path != dpr_question_encoder \
                    or main_state_registry.use_gpu != use_gpu:

                main_state_registry.dpr_retriever = IndexedDPR(
                    document_store=ELASTICSEARCH_STORAGE,
                    query_embedding_model=dpr_question_encoder,
                    passage_embedding_model=dpr_context_encoder,
                    use_gpu=use_gpu
                )

            retriever = main_state_registry.dpr_retriever
        else:
            retriever = None
    else:
        # TODO maybe better use fallback with some kind of warning?
        raise ValueError(f'unknown retriever type - {retriever_type}')

    try:
        current_reader_name = main_state_registry.farm_reader.inferencer.model.language_model.model.name_or_path
    except Exception as ex:
        current_reader_name = None

    # setting up the reader
    if main_state_registry.farm_reader is None \
            or current_reader_name != reader_encoder \
            or main_state_registry.use_gpu != use_gpu:

        logger.info(f'Loading reader model: using GPU - {use_gpu}')
        logger.info(f'  reader encoder - {reader_encoder}')

        main_state_registry.farm_reader = FARMReader(
            reader_encoder, use_gpu=use_gpu)

    if load_generator:
        try:
            current_generator_name = main_state_registry.generator.model.name_or_path
        except Exception as ex:
            current_generator_name = None

        # FIXME: Right now we always reload due to what
        # is likely a haystack bug
        if True or main_state_registry.generator is None \
                or current_generator_name != generator \
                or main_state_registry.use_gpu != use_gpu:

            main_state_registry.generator = QuestionGenerator(
                generator, use_gpu=use_gpu)

    main_state_registry.use_gpu = use_gpu
    main_state_registry.save()

    return retriever, main_state_registry.farm_reader, main_state_registry.generator
