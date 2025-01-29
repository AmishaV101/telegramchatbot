import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["TelegramBot"]

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================== CORE FUNCTIONS ================== #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command and user registration"""
    contact_button = KeyboardButton("📱 Share Contact", request_contact=True)
    await update.message.reply_text(
        "👋 Welcome! Please share your contact:",
        reply_markup=ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True)
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves user data to MongoDB"""
    user = update.effective_user
    contact = update.message.contact
    
    # Save to database
    db.users.update_one(
        {"chat_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "phone": contact.phone_number,
            "registered_at": datetime.now()
        }},
        upsert=True
    )
    await update.message.reply_text("✅ Registration complete! Now chat with me!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages with Gemini"""
    response = text_model.generate_content(update.message.text)
    
    # Save chat history
    db.chats.insert_one({
        "user_id": update.effective_user.id,
        "query": update.message.text,
        "response": response.text,
        "timestamp": datetime.now()
    })
    await update.message.reply_text(response.text)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyzes images using Gemini Vision"""
    photo = await update.message.photo[-1].get_file()
    img_data = await photo.download_as_bytearray()
    
    response = vision_model.generate_content(img_data)
    
    # Save file metadata
    db.files.insert_one({
        "user_id": update.effective_user.id,
        "file_id": photo.file_id,
        "description": response.text,
        "timestamp": datetime.now()
    })
    await update.message.reply_text(f"🔍 Analysis:\n{response.text}")

async def web_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /websearch command"""
    query = ' '.join(context.args)
    
    # Simple web scraping (replace with better API if time permits)
    headers = {'User-Agent': 'Mozilla/5.0'}
    html = requests.get(f"https://www.google.com/search?q={query}", headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    results = [result.text for result in soup.find_all('div', class_='BNeawe')][:3]
    
    # Generate summary using Gemini
    summary = text_model.generate_content(f"Summarize these search results: {results}").text
    
    # Save search
    db.searches.insert_one({
        "user_id": update.effective_user.id,
        "query": query,
        "summary": summary,
        "timestamp": datetime.now()
    })
    await update.message.reply_text(f"🌐 Web Results:\n{summary}")

# ================== MAIN ================== #

if __name__ == '__main__':
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('websearch', web_search))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    app.run_polling()