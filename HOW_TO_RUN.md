# How to Run Officer Priya CDS System

## Quick Start - Run All Services

You need to run **2 services** in **2 different terminals**:

### Terminal 1: Backend API (includes EVERYTHING)
```bash
./start-backend.sh
```
- Runs on port 8000
- Handles all API requests
- **Automatically runs Telegram Bot in background**
- **Automatically runs file scheduler in background**
- **Automatically runs daily content scheduler in background**
- Required for everything to work

### Terminal 2: Frontend
```bash
./start-frontend.sh
```
- Runs on port 5173
- Admin dashboard UI
- Open http://localhost:5173 in browser

## What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| Backend API | 8000 | REST API + Telegram Bot + File Scheduler + Daily Scheduler |
| Frontend | 5173 | Admin dashboard |

## Important Notes

✅ **Everything runs automatically when you start the backend!**

- Backend includes: API, Telegram Bot, File Scheduler, Daily Content Scheduler
- No need to run separate terminals for bot or schedulers
- Just start backend and frontend - that's it!
- Bot runs in a background thread automatically

⚠️ **Both services must be running for full functionality:**

- Without **Backend API**: Nothing works (it runs everything)
- Without **Frontend**: No admin dashboard (but bot and schedulers still work)

## Testing

### 1. Test Backend API
```bash
curl http://localhost:8000/api/health
```
Should return: `{"status":"healthy","timestamp":"..."}`

### 2. Test Telegram Bot
- Open Telegram
- Search for @OfficerPriyaBot
- Send `/start`
- Should receive welcome message
- Bot is running automatically with backend!

### 3. Test Scheduler
- Set schedule time to current time + 2 minutes
- Wait 2 minutes
- Check Telegram for message

### 4. Test Frontend
- Open http://localhost:5173
- Should see dashboard
- Select user from dropdown
- Click "Send Now" button

## Stopping Services

Press `Ctrl+C` in each terminal to stop the service.

Or kill all at once:
```bash
pkill -f "uvicorn main:app"
pkill -f "vite"
```

Note: Bot and schedulers stop automatically when backend stops (they run in background threads)!

## Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use: `lsof -i :8000`
- Check if virtual environment is activated
- Check if all dependencies are installed: `pip install -r requirements.txt`

### Bot not responding?
- Bot runs automatically with backend - check backend terminal for bot logs
- Look for "🤖 Starting Telegram Bot in background..." message
- Check if bot token is correct in `backend/.env`
- Bot logs appear in the same terminal as backend

### Daily content not being sent?
- Daily scheduler runs automatically with backend
- Check backend terminal for scheduler logs
- Verify schedule is enabled in UI
- Verify time format is HH:MM

### Scheduled files not being sent?
- File scheduler runs automatically with backend
- Check backend terminal for file scheduler logs
- Verify file was scheduled in Documents tab
- Check that scheduled time has passed

### Frontend won't load?
- Check if port 5173 is already in use: `lsof -i :5173`
- Check if node_modules are installed: `npm install`
- Check browser console for errors

## First Time Setup

If this is your first time running the project:

1. **Install Backend Dependencies:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run Database Migration:**
```bash
python migrations/001_advanced_scheduler_file_management.py
python migrations/002_custom_playlists.py
python migrations/003_playlist_schedules.py
python migrations/004_global_schedule.py
python migrations/005_advanced_schedules.py
python migrations/006_playlist_metadata.py
python migrations/007_custom_subjects.py
python migrations/008_user_blocks.py
```

3. **Install Frontend Dependencies:**
```bash
cd frontend
npm install
```

4. **Configure Environment:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your Telegram bot token, GROQ API key, YouTube API key
```

5. **Start All Services** (see Quick Start above)

## Development Tips

- Keep both terminals visible to monitor logs
- Backend terminal shows: API requests, bot messages, file scheduler, and daily scheduler activity
- Backend API auto-reloads on code changes (bot and schedulers restart automatically)
- Frontend auto-reloads on code changes
- All logs appear in backend terminal - easy to debug!
- Bot runs in background thread - no separate terminal needed

## Production Deployment

For production, use process managers:
- Backend API (includes bot and schedulers): Use gunicorn or uvicorn with systemd
- Frontend: Build and serve with nginx

See `DEPLOYMENT_GUIDE.md` for details.

## Architecture

```
┌─────────────────────────────────────────┐
│         Backend (Port 8000)             │
│  ┌───────────────────────────────────┐  │
│  │         FastAPI Server            │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │   Telegram Bot (Background)       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  File Scheduler (Background)      │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Daily Scheduler (Background)     │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│       Frontend (Port 5173)              │
│         React + Vite                    │
└─────────────────────────────────────────┘
```

Everything runs from one backend process!
