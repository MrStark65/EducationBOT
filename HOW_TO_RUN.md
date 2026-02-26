# How to Run Officer Priya CDS System

## Quick Start - Run All Services

You need to run **4 separate services** in **4 different terminals**:

### Terminal 1: Backend API
```bash
./start-backend.sh
```
- Runs on port 8000
- Handles all API requests
- Required for frontend to work

### Terminal 2: Telegram Bot
```bash
./start-bot.sh
```
- Listens for Telegram messages
- Handles button clicks (Done/Not Done)
- Responds to /start command

### Terminal 3: Scheduler
```bash
./start-scheduler.sh
```
- Checks every minute for scheduled messages
- Sends daily messages at scheduled time
- **Required for automated daily messages**

### Terminal 4: Frontend
```bash
./start-frontend.sh
```
- Runs on port 5173
- Admin dashboard UI
- Open http://localhost:5173 in browser

## What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| Backend API | 8000 | REST API for frontend |
| Telegram Bot | - | Handles Telegram interactions |
| Scheduler | - | Sends scheduled messages |
| Frontend | 5173 | Admin dashboard |

## Important Notes

⚠️ **All 4 services must be running for full functionality:**

- Without **Backend API**: Frontend won't work
- Without **Telegram Bot**: Button clicks won't work
- Without **Scheduler**: Scheduled messages won't be sent
- Without **Frontend**: No admin dashboard

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
pkill -f "bot_simple.py"
pkill -f "multi_user_scheduler.py"
pkill -f "vite"
```

## Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use: `lsof -i :8000`
- Check if virtual environment is activated
- Check if all dependencies are installed: `pip install -r requirements.txt`

### Bot not responding?
- Check if bot token is correct in `backend/.env`
- Check bot terminal for errors
- Verify bot is running: `ps aux | grep bot_simple`

### Scheduler not sending messages?
- Check if scheduler is running: `ps aux | grep multi_user_scheduler`
- Check scheduler terminal for logs
- Verify schedule is enabled in UI
- Verify time format is HH:MM

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
# Edit .env and add your Telegram bot token
```

5. **Start All Services** (see Quick Start above)

## Development Tips

- Keep all 4 terminals visible to monitor logs
- Backend API auto-reloads on code changes
- Frontend auto-reloads on code changes
- Bot and Scheduler need manual restart after code changes

## Production Deployment

For production, use process managers:
- Backend API: Use gunicorn or uvicorn with systemd
- Bot: Use systemd service
- Scheduler: Use systemd service or cron
- Frontend: Build and serve with nginx

See `DEPLOYMENT_GUIDE.md` for details.
