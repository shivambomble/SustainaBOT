import streamlit as st
import datetime
import re
import sys
from rag.rag_chain import build_rag_chain
from utils.email_sender import send_email
from utils.news_export import export_news_to_json, export_news_to_markdown, create_news_digest_email
from web_search.search import search_web
from models.llm import get_llm
from PIL import Image
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from config.config_template import TAVILY_API_KEY

# Set page config at the very beginning
st.set_page_config(page_title="Sustainabot 🌱", page_icon="🌍")

# Initialize session state for navigation and data persistence
if "page" not in st.session_state:
    st.session_state.page = "home"

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_response_mode" not in st.session_state:
    st.session_state.current_response_mode = "Concise"
    
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
    # Use override if available, otherwise use day-based index
    if "tip_override" in st.session_state:
        index = st.session_state.tip_override
    else:
        index = datetime.datetime.now().day % len(SUSTAINABILITY_TIPS)
    
    tip_content = SUSTAINABILITY_TIPS[index]
    st.info(tip_content)

def clean_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def get_sustainability_suggestions() -> list:
    """Get random sustainability question suggestions"""
    suggestions = [
        "What are the environmental benefits of solar energy?",
        "How can businesses reduce their carbon footprint?",
        "What is the difference between renewable and non-renewable energy?",
        "How do electric vehicles compare to traditional cars environmentally?",
        "What are the latest developments in wind energy technology?",
        "How does recycling help the environment?",
        "What is carbon neutrality and how can it be achieved?",
        "What are the environmental impacts of fast fashion?",
        "How can smart grids improve energy efficiency?",
        "What role do forests play in climate change mitigation?",
        "How does sustainable agriculture benefit the environment?",
        "What are the challenges facing renewable energy adoption?",
        "How can cities become more sustainable?",
        "What is the circular economy and why is it important?",
        "How do green buildings reduce environmental impact?"
    ]
    
    import random
    return random.sample(suggestions, 3)

def is_sustainability_related(query: str) -> bool:
    """Check if the query is related to sustainability, environment, or energy domains"""
    
    # Define sustainability-related keywords and phrases
    sustainability_keywords = [
        # Energy & Power
        "renewable energy", "solar", "wind", "hydroelectric", "geothermal", "nuclear", 
        "fossil fuel", "coal", "oil", "gas", "electricity", "power", "energy storage",
        "battery", "grid", "smart grid", "energy efficiency", "biomass", "biofuel",
        
        # Environment & Climate
        "climate change", "global warming", "greenhouse gas", "carbon", "co2", "emission",
        "pollution", "air quality", "water quality", "deforestation", "biodiversity",
        "ecosystem", "conservation", "wildlife", "ocean", "atmosphere", "ozone",
        
        # Sustainability Practices
        "sustainability", "sustainable", "green", "eco-friendly", "environmental",
        "recycling", "waste management", "circular economy", "carbon footprint",
        "life cycle", "esg", "environmental impact", "sustainable development",
        
        # Transportation
        "electric vehicle", "ev", "hybrid", "public transport", "carbon neutral",
        "fuel efficiency", "alternative fuel", "hydrogen", "electric car",
        
        # Agriculture & Food
        "sustainable agriculture", "organic farming", "food security", "water conservation",
        "sustainable food", "plant-based", "carbon farming", "regenerative agriculture",
        
        # Business & Policy
        "green technology", "clean tech", "environmental policy", "carbon tax",
        "renewable portfolio", "net zero", "carbon neutral", "sustainability report",
        "green investment", "climate finance", "environmental regulation"
    ]
    
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Check if any sustainability keywords are present
    for keyword in sustainability_keywords:
        if keyword in query_lower:
            return True
    
    # Additional check using LLM for more nuanced domain detection
    llm = get_llm()
    
    domain_check_prompt = f"""
You are a domain classifier. Determine if the following question is related to sustainability, environmental issues, climate change, renewable energy, or green technology.

Question: "{query}"

Respond with only "YES" if the question is related to sustainability/environment/energy domains, or "NO" if it's not related.

Examples:
- "What is solar energy?" -> YES
- "How to reduce carbon footprint?" -> YES  
- "What is the weather today?" -> NO
- "How to cook pasta?" -> NO
- "Tell me about electric vehicles" -> YES
- "What is machine learning?" -> NO

Response:"""
    
    try:
        domain_response = llm.invoke(domain_check_prompt).content.strip().upper()
        return domain_response == "YES"
    except:
        # Fallback to keyword-based detection if LLM fails
        return False

def get_response(query: str, response_mode: str = "Concise") -> str:
    # First, check if the query is related to sustainability domain
    if not is_sustainability_related(query):
        suggestions = get_sustainability_suggestions()
        
        return f"""
🌱 **SustainaBOT Domain Focus**

I'm specifically designed to help with sustainability, environmental, and energy-related questions. 

**I can help you with:**
• ♻️ Sustainability practices and green living
• 🌍 Climate change and environmental issues  
• ⚡ Renewable energy (solar, wind, hydro, etc.)
• 🔋 Energy storage and efficiency
• � Enlectric vehicles and clean transportation
• 🏭 Corporate sustainability and ESG
• 📋 Environmental policies and regulations
• 💰 Green investments and clean technology

**Here are some questions you could ask me:**

1. "{suggestions[0]}"
2. "{suggestions[1]}"
3. "{suggestions[2]}"

**Please ask me something related to sustainability, environment, or energy topics!**
"""
    
    llm = get_llm()
    result = ""
    
    # Try RAG first, with fallback to web search
    try:
        # Convert response_mode to lowercase to match expected values in build_rag_chain
        rag_chain = build_rag_chain(response_mode=response_mode.lower())
        
        # Check if RAG chain was successfully built
        if rag_chain is None:
            print("⚠️ RAG chain could not be built - vector store unavailable")
            raise ValueError("Vector store unavailable, falling back to web search")
        
        response = rag_chain.invoke({"query": query})
        result = response.get("result", "")
        print("✅ RAG response generated successfully")
        
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
            raise ValueError("RAG response not meaningful, falling back to web search")
            
    except Exception as rag_error:
        print(f"⚠️ RAG failed: {str(rag_error)}")
        
        # Show user-friendly message for vector store issues
        if "vector store" in str(rag_error).lower() or "no documents" in str(rag_error).lower():
            st.info("📚 Knowledge base is being initialized. Using web search for your query...")
        else:
            st.info("RAG did not return a confident answer. Falling back to live web search...")
        
        # Fall back to web search
        try:
            raw_snippets = search_web(query)
            summary_prompt = f"""
You are SustainaBOT, an AI assistant specialized in sustainability, environmental issues, and renewable energy. {"Summarize the following web search results into a short and clear paragraph" if response_mode == "Concise" else "Provide a detailed and structured explanation"} answering the sustainability/environmental query: '{query}'.

Focus only on sustainability, environmental, and energy-related aspects. If the search results don't contain relevant sustainability information, politely redirect the user to ask sustainability-related questions.

Search Results:
{raw_snippets}
"""
            result = llm.invoke(summary_prompt).content
            print("✅ Web search fallback successful")
        except Exception as web_error:
            print(f"❌ Web search also failed: {str(web_error)}")
            return f"I apologize, but I'm unable to process your query at the moment due to technical issues. Please try again later."

    return clean_markdown(result.strip())

def test_tavily_connection():
    """Test if Tavily API is working correctly"""
    try:
        tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
        test_results = tool.invoke({"query": "renewable energy"})
        return True, test_results
    except Exception as e:
        return False, str(e)

def get_renewable_energy_news(category="general", num_articles=5):
    """Fetch renewable energy news with category filtering"""
    
    # Define search queries for different categories
    search_queries = {
        "general": "latest renewable energy news developments 2024 2025",
        "solar": "solar energy news developments photovoltaic panels 2024 2025",
        "wind": "wind energy news turbines offshore onshore 2024 2025", 
        "hydro": "hydroelectric power news dam renewable water energy 2024 2025",
        "geothermal": "geothermal energy news power plants renewable 2024 2025",
        "battery": "battery storage energy news lithium renewable grid 2024 2025",
        "policy": "renewable energy policy government legislation climate 2024 2025",
        "investment": "renewable energy investment funding venture capital 2024 2025"
    }
    
    query = search_queries.get(category, search_queries["general"])
    llm = get_llm()
    
    with st.spinner(f"Fetching the latest {category} renewable energy news..."):
        try:
            # Get the search results with URLs
            tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY)
            search_results = tool.invoke({"query": query})
            
            # Debug: Log the type and structure of search results (remove in production)
            # st.write(f"Debug: Search results type: {type(search_results)}")
            # st.write(f"Debug: Search results length: {len(search_results) if hasattr(search_results, '__len__') else 'N/A'}")
            
            # Validate and normalize search results structure
            if not search_results:
                raise ValueError("No search results returned")
            
            # Handle different possible return formats
            if isinstance(search_results, dict):
                # If it's a dict, look for common keys that might contain the results
                if "results" in search_results:
                    search_results = search_results["results"]
                elif "data" in search_results:
                    search_results = search_results["data"]
                else:
                    # Convert single result dict to list
                    search_results = [search_results]
            
            if not isinstance(search_results, list):
                raise ValueError("Invalid search results format")
            
            # Extract URLs and contents with proper validation
            news_data = []
            for i, res in enumerate(search_results[:num_articles]):
                # Ensure res is a dictionary and has required fields
                if not isinstance(res, dict):
                    continue
                
                # Extract data with fallbacks
                content = res.get("content", "No content available")
                url = res.get("url", "#")
                title = res.get("title", f"News Article {i+1}")
                
                # Only add if we have meaningful content
                if content and content != "No content available" and url != "#":
                    news_data.append({
                        "content": content,
                        "url": url,
                        "title": title,
                        "category": category
                    })
            
            # Check if we got any valid news data
            if not news_data:
                raise ValueError("No valid news articles found")
            
            # Format the data for the LLM
            formatted_data = "\n\n".join([f"Title: {item['title']}\nContent: {item['content']}\nURL: {item['url']}" for item in news_data])
            
            category_emoji = {
                "general": "🌱", "solar": "☀️", "wind": "💨", "hydro": "💧",
                "geothermal": "🌋", "battery": "🔋", "policy": "📋", "investment": "💰"
            }
            
            news_prompt = f"""
You are a sustainability news curator specializing in {category} renewable energy. Based on the following search results, create a list of the TOP {num_articles} most important and recent news items.

For each news item:
1. Create a clear, informative headline with {category_emoji.get(category, '🌱')} emoji
2. Write a 2-3 sentence summary highlighting key impacts and developments
3. Include approximate date if available (look for recent dates in content)
4. Add relevance score (High/Medium/Low impact)
5. Format as a numbered list

Search Results:
{formatted_data}
"""
            
            news_content = llm.invoke(news_prompt).content
            
            return news_content, news_data
            
        except Exception as e:
            error_msg = str(e)
            
            # Provide more specific error messages
            if "string indices must be integers" in error_msg:
                st.error("🔧 API response format issue. The news service returned unexpected data format.")
            elif "No valid news articles found" in error_msg:
                st.warning("📰 No news articles found for this category. Try refreshing or selecting a different category.")
            elif "Invalid search results format" in error_msg:
                st.error("🌐 Search service returned invalid data. Please try again in a moment.")
            elif "tavily" in error_msg.lower():
                st.error("🔑 News search service issue. Please check your API configuration.")
            else:
                st.error(f"❌ Error fetching news: {error_msg}")
            
            return "Unable to fetch news at this time. Please try again later.", []

def get_news_summary_stats(news_data):
    """Generate summary statistics for news data"""
    if not news_data:
        return {}
    
    return {
        "total_articles": len(news_data),
        "sources": len(set([item['url'].split('/')[2] for item in news_data if 'url' in item])),
        "avg_content_length": sum(len(item.get('content', '')) for item in news_data) // len(news_data)
    }



# ------------------------ Home Page (Landing Page) ------------------------
def show_home_page():
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2E8B57; font-size: 3rem; margin-bottom: 0.5rem;">
            🌍 SustainaBOT
        </h1>
        <h2 style="color: #4682B4; font-size: 1.5rem; font-weight: 300;">
            Your AI-Powered Environmental Intelligence Assistant
        </h2>
        <p style="font-size: 1.1rem; color: #666; margin-top: 1rem;">
            Combining RAG technology, real-time web search, and expert knowledge to answer your sustainability questions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Dashboard
    st.markdown("### 📊 Platform Overview")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        chat_count = len(st.session_state.get("chat_history", []))
        st.metric("💬 Chat Sessions", chat_count, delta="Active conversations")
    
    with col_stat2:
        saved_articles = len(st.session_state.get("saved_articles", []))
        st.metric("📰 Saved Articles", saved_articles, delta="Your collection")
    
    with col_stat3:
        # Count cached news categories
        cached_news = sum(1 for key in st.session_state.keys() if key.startswith("news_"))
        st.metric("🗂️ News Categories", "8", delta=f"{cached_news} cached")
    
    with col_stat4:
        current_time = datetime.datetime.now()
        st.metric("🕒 Current Time", current_time.strftime("%H:%M"), delta=current_time.strftime("%Y-%m-%d"))
    
    st.markdown("---")
    
    # Daily Sustainability Tip (Enhanced)
    st.markdown("### 🌱 Today's Sustainability Insight")
    tip_col, action_col = st.columns([3, 1])
    
    with tip_col:
        show_sustainability_tip()
    
    with action_col:
        st.markdown("**Quick Actions:**")
        if st.button("🔄 New Tip", key="new_tip"):
            # Force a different tip by changing the index
            st.session_state.tip_override = (datetime.datetime.now().second % len(SUSTAINABILITY_TIPS))
            st.rerun()
        
        if st.button("📧 Email Tip", key="email_tip"):
            st.session_state.show_tip_email = True
    
    # Email tip form
    if st.session_state.get("show_tip_email", False):
        with st.expander("📧 Email Today's Tip", expanded=True):
            tip_email = st.text_input("Enter email address:")
            col_send_tip, col_cancel_tip = st.columns(2)
            
            with col_send_tip:
                if st.button("Send Tip"):
                    if tip_email:
                        tip_index = st.session_state.get("tip_override", datetime.datetime.now().day % len(SUSTAINABILITY_TIPS))
                        tip_content = SUSTAINABILITY_TIPS[tip_index]
                        
                        subject = "🌱 Daily Sustainability Tip from SustainaBOT"
                        message = f"""
🌍 Daily Sustainability Tip

{tip_content}

💡 Small actions lead to big changes! Start implementing this tip today.

🤖 Generated by SustainaBOT - Your Environmental Intelligence Assistant
🌱 Stay sustainable, stay informed!
"""
                        send_email(tip_email, subject, message)
                        st.success(f"📧 Tip sent to {tip_email}")
                        st.session_state.show_tip_email = False
                        st.rerun()
                    else:
                        st.error("Please enter a valid email address.")
            
            with col_cancel_tip:
                if st.button("Cancel"):
                    st.session_state.show_tip_email = False
                    st.rerun()
    
    st.markdown("---")
    
    # Main Feature Cards
    st.markdown("### 🚀 Explore SustainaBOT Features")
    
    # Enhanced feature cards with more details
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e8 100%);">
                <h3 style="color: #2E7D32; margin-top: 0;">📰 Renewable Energy News Hub</h3>
                <p style="color: #424242;">Stay informed with curated news across 8 specialized categories</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("**🎯 Features:**")
        st.markdown("• ☀️ Solar • 💨 Wind • 💧 Hydro • 🔋 Storage")
        st.markdown("• 📋 Policy • 💰 Investment • 🌋 Geothermal")
        st.markdown("• 📤 Export options • 📧 Email digests")
        
        if st.button("🚀 Explore News Hub", key="news_btn", use_container_width=True):
            st.session_state.page = "news"
            st.rerun()
        
        # Show quick news preview if available
        if "news_general_5" in st.session_state:
            with st.expander("📰 Latest Headlines Preview"):
                _, preview_data = st.session_state["news_general_5"]
                for i, item in enumerate(preview_data[:3]):
                    st.markdown(f"• {item['title'][:60]}...")
                st.caption("Click 'Explore News Hub' for full articles")
    
    with col2:
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #2196F3; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #f0f7ff 0%, #e3f2fd 100%);">
                <h3 style="color: #1565C0; margin-top: 0;">💬 AI Chat Assistant</h3>
                <p style="color: #424242;">Get expert answers on sustainability, climate change, and environmental practices</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat features
        st.markdown("**🎯 Capabilities:**")
        st.markdown("• 🧠 RAG-powered responses")
        st.markdown("• 🌐 Real-time web search fallback")
        st.markdown("• 📝 Conversation history")
        st.markdown("• 📧 Share responses via email")
        
        if st.button("💬 Start Chatting", key="chat_btn", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
        
        # Show suggested questions on home page
        st.markdown("**💡 Try these questions:**")
        home_suggestions = get_sustainability_suggestions()
        
        for i, suggestion in enumerate(home_suggestions):
            if st.button(f"💬 {suggestion[:50]}...", key=f"home_sug_{i}", use_container_width=True):
                # Navigate to chat and add the question
                st.session_state.page = "chat"
                st.session_state.pending_question = suggestion
                st.rerun()
        
        # Show recent chat preview
        if st.session_state.get("chat_history"):
            with st.expander("💭 Recent Conversations"):
                recent_chats = st.session_state.chat_history[-3:]
                for chat in recent_chats:
                    st.markdown(f"• Q: {chat['question'][:50]}...")
                st.caption("Continue your conversations in the chat section")
    
    st.markdown("---")
    
    # Quick Actions Section
    st.markdown("### ⚡ Quick Actions")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("🔍 Ask Quick Question", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    
    with quick_col2:
        if st.button("📈 Latest Solar News", use_container_width=True):
            st.session_state.page = "news"
            # Set default category to solar
            st.session_state.default_news_category = "solar"
            st.rerun()
    
    with quick_col3:
        if st.button("💨 Wind Energy Updates", use_container_width=True):
            st.session_state.page = "news"
            st.session_state.default_news_category = "wind"
            st.rerun()
    
    with quick_col4:
        if st.button("🔋 Battery Storage News", use_container_width=True):
            st.session_state.page = "news"
            st.session_state.default_news_category = "battery"
            st.rerun()
    
    st.markdown("---")
    
    # Data Visualization Section (Enhanced)
    st.markdown("### 📊 Environmental Data Insights")
    
    viz_col1, viz_col2 = st.columns([2, 1])
    
    with viz_col1:
        with st.expander("📈 Global CO₂ Emissions Analysis", expanded=False):
            st.markdown("**Explore comprehensive climate data visualizations:**")
            
            tab1, tab2 = st.tabs(["📅 Annual Trends", "🌍 Regional Analysis"])
            
            with tab1:
                try:
                    image1 = Image.open("images/annual_co2_emissions.png")
                    st.image(image1, caption="Annual Global CO₂ Emissions Over Time", use_container_width=True)
                    st.markdown("**Key Insights:** Track global emission trends and identify critical periods of change.")
                except:
                    st.warning("📊 CO₂ emissions chart not available")
            
            with tab2:
                try:
                    image2 = Image.open("images/annual_co2_by_region.png")
                    st.image(image2, caption="Annual CO₂ Emissions by World Region", use_container_width=True)
                    st.markdown("**Key Insights:** Compare regional contributions to global emissions.")
                except:
                    st.warning("🌍 Regional emissions chart not available")
    
    with viz_col2:
        st.markdown("**📊 Data Sources:**")
        st.markdown("• Global Carbon Atlas")
        st.markdown("• IPCC Reports")
        st.markdown("• National Inventories")
        st.markdown("• Satellite Observations")
        
        st.markdown("**🎯 Use Cases:**")
        st.markdown("• Research & Analysis")
        st.markdown("• Policy Development")
        st.markdown("• Educational Content")
        st.markdown("• Trend Monitoring")
    
    # Footer with additional info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>🌱 SustainaBOT</strong> - Empowering sustainable decisions through AI-driven insights</p>
        <p>Built with ❤️ for a greener future | Powered by RAG, LLM, and real-time data</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------ Enhanced News Page ------------------------
def show_news_page():
    st.title("📰 Renewable Energy News Hub")
    st.subheader("Stay updated with the latest developments in clean energy")
    
    # Top navigation bar
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (5min)", value=False)
    
    with col3:
        if st.button("📧 Subscribe"):
            st.info("Newsletter feature coming soon!")
    
    st.markdown("---")
    
    # News controls and filters
    col_cat, col_num, col_refresh = st.columns([2, 1, 1])
    
    with col_cat:
        # Check if there's a default category from home page
        default_category = st.session_state.get("default_news_category", "general")
        category_options = ["general", "solar", "wind", "hydro", "geothermal", "battery", "policy", "investment"]
        default_index = category_options.index(default_category) if default_category in category_options else 0
        
        category = st.selectbox(
            "📂 Select Category:",
            category_options,
            index=default_index,
            format_func=lambda x: {
                "general": "🌱 General News",
                "solar": "☀️ Solar Energy", 
                "wind": "💨 Wind Power",
                "hydro": "💧 Hydroelectric",
                "geothermal": "🌋 Geothermal",
                "battery": "🔋 Energy Storage",
                "policy": "📋 Policy & Regulation",
                "investment": "💰 Investment & Finance"
            }[x]
        )
        
        # Clear the default category after first use
        if "default_news_category" in st.session_state:
            del st.session_state.default_news_category
    
    with col_num:
        num_articles = st.selectbox("📊 Articles:", [3, 5, 8, 10], index=1)
    
    with col_refresh:
        refresh_clicked = st.button("🔄 Refresh News")
    
    # Add diagnostic section (can be removed in production)
    if st.checkbox("🔧 Show Diagnostics", value=False):
        st.markdown("**API Diagnostics:**")
        
        # Show environment info
        st.markdown("**Environment Information:**")
        st.write(f"- Python version: {sys.version}")
        st.write(f"- Streamlit running locally: {'Yes' if 'localhost' in st.get_option('browser.serverAddress') or '127.0.0.1' in st.get_option('browser.serverAddress') else 'No (Cloud deployment)'}")
        
        # API Key diagnostics
        tavily_key_status = "✅ Set" if TAVILY_API_KEY and TAVILY_API_KEY != 'your_tavily_api_key_here' else "❌ Not configured"
        st.markdown(f"**Tavily API Key Status:** {tavily_key_status}")
        
        if TAVILY_API_KEY and TAVILY_API_KEY != 'your_tavily_api_key_here':
            st.write(f"- Key length: {len(TAVILY_API_KEY)} characters")
            st.write(f"- Key starts with: {TAVILY_API_KEY[:8]}...")
        else:
            st.error("🔑 Tavily API key is not properly configured!")
            st.markdown("""
            **To fix this on Streamlit Cloud:**
            1. Go to your app settings on Streamlit Cloud
            2. Add environment variables in the 'Secrets' section:
            ```
            TAVILY_API_KEY = "your_actual_api_key_here"
            ```
            """)
        
        if st.button("Test Tavily Connection"):
            with st.spinner("Testing Tavily API..."):
                is_working, result = test_tavily_connection()
                
                if is_working:
                    st.success("✅ Tavily API is working correctly")
                    st.write(f"Result type: {type(result)}")
                    if isinstance(result, list) and len(result) > 0:
                        st.write(f"First result keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'Not a dict'}")
                        st.write(f"Number of results: {len(result)}")
                    elif isinstance(result, dict):
                        st.write(f"Result keys: {list(result.keys())}")
                else:
                    st.error(f"❌ Tavily API Error: {result}")
                    if "authentication" in str(result).lower() or "api key" in str(result).lower():
                        st.warning("This looks like an API key authentication issue!")
        
        # Environment variables check
        st.markdown("**Environment Variables Check:**")
        import os
        env_vars = ['TAVILY_API_KEY', 'GROQ_API_KEY', 'SMTP_EMAIL', 'SMTP_PASSWORD']
        for var in env_vars:
            value = os.getenv(var)
            if value and value != f'your_{var.lower()}_here':
                st.write(f"✅ {var}: Set ({len(value)} chars)")
            else:
                st.write(f"❌ {var}: Not set or using default value")
    
    # Initialize session state for news caching
    cache_key = f"news_{category}_{num_articles}"
    cache_time_key = f"news_time_{category}_{num_articles}"
    
    # Check if we need to fetch new news (cache for 5 minutes)
    should_fetch = (
        cache_key not in st.session_state or 
        cache_time_key not in st.session_state or
        refresh_clicked or
        (datetime.datetime.now() - st.session_state.get(cache_time_key, datetime.datetime.min)).seconds > 300
    )
    
    if should_fetch:
        with st.spinner(f"Fetching latest {category} news..."):
            news_content, news_data = get_renewable_energy_news(category, num_articles)
            st.session_state[cache_key] = (news_content, news_data)
            st.session_state[cache_time_key] = datetime.datetime.now()
    else:
        news_content, news_data = st.session_state[cache_key]
    
    # News statistics
    if news_data:
        stats = get_news_summary_stats(news_data)
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("📰 Articles", stats.get('total_articles', 0))
        with col_stat2:
            st.metric("🌐 Sources", stats.get('sources', 0))
        with col_stat3:
            st.metric("🕒 Last Updated", 
                     st.session_state.get(cache_time_key, datetime.datetime.now()).strftime("%H:%M"))
        with col_stat4:
            st.metric("📂 Category", category.title())
    
    st.markdown("---")
    
    # Main news content
    if news_content and news_data:
        # Display the formatted news content
        st.markdown(news_content)
        
        st.markdown("---")
        
        # Enhanced news cards
        st.subheader("📎 Detailed News Cards")
        
        for i, item in enumerate(news_data):
            with st.expander(f"📰 {item['title']}", expanded=False):
                col_content, col_actions = st.columns([3, 1])
                
                with col_content:
                    st.markdown(f"**Summary:** {item['content'][:300]}...")
                    st.markdown(f"**Source:** {item['url'].split('/')[2]}")
                
                with col_actions:
                    st.markdown("**Actions:**")
                    if st.button(f"🔗 Read Full Article", key=f"read_{i}"):
                        st.markdown(f"[Open Article]({item['url']})")
                    
                    if st.button(f"📧 Share", key=f"share_{i}"):
                        st.text_area(f"Share this article:", 
                                   f"Check out this renewable energy news: {item['title']}\n{item['url']}", 
                                   key=f"share_text_{i}")
                    
                    if st.button(f"💾 Save", key=f"save_{i}"):
                        if "saved_articles" not in st.session_state:
                            st.session_state.saved_articles = []
                        st.session_state.saved_articles.append(item)
                        st.success("Article saved!")
        
        # Export and sharing options
        st.markdown("---")
        st.subheader("📤 Export & Share")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("📄 Export as Markdown"):
                markdown_content = export_news_to_markdown(news_data, category)
                st.download_button(
                    label="⬇️ Download Markdown",
                    data=markdown_content,
                    file_name=f"renewable_news_{category}_{datetime.datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
        
        with col_export2:
            if st.button("📊 Export as JSON"):
                json_content = export_news_to_json(news_data, category)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_content,
                    file_name=f"renewable_news_{category}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col_export3:
            if st.button("📧 Email Digest"):
                st.session_state.show_email_digest = True
        
        # Email digest form
        if st.session_state.get("show_email_digest", False):
            with st.expander("📧 Send News Digest", expanded=True):
                digest_email = st.text_input("Enter email address for digest:")
                
                col_send_digest, col_cancel_digest = st.columns(2)
                with col_send_digest:
                    if st.button("Send Digest"):
                        if digest_email:
                            email_content = create_news_digest_email(news_data, category)
                            send_email(digest_email, email_content["subject"], email_content["body"])
                            st.success(f"📧 News digest sent to {digest_email}")
                            st.session_state.show_email_digest = False
                            st.rerun()
                        else:
                            st.error("Please enter a valid email address.")
                
                with col_cancel_digest:
                    if st.button("Cancel Digest"):
                        st.session_state.show_email_digest = False
                        st.rerun()
        
        # Saved articles section
        if "saved_articles" in st.session_state and st.session_state.saved_articles:
            st.markdown("---")
            st.subheader("💾 Saved Articles")
            
            col_saved_header, col_clear_all = st.columns([3, 1])
            with col_clear_all:
                if st.button("🗑️ Clear All"):
                    st.session_state.saved_articles = []
                    st.rerun()
            
            for i, saved_item in enumerate(st.session_state.saved_articles):
                col_saved, col_remove = st.columns([4, 1])
                with col_saved:
                    st.markdown(f"• [{saved_item['title']}]({saved_item['url']})")
                with col_remove:
                    if st.button("🗑️", key=f"remove_saved_{i}"):
                        st.session_state.saved_articles.pop(i)
                        st.rerun()
    
    else:
        st.error("Unable to fetch news at this time. Please try again later.")
    
    # Auto-refresh functionality
    if auto_refresh:
        import time
        time.sleep(300)  # 5 minutes
        st.rerun()

# ------------------------ Chat Page (Continuous Chat) ------------------------
def show_chat_page():
    st.title("♻️ SustainaBOT - Environmental Q&A Assistant")
    st.caption("Ask your sustainability and climate questions!")
    
    # Handle pending question from home page
    if "pending_question" in st.session_state:
        pending_q = st.session_state.pending_question
        del st.session_state.pending_question
        
        # Automatically process the pending question
        with st.spinner("🤔 Thinking..."):
            answer = get_response(pending_q, st.session_state.current_response_mode)
            chat_entry = {
                "question": pending_q,
                "answer": answer,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "response_mode": st.session_state.current_response_mode
            }
            st.session_state.chat_history.append(chat_entry)
    
    # Top navigation and controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        response_mode = st.selectbox("Response Style:", ["Concise", "Detailed"], 
                                   index=0 if st.session_state.current_response_mode == "Concise" else 1)
        st.session_state.current_response_mode = response_mode
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        
        # Create a container for chat messages with scrolling
        chat_container = st.container()
        
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                # User message
                with st.chat_message("user"):
                    st.write(f"**Q:** {chat['question']}")
                
                # Bot response
                with st.chat_message("assistant"):
                    st.write(f"**A:** {chat['answer']}")
                    
                    # Email option for each response
                    email_key = f"email_{i}"
                    if email_key not in st.session_state:
                        st.session_state[email_key] = False
                    
                    col_email, col_timestamp = st.columns([3, 1])
                    with col_email:
                        if st.button(f"📧 Email this response", key=f"email_btn_{i}"):
                            st.session_state[email_key] = True
                    
                    with col_timestamp:
                        st.caption(f"🕒 {chat['timestamp']}")
                    
                    # Email form for this specific response
                    if st.session_state[email_key]:
                        with st.expander("📧 Send Email", expanded=True):
                            manager_email = st.text_input(f"Enter email address:", key=f"email_input_{i}")
                            
                            col_send, col_cancel = st.columns(2)
                            with col_send:
                                if st.button("Send", key=f"send_{i}"):
                                    if manager_email:
                                        subject = "Sustainability Query Response from SustainaBOT"
                                        message = f"""📌 Query: {chat['question']}

🧠 Response Summary:

{chat['answer']}

📬 _This response was generated using SustainaBOT, powered by AI and real-time data._

Best regards,  
SustainaBOT 🤖🌱
"""
                                        send_email(manager_email, subject, message)
                                        st.success(f"📧 Response sent to {manager_email}")
                                        st.session_state[email_key] = False
                                        st.rerun()
                                    else:
                                        st.error("Please enter a valid email address.")
                            
                            with col_cancel:
                                if st.button("Cancel", key=f"cancel_{i}"):
                                    st.session_state[email_key] = False
                                    st.rerun()
                
                st.markdown("---")
    
    else:
        show_sustainability_tip()
        st.info("👋 Start a conversation by asking your first sustainability question below!")
        
        # Show suggested questions for new users
        st.markdown("### 💡 Suggested Questions")
        suggestions = get_sustainability_suggestions()
        
        col_sug1, col_sug2, col_sug3 = st.columns(3)
        
        with col_sug1:
            if st.button(f"💬 {suggestions[0][:30]}...", key="sug1", use_container_width=True):
                # Add suggestion to chat history
                with st.spinner("🤔 Thinking..."):
                    answer = get_response(suggestions[0], st.session_state.current_response_mode)
                    chat_entry = {
                        "question": suggestions[0],
                        "answer": answer,
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "response_mode": st.session_state.current_response_mode
                    }
                    st.session_state.chat_history.append(chat_entry)
                    st.rerun()
        
        with col_sug2:
            if st.button(f"💬 {suggestions[1][:30]}...", key="sug2", use_container_width=True):
                with st.spinner("🤔 Thinking..."):
                    answer = get_response(suggestions[1], st.session_state.current_response_mode)
                    chat_entry = {
                        "question": suggestions[1],
                        "answer": answer,
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "response_mode": st.session_state.current_response_mode
                    }
                    st.session_state.chat_history.append(chat_entry)
                    st.rerun()
        
        with col_sug3:
            if st.button(f"💬 {suggestions[2][:30]}...", key="sug3", use_container_width=True):
                with st.spinner("🤔 Thinking..."):
                    answer = get_response(suggestions[2], st.session_state.current_response_mode)
                    chat_entry = {
                        "question": suggestions[2],
                        "answer": answer,
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                        "response_mode": st.session_state.current_response_mode
                    }
                    st.session_state.chat_history.append(chat_entry)
                    st.rerun()
    
    # Chat input at the bottom
    st.subheader("💭 Ask a Question")
    st.caption("🌱 I specialize in sustainability, environmental issues, and renewable energy topics")
    
    # Use form to handle enter key submission
    with st.form(key="chat_form", clear_on_submit=True):
        query = st.text_input("🔍 Enter your question", placeholder="e.g., What is the carbon footprint of electric vehicles?")
        submit_button = st.form_submit_button("Send 🚀")
    
    # Process the query
    if submit_button and query.strip():
        with st.spinner("🤔 Thinking..."):
            answer = get_response(query, response_mode)
            
            # Add to chat history
            chat_entry = {
                "question": query,
                "answer": answer,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "response_mode": response_mode
            }
            st.session_state.chat_history.append(chat_entry)
            
            # Rerun to show the new message
            st.rerun()
    
    elif submit_button and not query.strip():
        st.warning("Please enter a question to continue.")

# ------------------------ Main App Logic ------------------------
# Route to the appropriate page based on session state
if st.session_state.page == "home":
    show_home_page()
elif st.session_state.page == "news":
    show_news_page()
elif st.session_state.page == "chat":
    show_chat_page()
