import os
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from models.embeddings import load_embedding_model

def create_vector_store(documents: List[Document], persist_path: str = "vector_db/") -> VectorStore:
    os.makedirs(persist_path, exist_ok=True)
    embeddings = load_embedding_model()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(persist_path)
    return vectorstore

def load_vector_store(persist_path: str = "vector_db/") -> VectorStore:
    embeddings = load_embedding_model()
    return FAISS.load_local(persist_path, embeddings, allow_dangerous_deserialization=True)