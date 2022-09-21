from asyncio import base_subprocess
import unittest
import os
from data_storage.schema import Base, DataCorpus, Document
from data_storage.schema import BaseSession
from data_storage.config import documents_path
from uuid import uuid4


class DataCorpusTest(unittest.TestCase):

    def test_creation_removal(self):
        # Create data corpus
        session = BaseSession()
        corpus = DataCorpus(name='sample_corpus')
        session.add(corpus)
        session.commit()

        # Add a document to it
        added_object = corpus.upload_document(
            session, "sample_document.pdf", "sample document_content")

        # File should now exist on drive
        self.assertTrue(os.path.exists(added_object.path),
                        "File added to database but not existing on drive!")

        # Now remove the document
        session.delete(added_object)
        session.commit()

        # File should disappear from drive
        self.assertFalse(os.path.exists(added_object.path),
                         "File removed from database but file content remaining on drive!")

        session.delete(corpus)
        session.commit()

    def test_content_replaced(self):
        # Create data corpus
        session = BaseSession()
        corpus = DataCorpus(name='sample_corpus')
        session.add(corpus)
        session.commit()
        print("Adding first doc")
        # Add a document to it
        first_object = corpus.upload_document(
            session, "sample_document.pdf", "sample document_content")
        print("Adding second doc")
        # Add another document with the same name but another content
        added_object = corpus.upload_document(
            session, "sample_document.pdf", "new_test_content")

        # Content of the file should be replaced
        document = session.query(Document).filter(
            Document.upload_name == 'sample_document.pdf', Document.data_corpus_id == corpus.id).one()

        with open(document.path, 'r') as f:
            self.assertEqual(f.read(), "new_test_content",
                             "Failed to replace file content with new text")

        # Old file should be deleted
        self.assertFalse(os.path.exists(first_object.path),
                         "After file replacement, previous content has not been removed")

        session.delete(corpus)
        session.commit()

    def test_cascade_deletion(self):
        # Create data corpus
        session = BaseSession()
        corpus = DataCorpus(name='sample_corpus')
        session.add(corpus)
        session.commit()

        # Add multiple documents to the corpus
        document_objects = [
            corpus.upload_document(session, name, 'content') for name in ['n1.pdf', 'n2.pdf']
        ]

        # Remove the corpus
        session.delete(corpus)
        session.commit()

        # Documents should be gone from the database AND the drive
        for document in document_objects:
            self.assertEqual(len(session.query(Document).filter(Document.id == document.id).all(
            )), 0, "Corpus removed but document remains in the database")

            self.assertFalse(
                os.path.exists(document.path),
                "Corpus removed but document remains on the drive"
            )


if __name__ == "__main__":
    unittest.main()
