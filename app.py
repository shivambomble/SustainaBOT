import streamlit as st
import datetime
import re
from rag.rag_chain import build_rag_chain
from utils.email_sender import send_email
from web_search.search import search_web
from models.llm import get_llm
import streamlit as st
from PIL import Image

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
    rag_chain = build_rag_chain()
    llm = get_llm()

    response = rag_chain.invoke({"query": query})
    result = response.get("result", "")

    if not result or "i don't know" in result.lower() or "not mention" in result.lower():
        st.info("RAG did not return a confident answer. Falling back to live web search...")
        raw_snippets = search_web(query)

        if response_mode == "Concise":
            summary_prompt = f"""
You are an AI assistant. Summarize the following web search results into a **short and clear paragraph** answering the query: '{query}'.

Search Results:
{raw_snippets}
"""
        else:
            summary_prompt = f"""
You are an AI assistant. Provide a **detailed and structured explanation** answering the query: '{query}' using the web search results.

Search Results:
{raw_snippets}
"""
        result = llm.invoke(summary_prompt).content

    return clean_markdown(result.strip())

# ------------------------ Streamlit UI ------------------------

st.set_page_config(page_title="Sustainabot 🌱", page_icon="🌍")
st.title("♻️ SustainaBOT - Environmental Q&A Assistant")
st.caption("Ask your sustainability and climate questions!")

show_sustainability_tip()

# Initialize session state
for key in ["response_generated", "email_phase", "continue_phase", "query", "result"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "response_generated" else None

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

with st.expander("📊 View Global CO₂ Emissions Graphs"):
    image1 = Image.open("images/annual_co2_emissions.png")
    st.image(image1, caption="Annual Global CO₂ Emissions Over Time", use_container_width=True)

    image2 = Image.open("images/annual_co2_by_region.png")
    st.image(image2, caption="Annual CO₂ Emissions by World Region", use_container_width=True)
