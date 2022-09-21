import os
import shutil

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy import event

from .config import engine_path, documents_path
from uuid import uuid4

if not os.path.exists(documents_path) or not os.path.isdir(documents_path):
    try:
        shutil.rmtree(documents_path)
    except:
        pass
    os.makedirs(documents_path)


Base = declarative_base()


class Document(Base):
    # An UTF-8 formatted document, saved locally
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    # Reference to the data corpus containing the given document
    data_corpus_id = Column(Integer, ForeignKey('data_corpus.id'))
    # How is the file saved locally
    path = Column(String, nullable=False)
    # What was the file's name when it was uploaded by the user
    upload_name = Column(String, nullable=False)

    @property
    def text(self):
        if '_text_cache' in self:
            return self._text_cache
        else:
            with open(self.path, 'r') as f:
                self._text_cache = f.read()
            return self._text_cache

    @text.setter
    def text(self, value):
        raise AttributeError(
            "Document's text cannot be set, please use DataCorpus.upload_document to replace content.")


@event.listens_for(Document, 'after_delete')
def remove_file_on_drive(mapper, connection, target):
    print("Removing file ", target.path)
    if os.path.exists(target.path):
        os.remove(target.path)


class DataCorpus(Base):
    __tablename__ = 'data_corpus'

    id = Column(Integer, primary_key=True)
    # Name of the data corpus
    name = Column(String, nullable=False)

    documents = relationship(
        'Document', cascade='all,delete', backref="data_corpus")

    def upload_document(self, session: Session, upload_name: str, content: str):
        """Adds a new document to the data corpus.
        If a document with the same upload name already exists, 
        it will be replaced"""

        # Check if document with the same upload name already exists
        existing_docs = session.query(Document).filter(
            Document.data_corpus_id == self.id, Document.upload_name == upload_name.strip()).all()

        for document in existing_docs:
            session.delete(document)

        filename = None
        while True:
            filename = str(uuid4())
            # The chance of repeating an uuid is extremally small, but check for it nevertheless
            if not os.path.exists(os.path.join(documents_path, f"{filename}.txt")):
                break

        filename += ".txt"

        # Save a file to the drive
        with open(os.path.join(documents_path, filename), 'w') as file:
            file.write(content)

        new_document = Document(data_corpus_id=self.id, path=os.path.join(
            documents_path, filename), upload_name=upload_name.strip())

        session.add(
            new_document
        )

        session.commit()

        return new_document


class Dataset(Base):
    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    # ID of the corresponding data corpus
    data_corpus_id = Column(Integer, ForeignKey('data_corpus.id'))
    data_corpus = relationship(DataCorpus)
    # Name of the dataset
    name = Column(String, nullable=False)


engine = create_engine(engine_path)

Base.metadata.create_all(engine)

BaseSession = sessionmaker(bind=engine)
