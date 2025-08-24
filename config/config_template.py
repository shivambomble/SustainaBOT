"""
Configuration template for SustainaBOT
Copy this file to config.py and fill in your actual API keys
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get configuration from environment or Streamlit secrets
def get_config_value(key, default_value):
    """Get configuration value from environment variables or Streamlit secrets"""
    # First try environment variables
    value = os.getenv(key)
    if value and value != default_value:
        return value
    
    # Then try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    return default_value

# Groq API Configuration
GROQ_API_KEY = get_config_value("GROQ_API_KEY", "your_groq_api_key_here")

# Email Configuration
SMTP_CONFIG = {
    "EMAIL": get_config_value("SMTP_EMAIL", "your_email@gmail.com"),
    "PASSWORD": get_config_value("SMTP_PASSWORD", "your_app_password_here")
}

# Tavily Search API Configuration
TAVILY_API_KEY = get_config_value("TAVILY_API_KEY", "your_tavily_api_key_here")

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

# Validate configuration on import (with graceful handling for development)
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
        print("💡 Please check your .env file and ensure all required API keys are set.")
        print("📖 Refer to SETUP.md for configuration instructions.")