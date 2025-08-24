from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from models.llm import get_llm
from rag.splitter import split_documents
from rag.vector_store import create_vector_store, load_vector_store
from langchain_core.vectorstores import VectorStore

def build_rag_chain(documents=None, response_mode="concise", persist_path="vector_db/"):
    """
    Builds and returns a RetrievalQA chain using a retriever and LLM.
    Supports 'concise' and 'detailed' response modes.
    
    Args:
        documents (List[Document], optional): Raw documents to be split and embedded if vector DB doesn't exist.
        response_mode (str): 'concise' or 'detailed'
        persist_path (str): Path where vector store is or should be persisted.

    Returns:
        RetrievalQA or None: A configured RetrievalQA chain, or None if vector store cannot be created.
    """

    # Load or create vector store with better error handling
    vector_store = None
    try:
        vector_store: VectorStore = load_vector_store(persist_path)
        print(f"✅ Successfully loaded vector store from {persist_path}")
    except Exception as e:
        print(f"⚠️ Failed to load vector store: {str(e)}")
        
        # Try to build vector store from documents if available
        if documents is not None:
            try:
                print("🔄 Creating new vector store from provided documents...")
                split_docs = split_documents(documents)
                vector_store: VectorStore = create_vector_store(split_docs, persist_path)
                print("✅ Successfully created new vector store")
            except Exception as create_error:
                print(f"❌ Failed to create vector store: {str(create_error)}")
                return None
        else:
            # Try to load documents and create vector store
            try:
                print("🔄 Attempting to load documents and create vector store...")
                from rag.loader import load_documents
                documents = load_documents()
                if documents:
                    split_docs = split_documents(documents)
                    vector_store: VectorStore = create_vector_store(split_docs, persist_path)
                    print("✅ Successfully created vector store from loaded documents")
                else:
                    print("❌ No documents found to create vector store")
                    return None
            except Exception as fallback_error:
                print(f"❌ Fallback document loading failed: {str(fallback_error)}")
                return None
    
    if vector_store is None:
        print("❌ Failed to initialize vector store")
        return None

    retriever = vector_store.as_retriever()
    llm = get_llm()

    if response_mode == "detailed":
        template = """
You are SustainaBOT, an expert in sustainable energy and carbon emissions.

Using the context provided, generate a **structured and comprehensive response** to the question, following the format below:

1. **Domain Knowledge**: Briefly explain the relevant background or domain-specific concepts required to understand the answer.
2. **Solution/Analysis**: Provide a deep, well-reasoned explanation addressing the question using the context provided.
3. **Conclusion**: Summarize the key takeaway or implication based on the above analysis.

Be precise, informative, and maintain a professional tone. Avoid redundancy and do not assume any information not found in the context.
If the context doesn't contain information relevant to the question, respond with 'I don't know based on the provided context.'

Context:
{context}

Question: {question}
"""
        chain_type = "stuff"  # Using stuff chain type for detailed mode
    else:
        template = """
You are SustainaBOT, an expert in sustainable energy and carbon emissions.

Using the context provided, give a **brief and concise** answer to the question. 
Include only the essential points and avoid unnecessary elaboration. 
Your goal is to communicate efficiently without missing key insights.

If the context doesn't contain information relevant to the question, respond with 'I don't know based on the provided context.'

Context:
{context}

Question: {question}
"""
        chain_type = "stuff"  # Using stuff chain type for concise mode

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type=chain_type,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return rag_chain
