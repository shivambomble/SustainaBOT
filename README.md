# SustainaBOT 🌍♻️

SustainaBOT is an AI-powered assistant designed to answer questions about sustainability, environmental impact, and climate change. It combines Retrieval-Augmented Generation (RAG), web search capabilities, and large language models to provide accurate and informative responses to sustainability-related queries.

## Features

- **Hybrid Knowledge System**: Combines document-based knowledge with real-time web search
- **RAG Architecture**: Uses sustainability reports from major companies as a knowledge base
- **Web Search Fallback**: Automatically falls back to web search when the knowledge base doesn't have an answer
- **Renewable Energy News**: Daily updated top 5 news about renewable energy developments
- **Email Functionality**: Send responses directly to teammates or colleagues
- **Streamlit UI**: User-friendly interface with a landing page for multiple features
- **Daily Sustainability Tips**: Provides daily tips for sustainable living
- **Response Modes**: Choose between concise or detailed responses

## Architecture

SustainaBOT is built with a modular architecture:

1. **Document Processing**:
   - PDF loading from sustainability reports
   - Text chunking and embedding
   - FAISS vector database for efficient retrieval

2. **Query Processing**:
   - RAG chain for document-based answers
   - Web search fallback using Tavily API
   - Response formatting and cleaning

3. **User Interface**:
   - Streamlit-based web application with landing page
   - News section with clickable source links
   - Chat interface for sustainability Q&A
   - Email functionality for sharing results

4. **Models**:
   - Groq LLM integration (llama3-70b-8192)
   - HuggingFace embeddings for document vectorization

## Setup Instructions

### Prerequisites

- Python 3.9+
- API keys for Groq and Tavily
- SMTP credentials for email functionality

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shivambomble/SustainaBOT.git
   cd SustainaBOT
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Create or modify `config/config.py` with your API keys:
   ```python
   GROQ_API_KEY = "your_groq_api_key"
   TAVILY_API_KEY = "your_tavily_api_key"
   SMTP_CONFIG = {
       "EMAIL": "your_email@gmail.com",
       "PASSWORD": "your_app_password"
   }
   ```

4. Build the vector database:
   ```bash
   python build_vector_store.py
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

### Landing Page

The application now features a landing page with two main options:

1. **Renewable Energy News**: View the top 5 latest news about renewable energy with links to original sources
2. **Chat with SustainaBOT**: Access the Q&A functionality for sustainability questions

### Chat Interface

1. Enter your sustainability-related question in the text input field
2. Select your preferred response style (Concise or Detailed)
3. Click "Get Answer" to generate a response
4. Optionally, send the response via email to a colleague

### News Section

1. View the top 5 latest news about renewable energy
2. Each news item includes a headline, summary, and date when available
3. Click on "Read more" links to access the original news sources
4. Refresh the news with the "Refresh News" button

### Email Agent

You can also use the email agent directly in your code:

```python
from agent.email_agent import email_agent

query = "What is the carbon footprint of cloud computing?"
recipient_email = "colleague@example.com"

email_agent(query, recipient_email)
```

## Data Sources

SustainaBOT uses sustainability reports from major companies as its knowledge base, including:

- Amazon Sustainability Report 2024
- Boeing Sustainability & Social Impact Report 2024
- Apple Environmental Progress Report 2024
- Microsoft Environmental Sustainability Report 2024
- BP Sustainability Report 2024
- Google Environmental Report 2024
- And more...

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [Streamlit](https://streamlit.io/) for the web interface
- [FAISS](https://github.com/facebookresearch/faiss) for vector similarity search
- [Groq](https://groq.com/) for LLM inference
- [Tavily](https://tavily.com/) for web search capabilities