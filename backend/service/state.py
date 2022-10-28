from dataclasses import dataclass
from typing import Optional, Union
import logging

from haystack.nodes import FARMReader, QuestionGenerator
from quap.document_stores.document_store import ELASTICSEARCH_STORAGE
from quap.ml.nodes import IndexedBM25, IndexedDPR


logger = logging.getLogger('quap')


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# todo introduce locks for modifying (may be needed because of async endpoints)
@dataclass
class ModelState(metaclass=SingletonMeta):
    bm25_retriever: Optional[IndexedBM25] = None
    dpr_retriever: Optional[IndexedDPR] = None
    farm_reader: Optional[FARMReader] = None
    question_generator: Optional[QuestionGenerator] = None
    use_gpu: bool = False

    def _load_retriever(
            self,
            retriever_type: str = 'dpr',
            dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
            dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
            use_gpu: bool = False
    ) -> Union[IndexedDPR, IndexedBM25]:
        if retriever_type == 'bm25':
            self.bm25_retriever = self.bm25_retriever or IndexedBM25(ELASTICSEARCH_STORAGE)
            retriever = self.bm25_retriever
        elif retriever_type == 'dpr':
            if self.dpr_retriever is None \
                    or self.dpr_retriever.passage_encoder.model.name_or_path != dpr_context_encoder \
                    or self.dpr_retriever.query_encoder.model.name_or_path != dpr_question_encoder \
                    or self.use_gpu != use_gpu:
                self.dpr_retriever = IndexedDPR(
                    document_store=ELASTICSEARCH_STORAGE,
                    query_embedding_model=dpr_question_encoder,
                    passage_embedding_model=dpr_context_encoder,
                    use_gpu=use_gpu
                )

            retriever = self.dpr_retriever
        else:
            raise ValueError(f'unknown retriever type - {retriever_type}')

        return retriever

    def _load_reader(
            self,
            reader_encoder: str = 'deepset/roberta-base-squad2',
            use_gpu: bool = False
    ) -> FARMReader:
        if self.farm_reader is None \
                or self.farm_reader.inferencer.model.language_model.model.name_or_path != reader_encoder \
                or self.use_gpu != use_gpu:
            logger.info(f'Loading reader model: using GPU - {use_gpu}')
            logger.info(f'  reader encoder - {reader_encoder}')

            self.farm_reader = FARMReader(reader_encoder, use_gpu=use_gpu)

        return self.farm_reader

    def _load_generator(
            self,
            question_generator: str = 'valhalla/t5-base-e2e-qg',
            use_gpu: bool = False
    ) -> QuestionGenerator:
        # FIXME: Right now we always reload due to what
        # todo check this out
        # is likely a haystack bug
        if True or self.question_generator is None \
                or self.question_generator.model.name_or_path != question_generator \
                or self.use_gpu != use_gpu:

            self.question_generator = QuestionGenerator(question_generator, use_gpu=use_gpu)

        return self.question_generator

    def load_qa_models(
            self,
            retriever_type: str = 'dpr',
            dpr_question_encoder: str = 'facebook/dpr-question_encoder-single-nq-base',
            dpr_context_encoder: str = 'facebook/dpr-ctx_encoder-single-nq-base',
            reader_encoder: str = 'deepset/roberta-base-squad2',
            use_gpu: bool = False
    ) -> tuple[Union[IndexedDPR, IndexedBM25], FARMReader]:

        retriever = self._load_retriever(retriever_type, dpr_question_encoder, dpr_context_encoder, use_gpu)
        reader = self._load_reader(reader_encoder, use_gpu)
        self.use_gpu = use_gpu

        # todo if we want to make this optional, we have to take care of monitoring devices for each model
        self.clear(generator=True)

        return retriever, reader

    def load_qg_models(
            self,
            reader_encoder: str = 'deepset/roberta-base-squad2',
            generator: str = 'valhalla/t5-base-e2e-qg',
            use_gpu: bool = False
    ) -> tuple[QuestionGenerator, FARMReader]:

        generator = self._load_generator(generator, use_gpu)
        reader = self._load_reader(reader_encoder, use_gpu)

        # todo if we want to make this optional, we have to take care of monitoring devices for each model
        self.clear(retriever=True)

        return generator, reader

    def clear(self, retriever: bool = False, reader: bool = False, generator: bool = False) -> None:
        if retriever:
            self.dpr_retriever = None
        if reader:
            self.farm_reader = None
        if generator:
            self.question_generator = None
