#!/usr/bin/env python3
"""Setup Telegram webhook"""

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def setup_webhook():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
    bot = Bot(token=token)
    
    # For local testing, we'll use polling instead of webhook
    # To use webhook, you need a public URL (use ngrok or deploy to Render)
    
    print("🤖 Telegram Bot Setup")
    print("=" * 50)
    
    # Get bot info
    me = await bot.get_me()
    print(f"✅ Bot connected: @{me.username}")
    print(f"   Bot ID: {me.id}")
    print(f"   Bot Name: {me.first_name}")
    
    # Check current webhook
    webhook_info = await bot.get_webhook_info()
    print(f"\n📡 Current webhook: {webhook_info.url or 'None (using polling)'}")
    
    # For local development, delete webhook to use polling
    if webhook_info.url:
        print("\n🔄 Removing webhook for local development...")
        await bot.delete_webhook()
        print("✅ Webhook removed. Bot will use polling mode.")
    
    print("\n" + "=" * 50)
    print("📝 Next steps:")
    print("1. For local testing: Use polling mode (webhook removed)")
    print("2. For production: Set webhook URL after deploying to Render")
    print("   Command: python setup_webhook.py --url https://your-app.onrender.com/api/telegram/webhook")
    print("\n💡 For now, test by sending messages directly via API:")
    print("   curl -X POST http://localhost:8000/api/send-daily")

if __name__ == "__main__":
    import sys
    
    if "--url" in sys.argv:
        # Set webhook URL
        idx = sys.argv.index("--url")
        if idx + 1 < len(sys.argv):
            webhook_url = sys.argv[idx + 1]
            
            async def set_webhook():
                token = os.getenv("TELEGRAM_BOT_TOKEN", "8765768664:AAFK0cbqSnKFfFoNl2a2kJF0g_mdMnoP348")
                bot = Bot(token=token)
                await bot.set_webhook(webhook_url)
                print(f"✅ Webhook set to: {webhook_url}")
            
            asyncio.run(set_webhook())
        else:
            print("❌ Error: --url requires a URL argument")
    else:
        asyncio.run(setup_webhook())
