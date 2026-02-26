#!/bin/bash

echo "🚀 Starting Backend API..."
echo "=========================="
cd backend
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "📡 Starting FastAPI server on port 8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
