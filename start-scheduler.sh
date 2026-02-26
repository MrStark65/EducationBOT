#!/bin/bash

echo "⏰ Starting Scheduler..."
echo "=========================="
cd backend
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "📅 Starting automated scheduler..."
echo "   Checks every minute for scheduled messages"
python multi_user_scheduler.py
