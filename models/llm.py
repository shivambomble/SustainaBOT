from langchain_groq import ChatGroq
from config.config import GROQ_API_KEY

def get_llm():
    llm = ChatGroq(
        model="llama3-70b-8192",
        groq_api_key=GROQ_API_KEY,
        temperature=0.7
    )
    return llm
