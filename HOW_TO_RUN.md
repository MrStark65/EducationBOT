# How to Run Officer Priya CDS System

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Telegram account
- Telegram Bot Token (from @BotFather)

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your bot token
# TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Step 2: Setup Frontend

```bash
# Navigate to frontend directory (open new terminal)
cd frontend

# Install dependencies
npm install
```

### Step 3: Run All Services

Open 4 separate terminals and run:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Telegram Bot:**
```bash
cd backend
source venv/bin/activate
python bot_simple.py
```

**Terminal 3 - Scheduler (Optional - for automated messages):**
```bash
cd backend
source venv/bin/activate
python multi_user_scheduler.py
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 📱 Register Users

1. Open Telegram
2. Search for your bot (e.g., @OfficerPriyaBot)
3. Send `/start` command
4. You'll receive a welcome message
5. Refresh the dashboard - you'll see your profile!

## 🎯 Using the Dashboard

### View All Users
- Dashboard automatically shows all registered users
- Click on user name in header to switch between users

### Send Messages to All Users
1. Click "Send to All Users (X)" button
2. All registered users receive their daily study videos
3. Each user gets personalized content based on their progress

### Configure Schedule
1. Go to "Schedule" tab
2. Enable automation
3. Set your preferred time (e.g., 06:00)
4. Click "Save Schedule"
5. Messages will be sent automatically at that time daily

### Manage Playlists
1. Go to "Settings" tab
2. Click "Edit" next to any subject
3. Paste YouTube playlist URL
4. Click "Save"

## 🛠️ Using Convenience Scripts

We've created scripts to make running easier:

### Start Backend API
```bash
./start-backend.sh
```

### Start Frontend
```bash
./start-frontend.sh
```

### Start Scheduler
```bash
./start-scheduler.sh
```

## 📊 Project Structure

```
Priya-cds-bot/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── bot_simple.py              # Telegram bot (handles buttons)
│   ├── multi_user_scheduler.py   # Automated scheduler
│   ├── multi_user_database.py    # Database schema
│   ├── user_repository.py        # User operations
│   ├── video_selector.py         # Video selection logic
│   ├── telegram_bot.py            # Telegram API wrapper
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main application
│   │   ├── components/           # React components
│   │   └── App.css               # Styling
│   ├── package.json              # Node dependencies
│   └── vite.config.js            # Vite configuration
└── README.md                      # Project documentation
```

## 🔧 Configuration

### Backend (.env file)
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Frontend (.env file - optional)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
cd backend
rm officer_priya_multi.db
python multi_user_database.py
```

### Bot Not Responding
1. Check bot token in `.env` file
2. Verify bot is running (`python bot_simple.py`)
3. Check bot logs for errors
4. Ensure bot is not blocked by Telegram

### Scheduler Not Sending
1. Verify scheduler is running (`python multi_user_scheduler.py`)
2. Check schedule is enabled in dashboard
3. Verify time format is HH:MM (e.g., 06:00)
4. Check scheduler logs for errors

## 📝 Testing

### Test Manual Send
```bash
# Clear today's logs first
cd backend
source venv/bin/activate
python clear_today_logs.py

# Then click "Send to All Users" in dashboard
```

### Test Scheduled Send
1. Set schedule time to 2 minutes from now
2. Enable automation
3. Save schedule
4. Wait and check Telegram
5. Verify message received

### Test Multiple Users
1. Register 2+ users via Telegram
2. Open dashboard
3. See all users in dropdown
4. Click "Send to All Users"
5. Verify all users received messages

## 🔄 Updating the Project

```bash
# Pull latest changes
git pull

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies
cd frontend
npm install

# Restart all services
```

## 🛑 Stopping the Project

Press `Ctrl+C` in each terminal to stop:
1. Backend API
2. Telegram Bot
3. Scheduler
4. Frontend

Or use:
```bash
# Kill all Python processes
pkill -f "python"

# Kill all Node processes
pkill -f "node"
```

## 📚 Additional Resources

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

## 🆘 Getting Help

If you encounter issues:

1. Check the logs in each terminal
2. Verify all services are running
3. Check database exists: `ls backend/*.db`
4. Verify bot token is correct
5. Ensure users are registered (send /start)

## 🎉 Success Checklist

- [ ] Backend API running on port 8000
- [ ] Telegram bot responding to /start
- [ ] Scheduler running (optional)
- [ ] Frontend accessible at localhost:5173
- [ ] Users registered via Telegram
- [ ] Dashboard showing users
- [ ] Can send messages to all users
- [ ] Can switch between users
- [ ] Schedule configuration working

## 🚀 Production Deployment

For production deployment, see:
- Backend: Deploy to Render, Railway, or Heroku
- Frontend: Deploy to Vercel, Netlify, or Cloudflare Pages
- Database: Use PostgreSQL instead of SQLite
- Scheduler: Use cron jobs or background workers

---

**Built with ❤️ for CDS OTA Preparation**
