"""
Configuration template for SustainaBOT
Copy this file to config.py and fill in your actual API keys
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# Email Configuration
SMTP_CONFIG = {
    "EMAIL": os.getenv("SMTP_EMAIL", "your_email@gmail.com"),
    "PASSWORD": os.getenv("SMTP_PASSWORD", "your_app_password_here")
}

# Tavily Search API Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your_tavily_api_key_here")

# Validate that all required API keys are present
def validate_config():
    """Validate that all required configuration is present"""
    missing_keys = []
    
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        missing_keys.append("GROQ_API_KEY")
    
    if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
        missing_keys.append("TAVILY_API_KEY")
    
    if not SMTP_CONFIG["EMAIL"] or SMTP_CONFIG["EMAIL"] == "your_email@gmail.com":
        missing_keys.append("SMTP_EMAIL")
    
    if not SMTP_CONFIG["PASSWORD"] or SMTP_CONFIG["PASSWORD"] == "your_app_password_here":
        missing_keys.append("SMTP_PASSWORD")
    
    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
    
    return True

# Validate configuration on import
if __name__ != "__main__":
    validate_config()