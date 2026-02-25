# 🎖️ Officer Priya CDS Preparation Automation System

An automated Telegram-based study management system for CDS OTA examination preparation with disciplined, officer-style training approach.

## ✨ New Features (Multi-User System)

- **Multi-User Support** - Unlimited users can register independently
- **User Dashboard** - View and switch between all registered users
- **Broadcast Messages** - Send to all users at once
- **Per-User Scheduling** - Each user can set their own schedule
- **Independent Progress** - Each user has separate tracking
- **No Login Required** - Direct access to admin dashboard

## 📚 Features

- **Daily Automated Video Delivery** via Telegram
- **Completion Tracking** with interactive buttons
- **Study Streak Management** for motivation
- **Multi-User Admin Dashboard** for monitoring all users
- **Automated Scheduling** with per-user time settings
- **Zero-Cost Architecture** using free-tier services

## 🏗️ Architecture

- **Frontend**: React + Vite (Modern, responsive UI)
- **Backend**: FastAPI + Python (Multi-user API)
- **Database**: SQLite (Multi-user schema)
- **Bot**: Telegram Bot API (User registration)
- **Scheduler**: Background Python process (Automated sends)

## 🚀 Quick Start (3 Commands)

### 1. Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your bot token
uvicorn main:app --reload
```

### 2. Start Bot (New Terminal)
```bash
cd backend
source venv/bin/activate
python bot_simple.py
```

### 3. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

**Access:** http://localhost:5173

## 📱 Register Users

1. Open Telegram
2. Search for your bot (e.g., @OfficerPriyaBot)
3. Send `/start`
4. Refresh dashboard - you're in!

## 📖 Full Documentation

- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete setup guide
- **[MULTI_USER_GUIDE.md](MULTI_USER_GUIDE.md)** - Multi-user features
- **[DASHBOARD_UPDATE.md](DASHBOARD_UPDATE.md)** - Dashboard usage

## 🚀 Quick Start (Old)

### Backend Setup

1. Install dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and chat ID
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your backend URL
```

3. Run the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`

## 📱 Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Add both to `backend/.env`

## 🔧 Configuration

### Playlist URLs

The system uses these YouTube playlists by default:
- **English**: https://www.youtube.com/playlist?list=PLhrq-fv7kVgeyGNN5Y4p2iuNd5hLIPUST
- **History**: https://www.youtube.com/playlist?list=PL3M0QAJjbrLhhy-PKTB3T2ZoA41ptNsfl
- **Polity**: https://www.youtube.com/playlist?list=PL3M0QAJjbrLj0dI6wXZad0C0qNrIhuH_W
- **Geography**: https://www.youtube.com/playlist?list=PL3M0QAJjbrLgfkfZlkaZnmQoJhXOL1c_V
- **Economics**: https://www.youtube.com/playlist?list=PL3M0QAJjbrLhs6obUK9RiZ2JKnOMvSzWh

You can modify these through the admin dashboard.

## 📊 API Endpoints

### Daily Operations
- `POST /api/send-daily` - Send daily videos
- `POST /api/telegram/webhook` - Handle Telegram callbacks

### Dashboard
- `GET /api/dashboard/metrics` - Get progress metrics
- `GET /api/dashboard/logs` - Get daily logs

### Configuration
- `GET /api/config/playlists` - Get playlist URLs
- `PUT /api/config/playlists` - Update playlist URL

### Admin
- `POST /api/admin/reset` - Reset all progress
- `POST /api/admin/send-now` - Manually trigger daily send

## 🌐 Deployment

### Backend (Render)

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `DATABASE_PATH`

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
4. Add environment variable:
   - `VITE_API_BASE_URL` (your Render backend URL)

### GitHub Actions

1. Go to repository Settings → Secrets
2. Add secret:
   - `BACKEND_URL` (your Render backend URL)
3. The workflow in `.github/workflows/daily-send.yml` will run daily at 6 AM UTC

## 🎯 Usage

### For Students (Officer Priya)

1. Receive daily Telegram message with study videos
2. Watch the videos
3. Click ✅ Done or ❌ Not Done
4. Track your streak and stay motivated!

### For Administrators

1. Open the admin dashboard
2. View metrics: current day, completion %, streak
3. Review daily logs
4. Modify playlists if needed
5. Reset progress or manually send messages

## 🔒 Security Notes

- Never commit `.env` files
- Keep your Telegram bot token secret
- Use environment variables for sensitive data
- Enable CORS only for trusted domains in production

## 📝 License

MIT License - feel free to use and modify for your needs!

## 👨‍💻 Developer

Lakshay Singh  
Officer Preparation Automation System v1.0

---

**Good luck with your CDS OTA preparation! 🎖️**
