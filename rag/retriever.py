from langchain_core.vectorstores import VectorStoreRetriever
from .vector_store import load_vector_store

def get_retriever(persist_path: str = "vector_db/") -> VectorStoreRetriever:
    vectorstore = load_vector_store(persist_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 7})
    return retriever