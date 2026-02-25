#!/usr/bin/env python3
"""Run Telegram bot with polling for local development"""

import asyncio
import os
import json
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
import aiohttp

load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
BACKEND_URL = "http://localhost:8000"

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    
    # Answer callback immediately to remove loading state
    await query.answer()
    
    try:
        # Parse callback data
        data = json.loads(query.data)
        day = data.get("day")
        status = data.get("status")
        
        # Send to backend webhook
        async with aiohttp.ClientSession() as session:
            webhook_data = {
                "callback_query": {
                    "id": query.id,
                    "from": {
                        "id": query.from_user.id,
                        "first_name": query.from_user.first_name
                    },
                    "message": {
                        "chat": {
                            "id": query.message.chat_id
                        }
                    },
                    "data": query.data
                }
            }
            
            async with session.post(f"{BACKEND_URL}/api/telegram/webhook", json=webhook_data) as resp:
                result = await resp.json()
                
                if result.get("ok"):
                    status_text = "Done ✅" if status == "DONE" else "Not Done ❌"
                    await query.message.reply_text(
                        f"✅ Day {day} marked as {status_text}!\n\n"
                        f"Check your dashboard for updated stats."
                    )
                else:
                    await query.message.reply_text(
                        f"❌ Failed to update: {result.get('error', 'Unknown error')}"
                    )
    
    except Exception as e:
        print(f"Error handling callback: {e}")
        await query.message.reply_text(f"❌ Error: {str(e)}")

async def main():
    """Start the bot with polling"""
    print("🤖 Starting Telegram Bot (Polling Mode)")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 50)
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add callback handler
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Get bot info
    bot = Bot(BOT_TOKEN)
    me = await bot.get_me()
    print(f"✅ Bot started: @{me.username}")
    print(f"   Listening for button clicks...")
    print(f"\n💡 Test by running: curl -X POST {BACKEND_URL}/api/send-daily")
    print("\nPress Ctrl+C to stop\n")
    
    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("✅ Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
