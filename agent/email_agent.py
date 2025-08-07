import re
from rag.rag_chain import build_rag_chain
from utils.email_sender import send_email
from web_search.search import search_web
from models.llm import get_llm

def clean_markdown(text: str) -> str:
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)  

def email_agent(query: str, manager_email: str):
    rag_chain = build_rag_chain()
    llm = get_llm()

    # Try RAG response first
    response = rag_chain.invoke({"query": query})
    result = response["result"]

    # Fallback to Web Search if RAG fails
    if not result or "i don't know" in result.lower() or "not mention" in result.lower():
        print("RAG did not return a confident answer. Falling back to live web search...")
        raw_snippets = search_web(query)

        # Summarize
        summary_prompt = f"""
You are an AI assistant. Summarize the following web search results into a clear, concise, and professional paragraph answering the query: '{query}'.

Search Results:
{raw_snippets}
"""
        result = llm.invoke(summary_prompt).content

    # Clean result 
    clean_result = clean_markdown(result.strip())

    subject = "📩 Sustainability Query Response"
    message = f"""📌Query: {query}

🧠Response Summary:

{clean_result}

📬 _This response was generated using our AI assistant, powered by document intelligence and live web search._

Best regards,  
Sustainabot 🤖🌱
"""

    send_email(manager_email, subject, message)
