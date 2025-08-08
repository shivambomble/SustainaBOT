import streamlit as st
import datetime
import re
from rag.rag_chain import build_rag_chain
from utils.email_sender import send_email
from web_search.search import search_web
from models.llm import get_llm
from PIL import Image
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from config.config import TAVILY_API_KEY

# Set page config at the very beginning
st.set_page_config(page_title="Sustainabot 🌱", page_icon="🌍")

# Initialize session state for navigation and data persistence
if "page" not in st.session_state:
    st.session_state.page = "home"
    
for key in ["response_generated", "email_phase", "continue_phase", "query", "result"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "response_generated" else None

# Sidebar for all pages
with st.sidebar:
    st.title("🌍 SustainaBOT Menu")
    
    st.markdown("---")
    st.markdown("📘 **About**")
    st.caption("SustainaBOT helps answer questions about sustainability using RAG + Web search + LLM.")

    st.markdown("🔗 [GitHub Repo](https://github.com/shivambomble/SustainaBOT)")  # optional

SUSTAINABILITY_TIPS = [
    "🌿 Tip: Turn off lights and appliances when not in use to reduce energy consumption.",
    "💧 Tip: Fix leaky faucets – one drip per second wastes over 3,000 gallons/year.",
    "♻️ Tip: Recycle electronics responsibly to avoid heavy metal pollution.",
    "🚲 Tip: Walk, cycle, or carpool to reduce your carbon footprint.",
    "🛍️ Tip: Choose reusable bags instead of plastic ones."
]

def show_sustainability_tip():
    st.markdown("### 🌍 Sustainability Tip of the Day")
    index = datetime.datetime.now().day % len(SUSTAINABILITY_TIPS)
    st.info(SUSTAINABILITY_TIPS[index])

def clean_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def get_response(query: str, response_mode: str = "Concise") -> str:
    # Convert response_mode to lowercase to match expected values in build_rag_chain
    rag_chain = build_rag_chain(response_mode=response_mode.lower())
    llm = get_llm()

    response = rag_chain.invoke({"query": query})
    result = response.get("result", "")
    
    # Enhanced fallback detection
    fallback_phrases = [
        "i don't know", 
        "not mention", 
        "out of context", 
        "cannot answer", 
        "no information",
        "this context is about",  # Catches "This context is about Boeing, not Tesla"
        "the question seems to be out of context"
    ]
    
    should_fallback = not result or any(phrase in result.lower() for phrase in fallback_phrases)
    
    if should_fallback:
        st.info("RAG did not return a confident answer. Falling back to live web search...")
        raw_snippets = search_web(query)

        summary_prompt = f"""
You are an AI assistant. {"Summarize the following web search results into a short and clear paragraph" if response_mode == "Concise" else "Provide a detailed and structured explanation"} answering the query: '{query}'.

Search Results:
{raw_snippets}
"""
        result = llm.invoke(summary_prompt).content

    return clean_markdown(result.strip())

def get_renewable_energy_news():
    """Fetch the top 5 news about renewable energy using web search"""
    query = "latest renewable energy news and developments this week"
    llm = get_llm()
    
    with st.spinner("Fetching the latest renewable energy news..."):
        # Use the existing search function to get raw results
        raw_snippets = search_web(query)
        
        # Get the search results with URLs
        tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
        search_results = tool.invoke({"query": query})
        
        # Extract URLs and contents
        news_data = []
        for i, res in enumerate(search_results[:5]):
            news_data.append({
                "content": res["content"],
                "url": res["url"],
                "title": res.get("title", f"News {i+1}")
            })
        
        # Format the data for the LLM
        formatted_data = "\n\n".join([f"Title: {item['title']}\nContent: {item['content']}\nURL: {item['url']}" for item in news_data])
        
        news_prompt = f"""
You are a sustainability news curator. Based on the following search results, create a list of the TOP 5 most important and recent news items about renewable energy and sustainability.

For each news item:
1. Create a clear, informative headline (bold)
2. Write a 2-3 sentence summary of the news
3. Include the approximate date if available
4. Include the source URL at the end of each item
5. Format as a numbered list with emoji indicators

Search Results:
{formatted_data}
"""
        
        news_content = llm.invoke(news_prompt).content
        
        # Process the LLM response to ensure URLs are clickable
        processed_content = news_content
        
        # Return both the processed content and the raw news data for display
        return processed_content, news_data

# ------------------------ Home Page (Landing Page) ------------------------
def show_home_page():
    st.title("♻️ SustainaBOT - Environmental Intelligence")
    st.subheader("Your AI-powered sustainability assistant")
    
    show_sustainability_tip()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📰 Renewable Energy News")
        st.write("Stay updated with the latest developments in renewable energy and sustainability.")
        if st.button("Read Latest News", key="news_btn", use_container_width=True):
            st.session_state.page = "news"
            st.rerun()
    
    with col2:
        st.markdown("### 💬 Chat with SustainaBOT")
        st.write("Ask questions about sustainability, climate change, and environmental practices.")
        if st.button("Start Chatting", key="chat_btn", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    
    st.markdown("---")
    
    with st.expander("📊 View Global CO₂ Emissions Graphs"):
        image1 = Image.open("images/annual_co2_emissions.png")
        st.image(image1, caption="Annual Global CO₂ Emissions Over Time", use_container_width=True)

        image2 = Image.open("images/annual_co2_by_region.png")
        st.image(image2, caption="Annual CO₂ Emissions by World Region", use_container_width=True)

# ------------------------ News Page ------------------------
def show_news_page():
    st.title("📰 Renewable Energy News")
    st.subheader("Top 5 Latest Developments in Renewable Energy")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Check if we have cached news or need to fetch new ones
    if "news_content" not in st.session_state or "news_data" not in st.session_state or st.button("🔄 Refresh News"):
        st.session_state.news_content, st.session_state.news_data = get_renewable_energy_news()
    
    # Display the formatted news content
    st.markdown(st.session_state.news_content)
    
    # Add "Read more" links after each news item
    st.markdown("---")
    st.subheader("📎 Original Sources")
    
    for i, item in enumerate(st.session_state.news_data):
        st.markdown(f"**{i+1}. [{item['title']}]({item['url']})**")
        st.markdown(f"[Click here to read more]({item['url']})")
        st.markdown("---")

# ------------------------ Chat Page (Original App) ------------------------
def show_chat_page():
    st.title("♻️ SustainaBOT - Environmental Q&A Assistant")
    st.caption("Ask your sustainability and climate questions!")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    show_sustainability_tip()

    query = st.text_input("🔍 Enter your question")
    response_mode = st.radio("Select Response Style:", ["Concise", "Detailed"])

    # Generate Answer
    if st.button("Get Answer"):
        if query.strip():
            with st.spinner("Generating response..."):
                answer = get_response(query, response_mode)
                st.session_state.query = query
                st.session_state.result = answer
                st.session_state.response_generated = True
                st.session_state.email_phase = False
                st.session_state.continue_phase = False
                st.success("✅ Here's the answer:")
                st.markdown(answer)
        else:
            st.warning("Please enter a question to continue.")

    # Offer to Send Email
    if st.session_state.response_generated and not st.session_state.email_phase and not st.session_state.continue_phase:
        send_mail = st.radio("📨 Would you like to email this response to a teammate or coworker?", ["Yes", "No"], index=None)
        if send_mail == "Yes":
            st.session_state.email_phase = True
        elif send_mail == "No":
            st.session_state.continue_phase = True

    # Email Form
    if st.session_state.email_phase and not st.session_state.continue_phase:
        manager_email = st.text_input("📧 Enter your teammate's email address:")
        if st.button("Send Email"):
            if not manager_email:
                st.error("Please enter a valid email address.")
            else:
                subject = "Sustainability Query Response from SustainaBOT"
                message = f"""📌 Query: {st.session_state.query}

🧠 Response Summary:

{st.session_state.result}

📬 _This response was generated using SustainaBOT, powered by AI and real-time data._

Best regards,  
SustainaBOT 🤖🌱
"""
                send_email(manager_email, subject, message)
                st.success(f"📧 Response sent to {manager_email}")
                st.session_state.continue_phase = True

# ------------------------ Main App Logic ------------------------
# Route to the appropriate page based on session state
if st.session_state.page == "home":
    show_home_page()
elif st.session_state.page == "news":
    show_news_page()
elif st.session_state.page == "chat":
    show_chat_page()
