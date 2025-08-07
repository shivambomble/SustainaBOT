from rag.loader import load_pdfs_from_folder
from rag.splitter import split_documents
from rag.vector_store import create_vector_store

if __name__ == "__main__":
    # Load and split docs
    docs = load_pdfs_from_folder("data/reports/")
    chunks = split_documents(docs)

    # Create vector DB
    create_vector_store(chunks, persist_path="vector_db/")
    print("Vector store created and saved.")
