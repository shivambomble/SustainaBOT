# SustainaBOT Setup Instructions

## 🔧 Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/shivambomble/SustainaBOT.git
cd SustainaBOT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

#### Option A: Using .env file (Recommended)
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and add your actual API keys:
   ```bash
   # Edit with your preferred editor
   nano .env
   # or
   code .env
   ```

3. Fill in your API keys:
   ```env
   GROQ_API_KEY=your_actual_groq_key
   TAVILY_API_KEY=your_actual_tavily_key
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

#### Option B: Using config.py directly
1. Copy the template:
   ```bash
   cp config/config_template.py config/config.py
   ```

2. Edit `config/config.py` and replace the placeholder values with your actual API keys.

### 4. Get API Keys

#### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/Login
3. Generate an API key
4. Copy the key to your `.env` file

#### Tavily API Key
1. Visit [Tavily](https://tavily.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Copy the key to your `.env` file

#### Gmail App Password (for email features)
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings
3. Generate an "App Password" for the application
4. Use this app password (not your regular password)

### 5. Build Vector Database
```bash
python build_vector_store.py
```

### 6. Run the Application
```bash
streamlit run app.py
```

## 🔒 Security Notes

- **Never commit API keys to Git**
- The `.env` file is ignored by Git for security
- Use environment variables in production
- Rotate API keys regularly
- Use app passwords for Gmail, not your main password

## 🚀 Deployment

For production deployment:
1. Set environment variables on your hosting platform
2. Don't use the `.env` file in production
3. Use your platform's secret management system

## 📝 Configuration Validation

The application will validate your configuration on startup and warn you about missing keys.