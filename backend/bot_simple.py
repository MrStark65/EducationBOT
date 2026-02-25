#!/usr/bin/env python3
"""Simple Telegram bot polling using requests"""

import os
import json
import time
import requests
from dotenv import load_dotenv
from multi_user_database import MultiUserDatabase
from user_repository import UserRepository

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
BACKEND_URL = "http://localhost:8000"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Initialize multi-user database
db = MultiUserDatabase()
user_repo = UserRepository(db)

def get_updates(offset=None):
    """Get updates from Telegram"""
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return {"ok": False}

def answer_callback_query(callback_query_id, text=None):
    """Answer callback query"""
    url = f"{TELEGRAM_API}/answerCallbackQuery"
    data = {"callback_query_id": callback_query_id}
    if text:
        data["text"] = text
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error answering callback: {e}")
        return {"ok": False}

def send_message(chat_id, text, parse_mode=None):
    """Send message to chat"""
    url = f"{TELEGRAM_API}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return {"ok": False}

def handle_start_command(message):
    """Handle /start command - register new user"""
    chat_id = str(message.get("chat", {}).get("id"))
    user_info = message.get("from", {})
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    
    try:
        # Check if user exists
        existing_user = user_repo.get_user_by_chat_id(chat_id)
        
        if existing_user:
            welcome_msg = f"👋 Welcome back, {first_name}!\n\n"
            welcome_msg += "You're already registered with Officer Priya CDS System.\n\n"
            welcome_msg += "📚 Your daily study videos will be sent automatically.\n"
            welcome_msg += "📊 Check your progress at the dashboard!"
        else:
            # Create new user
            user_id = user_repo.create_user(chat_id, username, first_name, last_name)
            
            welcome_msg = f"🎉 Welcome, {first_name}!\n\n"
            welcome_msg += "✅ You've been registered with Officer Priya CDS System.\n\n"
            welcome_msg += "📚 You'll receive daily study videos for:\n"
            welcome_msg += "   • English\n"
            welcome_msg += "   • History\n"
            welcome_msg += "   • Polity\n"
            welcome_msg += "   • Geography\n"
            welcome_msg += "   • Economics\n\n"
            welcome_msg += "📊 Track your progress on the dashboard!\n"
            welcome_msg += "🔥 Build your study streak!\n\n"
            welcome_msg += "Good luck with your CDS preparation! 💪"
            
            print(f"✅ New user registered: {first_name} (Chat ID: {chat_id})")
        
        send_message(chat_id, welcome_msg)
        
    except Exception as e:
        print(f"Error handling /start: {e}")
        send_message(chat_id, "❌ Registration failed. Please try again later.")

def handle_message(message):
    """Handle incoming text messages"""
    text = message.get("text", "")
    
    if text.startswith("/start"):
        handle_start_command(message)
    elif text.startswith("/help"):
        chat_id = message.get("chat", {}).get("id")
        help_msg = "📖 Officer Priya CDS System Help\n\n"
        help_msg += "Commands:\n"
        help_msg += "/start - Register or check status\n"
        help_msg += "/help - Show this help message\n\n"
        help_msg += "You'll receive daily study videos automatically.\n"
        help_msg += "Click ✅ Done or ❌ Not Done to track your progress!"
        send_message(chat_id, help_msg)

def handle_callback(callback_query):
    """Handle callback query"""
    callback_id = callback_query.get("id")
    data_str = callback_query.get("data", "{}")
    chat_id = str(callback_query.get("message", {}).get("chat", {}).get("id"))
    
    try:
        # Verify user is registered
        user = user_repo.get_user_by_chat_id(chat_id)
        if not user:
            answer_callback_query(callback_id, "Please send /start first to register")
            send_message(chat_id, "⚠️ Please send /start to register before using the system.")
            return
        
        # Update last active
        user_repo.update_last_active(user.id)
        
        # Parse callback data
        data = json.loads(data_str)
        day = data.get("day")
        status = data.get("status")
        
        # Answer callback immediately
        status_text = "Done ✅" if status == "DONE" else "Not Done ❌"
        answer_callback_query(callback_id, f"Day {day} marked as {status_text}")
        
        # Send to backend webhook with user info
        webhook_data = {
            "callback_query": {
                "id": callback_id,
                "from": callback_query.get("from", {}),
                "message": callback_query.get("message", {}),
                "data": data_str,
                "user_id": user.id  # Add user ID for backend
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/api/telegram/webhook", json=webhook_data)
        result = response.json()
        
        if result.get("ok"):
            # Send confirmation message
            streak = result.get("streak", 0)
            send_message(chat_id, f"✅ Day {day} marked as {status_text}!\n🔥 Current streak: {streak} days\n\nCheck your dashboard for updated stats.")
        else:
            send_message(chat_id, f"❌ Failed to update: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error handling callback: {e}")
        answer_callback_query(callback_id, "Error occurred")
        if chat_id:
            send_message(chat_id, f"❌ Error: {str(e)}")

def main():
    """Main polling loop"""
    print("🤖 Starting Telegram Bot (Simple Polling)")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 50)
    
    # Get bot info
    response = requests.get(f"{TELEGRAM_API}/getMe")
    if response.ok:
        bot_info = response.json().get("result", {})
        print(f"✅ Bot started: @{bot_info.get('username')}")
        print(f"   Bot ID: {bot_info.get('id')}")
    else:
        print("❌ Failed to get bot info")
        return
    
    print(f"\n💡 Test by running: curl -X POST {BACKEND_URL}/api/send-daily")
    print("\nListening for button clicks...")
    print("Press Ctrl+C to stop\n")
    
    offset = None
    
    try:
        while True:
            # Get updates
            result = get_updates(offset)
            
            if not result.get("ok"):
                time.sleep(1)
                continue
            
            updates = result.get("result", [])
            
            for update in updates:
                # Update offset
                offset = update.get("update_id") + 1
                
                # Handle messages
                if "message" in update:
                    message = update["message"]
                    if "text" in message:
                        print(f"📥 Received message: {message.get('text', '')[:50]}")
                        handle_message(message)
                
                # Handle callback queries
                elif "callback_query" in update:
                    print(f"📥 Received button click")
                    handle_callback(update["callback_query"])
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping bot...")
        print("✅ Bot stopped")

if __name__ == "__main__":
    main()
