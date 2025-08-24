# SustainaBOT 🌍 - Environmental Intelligence Assistant

SustainaBOT is a comprehensive AI-powered environmental intelligence platform that combines cutting-edge AI technologies to provide expert insights on sustainability, climate change, and renewable energy. Built with Retrieval-Augmented Generation (RAG), real-time web search, and advanced language models, it serves as your complete sustainability companion.

## ✨ Key Features

### 🤖 **AI-Powered Chat Assistant**
- **Continuous Conversations**: Persistent chat history with seamless conversation flow
- **Hybrid Knowledge System**: RAG + real-time web search for comprehensive answers
- **Dual Response Modes**: Choose between concise or detailed explanations
- **Smart Fallback**: Automatically switches to web search when RAG confidence is low
- **Email Integration**: Share any response directly with colleagues

### 📰 **Advanced News Hub**
- **8 Specialized Categories**: Solar, Wind, Hydro, Geothermal, Battery Storage, Policy, Investment, General
- **Smart Caching**: 5-minute intelligent caching system for optimal performance
- **Export Capabilities**: Download news as Markdown or JSON formats
- **Email Digests**: Send curated news summaries to your team
- **Article Management**: Save, organize, and manage your reading list
- **Real-time Statistics**: Track articles, sources, and update times

### 🏠 **Enhanced Home Dashboard**
- **Live Statistics**: Real-time platform metrics and usage analytics
- **Interactive Tips**: Daily sustainability insights with email sharing
- **Quick Actions**: One-click access to specific news categories
- **Visual Data**: CO₂ emissions charts and environmental visualizations
- **Professional Design**: Modern UI with gradient styling and responsive layout

### 🔒 **Security & Configuration**
- **Environment-Based Config**: Secure API key management via `.env` files
- **GitHub-Safe Structure**: No sensitive data in version control
- **Template-Based Setup**: Easy configuration for new developers
- **Graceful Error Handling**: Helpful warnings for missing configurations

## 🏗️ Architecture

SustainaBOT follows a modern, modular architecture designed for scalability and maintainability:

### 📊 **Data Layer**
- **Document Processing**: PDF parsing and text extraction from sustainability reports
- **Vector Database**: FAISS-powered similarity search with HuggingFace embeddings
- **Smart Caching**: Category-specific news caching with automatic invalidation
- **Session Management**: Persistent chat history and user preferences

### 🧠 **Intelligence Layer**
- **RAG Pipeline**: Advanced retrieval-augmented generation with confidence scoring
- **LLM Integration**: Groq-powered inference with llama3-70b-8192 model
- **Web Search**: Tavily API integration for real-time information retrieval
- **Content Processing**: Intelligent text cleaning and markdown formatting

### 🎨 **Presentation Layer**
- **Multi-Page Application**: Home dashboard, news hub, and chat interface
- **Responsive Design**: Professional UI with gradient styling and modern components
- **Interactive Elements**: Real-time statistics, export functions, and email integration
- **Error Handling**: Graceful fallbacks and user-friendly error messages

### 🔧 **Infrastructure Layer**
- **Configuration Management**: Environment-based secrets with template system
- **Modular Components**: Separated concerns across `rag/`, `models/`, `utils/`, `web_search/`
- **Export System**: Multi-format data export (JSON, Markdown, Email)
- **Security**: GitHub-safe configuration with comprehensive `.gitignore`

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (Recommended: Python 3.11+)
- **API Keys**: Groq and Tavily accounts
- **Email**: SMTP credentials for email functionality (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shivambomble/SustainaBOT.git
   cd SustainaBOT
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv project-env
   source project-env/bin/activate  # On Windows: project-env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # Required API Keys
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # Optional Email Configuration
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   ```

5. **Build the knowledge base:**
   ```bash
   python build_vector_store.py
   ```

6. **Launch the application:**
   ```bash
   streamlit run app.py
   ```

### 🔑 API Key Setup

#### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key
3. Add to your `.env` file

#### Tavily API Key
1. Visit [Tavily](https://tavily.com/)
2. Sign up and get your API key
3. Add to your `.env` file

#### Email Configuration (Optional)
For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833):
1. Enable 2-factor authentication
2. Generate an app password
3. Use the app password in your `.env` file

## 📖 User Guide

### 🏠 **Home Dashboard**

The enhanced home page provides:
- **Live Statistics**: Real-time metrics on chat sessions, saved articles, and platform usage
- **Daily Sustainability Tips**: Interactive tips with email sharing capability
- **Quick Actions**: Direct access to specific news categories (Solar, Wind, Battery Storage)
- **Feature Overview**: Comprehensive preview of all platform capabilities
- **Visual Data**: CO₂ emissions charts and environmental insights

### 💬 **Chat Interface**

**Continuous Conversations:**
1. Ask sustainability questions in natural language
2. Choose response style (Concise or Detailed)
3. View complete conversation history
4. Email any response to colleagues
5. Clear chat history when needed

**Advanced Features:**
- **Smart Responses**: RAG-powered answers with web search fallback
- **Conversation Persistence**: All chats saved during session
- **Email Integration**: Share individual responses or entire conversations
- **Response Modes**: Tailored output for different use cases

### 📰 **News Hub**

**Category-Based News:**
- **8 Specialized Categories**: Solar, Wind, Hydro, Geothermal, Battery, Policy, Investment, General
- **Customizable Articles**: Choose 3, 5, 8, or 10 articles per category
- **Smart Caching**: 5-minute cache for optimal performance
- **Real-time Statistics**: Track articles, sources, and update times

**Advanced Features:**
- **Export Options**: Download as Markdown or JSON
- **Email Digests**: Send curated news summaries
- **Article Management**: Save articles for later reading
- **Source Links**: Direct access to original news sources
- **Auto-refresh**: Optional automatic updates

### 📧 **Email Integration**

**Multiple Email Options:**
```python
# Direct email agent usage
from agent.email_agent import email_agent

query = "What are the latest developments in solar energy storage?"
recipient_email = "team@company.com"
email_agent(query, recipient_email)
```

**Built-in Email Features:**
- Share individual chat responses
- Send daily sustainability tips
- Email news digests by category
- Custom email formatting with SustainaBOT branding

## 📊 Data Sources & Knowledge Base

### 📚 **Corporate Sustainability Reports**
SustainaBOT's knowledge base includes comprehensive sustainability reports from industry leaders:

- **Technology**: Amazon, Apple, Microsoft, Google Environmental Reports 2024
- **Aerospace**: Boeing Sustainability & Social Impact Report 2024
- **Energy**: BP Sustainability Report 2024, Shell Sustainability Report
- **Automotive**: Tesla Impact Report, Ford Sustainability Report
- **And 20+ more major corporations**

### 🌐 **Real-Time Data Sources**
- **News Aggregation**: Tavily-powered web search across 1000+ sources
- **Climate Data**: Integration with environmental databases and APIs
- **Government Reports**: Access to EPA, IPCC, and international climate data
- **Research Papers**: Latest academic research on sustainability topics

### 📈 **Visual Data**
- **CO₂ Emissions**: Global and regional emission trends over time
- **Renewable Energy**: Adoption rates and capacity growth charts
- **Climate Indicators**: Temperature, sea level, and atmospheric data
- **Policy Tracking**: Environmental legislation and regulation updates

### 🔄 **Data Freshness**
- **RAG Knowledge**: Updated quarterly with latest corporate reports
- **News Data**: Real-time updates with 5-minute caching
- **Climate Data**: Daily updates from authoritative sources
- **Research Integration**: Monthly updates with latest academic findings

## 🛠️ Development

### Project Structure
```
SustainaBOT/
├── app.py                 # Main Streamlit application
├── main.py               # Direct email agent usage
├── build_vector_store.py # Knowledge base builder
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
│
├── agent/               # Email automation
│   └── email_agent.py
│
├── config/              # Configuration management
│   ├── config_template.py  # Secure config template
│   └── __init__.py
│
├── data/                # Knowledge base data
│   └── reports/         # PDF sustainability reports
│
├── images/              # Static assets
│   ├── annual_co2_emissions.png
│   └── annual_co2_by_region.png
│
├── models/              # AI model integrations
│   ├── llm.py          # Groq LLM interface
│   └── embeddings.py   # HuggingFace embeddings
│
├── rag/                 # RAG implementation
│   ├── rag_chain.py    # Main RAG pipeline
│   ├── retriever.py    # Document retrieval
│   ├── loader.py       # PDF processing
│   ├── splitter.py     # Text chunking
│   └── vector_store.py # FAISS integration
│
├── utils/               # Utility functions
│   ├── email_sender.py # Email functionality
│   ├── news_export.py  # Export utilities
│   └── format.py       # Text formatting
│
├── vector_db/           # FAISS database
│   ├── index.faiss     # Vector index
│   └── index.pkl       # Metadata
│
└── web_search/          # Web search integration
    └── search.py       # Tavily API interface
```

### 🔧 Configuration Management

SustainaBOT uses a secure, environment-based configuration system:

- **Template System**: `config/config_template.py` provides the structure
- **Environment Variables**: All secrets stored in `.env` file
- **GitHub Safe**: No sensitive data in version control
- **Easy Setup**: Copy `.env.example` to get started
- **Validation**: Automatic configuration validation with helpful error messages

### 🧪 Testing

```bash
# Test configuration
python -c "from config.config_template import GROQ_API_KEY; print('✅ Config loaded')"

# Test app imports
python -c "import app; print('✅ App imports successfully')"

# Run the application
streamlit run app.py
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### 📋 Contribution Guidelines

- Follow the existing code style and structure
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Keep commits focused and descriptive

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgements

### Core Technologies
- **[LangChain](https://github.com/langchain-ai/langchain)** - RAG framework and document processing
- **[Streamlit](https://streamlit.io/)** - Interactive web application framework
- **[FAISS](https://github.com/facebookresearch/faiss)** - Efficient vector similarity search
- **[Groq](https://groq.com/)** - High-performance LLM inference
- **[Tavily](https://tavily.com/)** - Real-time web search capabilities

### AI & ML Libraries
- **[HuggingFace Transformers](https://huggingface.co/transformers/)** - Embedding models
- **[LangChain Community](https://github.com/langchain-ai/langchain)** - Extended integrations
- **[Python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment management

### Data & Visualization
- **[Pillow](https://pillow.readthedocs.io/)** - Image processing
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **[NumPy](https://numpy.org/)** - Numerical computing

---

<div align="center">

**🌱 SustainaBOT - Empowering sustainable decisions through AI-driven insights**

*Built with ❤️ for a greener future*

[🌍 Live Demo](https://sustainabot.streamlit.app) • [📖 Documentation](https://github.com/shivambomble/SustainaBOT/wiki) • [🐛 Report Bug](https://github.com/shivambomble/SustainaBOT/issues) • [💡 Request Feature](https://github.com/shivambomble/SustainaBOT/issues)

</div>