from uuid import UUID

from sqlalchemy.orm import Session

from .models import DataCorpus, Dataset, Document, Context


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

    def get_by_name(self, name: str) -> DataCorpus:
        return self.session.query(DataCorpus).filter_by(name=name).one()

    def list(self) -> list[DataCorpus]:
        return self.session.query(DataCorpus).all()


class DocumentRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, document: Document) -> None:
        self.session.add(document)

    def get(self, id: UUID) -> Document:
        return self.session.query(Document).filter_by(id=id).one()

    def delete(self, document: Document) -> None:
        return self.session.delete(document)

    def list(self) -> list[Document]:
        return self.session.query(Document).all()


class DatasetRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, dataset: Dataset) -> None:
        self.session.add(dataset)

    def get(self, id: UUID) -> Dataset:
        return self.session.query(Dataset).filter_by(id=id).one()

    def get_by_name(self, name: str) -> Dataset:
        return self.session.query(Dataset).filter_by(name=name).one()

    def list(self) -> list[Dataset]:
        return self.session.query(Dataset).all()
