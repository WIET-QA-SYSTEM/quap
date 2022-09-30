from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from .models import DataCorpus, Dataset


class BaseSQLAlchemyRepository:
    def __init__(self, engine: Engine) -> None:
        self.session = Session(bind=engine)

    def commit(self) -> None:
        self.session.commit()


class DataCorpusRepository(BaseSQLAlchemyRepository):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    def add(self, corpus: DataCorpus) -> None:
        self.session.add(corpus)

    def get(self, id: UUID) -> DataCorpus:
        return self.session.query(DataCorpus).filter_by(id=id).one()

    def list(self) -> list[DataCorpus]:
        return self.session.query(DataCorpus).all()


class DatasetRepository(BaseSQLAlchemyRepository):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    def add(self, dataset: Dataset) -> None:
        self.session.add(dataset)

    def get(self, id: UUID) -> Dataset:
        return self.session.query(Dataset).filter_by(id=id).one()

    def list(self) -> list[Dataset]:
        return self.session.query(Dataset).all()
