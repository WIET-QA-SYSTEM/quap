from typing import List
import uuid

from haystack.utils import SquadData
from haystack import Label, Document, Answer, MultiLabel

import pandas as pd


class SquadData(SquadData):

    def __init__(self, squad_data):
        """
        :param squad_data: SQuAD format data, either as a dict with a `data` key, or just a list of SQuAD documents
        """
        if type(squad_data) == dict:
            self.version = squad_data.get("version")
            self.data = squad_data["data"]
        elif type(squad_data) == list:
            self.version = None
            self.data = squad_data
        self.df = self.to_df(self.data)
        self._documents = {
            doc.id: doc for doc in self.calculate_all_documents(self.data)
        }

    @property
    def documents(self) -> List[Document]:
        return list(self._documents.values())

    def to_label_objs(self):
        """
        Export all labels stored in this object to haystack.Label objects.
        """
        df_labels = self.df[["id", "question", "answer_text", "answer_start", "document_id"]]
        record_dicts = df_labels.to_dict("records")
        labels = [
            MultiLabel(labels=[
                Label(
                    query=rd["question"],
                    document=self._documents[rd["document_id"]],
                    answer=Answer(rd["answer_text"]),
                    is_correct_answer=True,
                    is_correct_document=True,
                    id=rd["id"],
                    origin=rd.get("origin", "SquadData tool"),
                )
            ])
            for rd in record_dicts
        ]
        return labels

    @staticmethod
    def to_df(data) -> pd.DataFrame:
        """Convert a list of SQuAD document dictionaries into a pandas dataframe (each row is one annotation)"""
        flat = []
        for document in data:
            document["title"] = document.get("title", str(uuid.uuid4()))
            title = document["title"]
            
            for paragraph in document["paragraphs"]:
                context = paragraph["context"]

                for question in paragraph["qas"]:
                    q = question["question"]
                    qid = question["id"]
                    is_impossible = question.get("is_impossible", False)
                    question["is_impossible"] = is_impossible

                    # For no_answer samples
                    if len(question["answers"]) == 0:
                        flat.append({
                            "title": title,
                            "context": context,
                            "question": q,
                            "id": qid,
                            "answer_text": "",
                            "answer_start": None,
                            "is_impossible": is_impossible,
                            "document_id": title,
                        })
                    # For span answer samples
                    else:
                        for answer in question["answers"]:
                            answer_text = answer["text"]
                            answer_start = answer["answer_start"]
                            flat.append({
                                "title": title,
                                "context": context,
                                "question": q,
                                "id": qid,
                                "answer_text": answer_text,
                                "answer_start": answer_start,
                                "is_impossible": is_impossible,
                                "document_id": title,
                            })

        df = pd.DataFrame.from_records(flat)
        return df

    @staticmethod
    def calculate_all_documents(data) -> List[Document]:
        
        documents = []
        for document in data:
            title = document["title"]
            text = '\n'.join([
                paragraph["context"] for paragraph in document["paragraphs"]
            ])

            documents.append(Document(text, id=title))

        return documents
