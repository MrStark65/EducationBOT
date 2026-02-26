#!/bin/bash

echo "🤖 Starting Telegram Bot..."
echo "=========================="
cd backend
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "📱 Starting bot polling..."
python bot_simple.py
