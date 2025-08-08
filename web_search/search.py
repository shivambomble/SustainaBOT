from langchain_community.tools.tavily_search.tool import TavilySearchResults
from config.config import TAVILY_API_KEY, GROQ_API_KEY
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def search_web(query: str) -> str:
    if not TAVILY_API_KEY:
        return "❌ Tavily API key not found. Please set `TAVILY_API_KEY` in `config/config.py`."

    if not GROQ_API_KEY:
        return "❌ Groq API key not found. Please set `GROQ_API_KEY` in `config/config.py`."

    # Tavily Web Search Tool
    tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
    search_results = tool.invoke({"query": query})

    if not search_results:
        return "No relevant information found from web search."

    # Extract top 3 results
    top_contents = "\n\n".join([res["content"] for res in search_results[:3]])

    # Use Groq's LLaMA3 model
    llm = ChatGroq(
        model="llama3-70b-8192",
        groq_api_key=GROQ_API_KEY,
        temperature=0.7,
    )

    # Prompt template for summarization
    prompt = ChatPromptTemplate.from_template(
        "You are an expert sustainability analyst. Given the following search results, write a concise, domain-relevant summary based on the user's query topic.\n\n"
        "Focus on industry-specific insights, sustainability practices, and real data, avoiding generic suggestions.\n\n"
        "User Query: {query}\n\nSearch Results:\n{results}"
    )

    # Build and invoke summarization chain
    chain = prompt | llm
    summary = chain.invoke({"query": query, "results": top_contents})

    return summary.content.strip()
