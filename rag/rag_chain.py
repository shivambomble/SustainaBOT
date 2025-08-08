from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from models.llm import get_llm
from rag.splitter import split_documents
from rag.vector_store import create_vector_store, load_vector_store
from langchain_core.vectorstores import VectorStore

def build_rag_chain(documents=None, response_mode="concise", persist_path="vector_db/") -> RetrievalQA:
    """
    Builds and returns a RetrievalQA chain using a retriever and LLM.
    Supports 'concise' and 'detailed' response modes.
    
    Args:
        documents (List[Document], optional): Raw documents to be split and embedded if vector DB doesn't exist.
        response_mode (str): 'concise' or 'detailed'
        persist_path (str): Path where vector store is or should be persisted.

    Returns:
        RetrievalQA: A configured RetrievalQA chain.
    """

    # Load or create vector store
    try:
        vector_store: VectorStore = load_vector_store(persist_path)
    except Exception:
        if documents is None:
            raise ValueError("No documents provided to create vector store.")
        split_docs = split_documents(documents)
        vector_store: VectorStore = create_vector_store(split_docs, persist_path)

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
