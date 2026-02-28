#!/bin/bash

echo "🤖 Starting Telegram Bot (Polling Mode)..."
echo "=========================="
cd backend
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "📱 Starting bot with AI support..."
python bot_polling_simple.py

