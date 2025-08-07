import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def load_pdfs_from_folder(folder_path: str = "data/reports/") -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, filename))
            docs = loader.load()
            documents.extend(docs)
    return documents
