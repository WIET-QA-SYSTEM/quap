from uuid import UUID
from requests import delete

from sqlalchemy.orm import Session

from .models import DataCorpus, Dataset, StoredDocument, StoredDocumentFragment


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

class StoredDocumentRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, document: StoredDocument) -> None:
        self.session.add(document)

    def get(self, id: UUID) -> StoredDocument:
        return self.session.query(StoredDocument).filter_by(id=id).one()

    def exists_in_corpus(self, name: str, corpus: DataCorpus) -> bool:
        return self.session.query(
            self.session.query(StoredDocument).filter_by(name=name, corpus=corpus).exists()
        ).scalar()

    def get_from_corpus(self, name: str, corpus: DataCorpus) -> StoredDocument:
        return self.session.query(StoredDocument).filter_by(name=name, corpus=corpus).first()

    def remove_from_corpus(self, name: str, corpus: DataCorpus) -> None:
        self.session.query(StoredDocument).filter_by(name=name, corpus=corpus).delete()

    def list(self) -> list[StoredDocument]:
        return self.session.query(StoredDocument).all()


class StoredDocumentFragmentRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, fragment: StoredDocumentFragment) -> None:
        self.session.add(fragment)

    def get(self, id: UUID) -> StoredDocumentFragment:
        return self.session.query(StoredDocumentFragment).filter_by(id=id).one()

    def list(self) -> list[StoredDocumentFragment]:
        return self.session.query(StoredDocumentFragment).all()    


class DatasetRepository(BaseSQLAlchemyRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add(self, dataset: Dataset) -> None:
        self.session.add(dataset)

    def get(self, id: UUID) -> Dataset:
        return self.session.query(Dataset).filter_by(id=id).one()

    def list(self) -> list[Dataset]:
        return self.session.query(Dataset).all()
