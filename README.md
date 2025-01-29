# Telegram AI Chatbot 🤖

A Telegram chatbot powered by Google Gemini AI, MongoDB for data storage, and web search capabilities.

## Features ✨
- User registration with phone number.
- AI-powered chat using Google Gemini.
- Image analysis via Gemini Vision.
- Web search with AI summarization.
- Data storage in MongoDB.

## Prerequisites 📋
- Python 3.10+
- MongoDB Atlas account (for cloud database).
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather)).
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com/)).

## Setup 🛠️

1. Clone the Repository
```bash
git clone https://github.com/yourusername/telegram-ai-bot.git
cd telegram-ai-bot

2. Install Dependencies
pip install -r requirements.txt

3. Configure Environment Variables
Create a .env file with:
TELEGRAM_TOKEN="YOUR_BOT_TOKEN"
GEMINI_API_KEY="YOUR_GEMINI_KEY"
MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/TelegramBot"

4. Run the Bot
python main.py

Usage 🚀
Start the bot with /start and share your contact.
Chat: Send text messages for Gemini responses.
Image Analysis: Upload images (JPG/PNG) for descriptions.
Web Search: Use /websearch <query>.
