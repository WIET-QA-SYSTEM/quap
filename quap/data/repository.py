from uuid import UUID

from sqlalchemy.orm import Session

from .models import DataCorpus, Dataset


class BaseSQLAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def commit(self) -> None:
        self.session.commit()


class DataCorpusRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, corpus: DataCorpus) -> None:
        self.session.add(corpus)

    def get(self, id: UUID) -> DataCorpus:
        return self.session.query(DataCorpus).filter_by(id=id).one()

    def list(self) -> list[DataCorpus]:
        return self.session.query(DataCorpus).all()


class DatasetRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, dataset: Dataset) -> None:
        self.session.add(dataset)

    def get(self, id: UUID) -> Dataset:
        return self.session.query(Dataset).filter_by(id=id).one()

    def list(self) -> list[Dataset]:
        return self.session.query(Dataset).all()
