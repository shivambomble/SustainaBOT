from langchain_community.tools.tavily_search.tool import TavilySearchResults
from config.config import TAVILY_API_KEY
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def search_web(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Tavily API key not found in config. Please set TAVILY_API_KEY in config/config.py"

    tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
    search_results = tool.invoke({"query": query})

    if not search_results:
        return "No relevant information found from web search."

    # Get the top 3 contents from search results
    top_contents = "\n\n".join([res["content"] for res in search_results[:3]])

    summarizer = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    prompt = ChatPromptTemplate.from_template(
        "You are an expert sustainability analyst. Given the following search results, write a concise, domain-relevant summary (based on the user's query topic). "
        "Focus on industry-specific insights, sustainability practices, and real data, avoiding generic suggestions.\n\n"
        "User Query: {query}\n\nSearch Results:\n{results}"
    )

    chain = prompt | summarizer
    summary = chain.invoke({"query": query, "results": top_contents})

    return summary.content.strip()
