from langchain_community.embeddings import HuggingFaceEmbeddings

def load_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
