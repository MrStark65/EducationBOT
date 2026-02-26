# Officer Priya CDS System - Complete Documentation

## 📚 Table of Contents
1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Features](#features)
4. [API Documentation](#api-documentation)
5. [Frontend Guide](#frontend-guide)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Telegram Bot Token

### Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Configuration

Create `backend/.env`:
```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI (Optional)
GROQ_API_KEY=your_groq_api_key_here

# Authentication
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Running

**Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Start Scheduler:**
```bash
cd backend
source venv/bin/activate
python multi_user_scheduler.py
```

Access dashboard at: http://localhost:5174

---

## 🎯 System Overview

### Architecture
- **Backend:** FastAPI (Python)
- **Frontend:** React + Vite
- **Database:** SQLite
- **Bot:** python-telegram-bot
- **AI:** Groq (Llama 3.3 70B)

### Key Components
1. **Multi-User System** - Global mode for all users
2. **Scheduler** - Automated daily content delivery
3. **Admin Dashboard** - Web-based management
4. **Telegram Bot** - User interaction
5. **AI Assistant** - Intelligent responses

---

## ✨ Features

### Core Features
✅ Automated daily video delivery
✅ Multi-subject support (English, History, Polity, Geography, Economics)
✅ Playlist scheduling per subject
✅ Progress tracking and streaks
✅ Completion status (Done/Not Done)
✅ File management (upload/download PDFs)

### Security Features
✅ JWT authentication
✅ Password hashing (bcrypt)
✅ Rate limiting (60/min, 1000/hour)
✅ Input validation
✅ Protected admin endpoints

### User Management
✅ Block/unblock users
✅ User analytics (completion rate, streaks)
✅ Activity logging
✅ System-wide statistics

### Analytics
✅ Real-time dashboard
✅ Leaderboards (top performers, streak leaders)
✅ System metrics
✅ Per-user detailed analytics

### AI Integration
✅ Natural language responses
✅ Personalized motivation
✅ Subject-specific study tips
✅ Context-aware conversations

---

## 📡 API Documentation

### Authentication

**Login:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response: { "access_token": "...", "token_type": "bearer" }
```

**Verify Token:**
```http
POST /api/auth/verify
Authorization: Bearer <token>
```

### User Management

**Get All Users:**
```http
GET /api/admin/users
Authorization: Bearer <token>
```

**Block User:**
```http
POST /api/admin/users/{chat_id}/block
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "Spam or abuse"
}
```

**Unblock User:**
```http
POST /api/admin/users/{chat_id}/unblock
Authorization: Bearer <token>
```

**Get User Analytics:**
```http
GET /api/admin/users/{chat_id}/analytics
Authorization: Bearer <token>
```

### Analytics

**System Analytics:**
```http
GET /api/admin/analytics/system
Authorization: Bearer <token>

Response:
{
  "total_users": 100,
  "active_users": 75,
  "blocked_users": 5,
  "total_completions": 2500,
  "average_completion_rate": 85.5
}
```

**All Users Analytics:**
```http
GET /api/admin/analytics/all-users
Authorization: Bearer <token>
```

### Schedule Management

**Get Schedule:**
```http
GET /api/config/schedule
```

**Update Schedule:**
```http
PUT /api/config/schedule
Content-Type: application/json

{
  "enabled": true,
  "time": "09:00"
}
```

### Playlist Management

**Get Playlists:**
```http
GET /api/config/playlists
```

**Update Playlist:**
```http
PUT /api/config/playlists
Content-Type: application/json

{
  "subject": "english",
  "url": "https://youtube.com/playlist?list=..."
}
```

### File Management

**List Files:**
```http
GET /api/files?limit=100&type=pdf
Authorization: Bearer <token>
```

**Upload File:**
```http
POST /api/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

**Download File:**
```http
GET /api/files/{file_id}/download
Authorization: Bearer <token>
```

---

## 🎨 Frontend Guide

### Components

**Dashboard** - System overview with stats
**Analytics** - Leaderboards and performance metrics
**Schedule** - Configure daily send time
**Playlists** - Manage subject playlists
**Files** - Upload and manage documents
**Users** - View all registered users
**User Management** - Block/unblock, view analytics
**System** - System information and errors

### Navigation

```
📊 Dashboard
📈 Analytics
⏰ Schedule
📚 Playlists
📁 File Library
👥 Users
🛡️ User Management
⚙️ System
```

### Design Theme

**Dastone Premium:**
- Primary: Royal Blue #3B82F6
- Accent: Purple #8B5CF6
- Success: Green #10B981
- Warning: Orange #F59E0B
- Danger: Red #EF4444

**Typography:**
- Font: Inter/Poppins
- Headings: 700 weight
- Body: 400 weight

**Components:**
- Cards: 16px radius, soft shadow
- Buttons: 8px radius, gradient
- Modals: 16px radius, overlay

---

## 🚀 Deployment

### Backend (Render)

1. Create new Web Service
2. Connect GitHub repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Frontend (Vercel/Netlify)

1. Connect GitHub repository
2. Build Command: `npm run build`
3. Output Directory: `dist`
4. Add environment variable: `VITE_API_URL`

### Environment Variables

**Backend:**
```env
TELEGRAM_BOT_TOKEN=<your_token>
GROQ_API_KEY=<your_key>
JWT_SECRET_KEY=<generate_secure_key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<change_this>
```

**Frontend:**
```env
VITE_API_URL=https://your-backend-url.com
```

### Database

SQLite database will be created automatically. For production, consider:
- Regular backups (built-in backup system)
- Persistent storage volume
- Database replication

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check .env file exists
- Ensure port 8000 is available

**Frontend won't start:**
- Check Node version (16+)
- Run `npm install` again
- Clear node_modules and reinstall
- Check VITE_API_URL is set

**Telegram bot not responding:**
- Verify bot token is correct
- Check bot is running
- Ensure webhook is not set (use polling)
- Check network connectivity

**Authentication failing:**
- Verify JWT_SECRET_KEY is set
- Check password is correct
- Clear browser localStorage
- Generate new token

**Rate limit errors:**
- Wait 1 minute before retrying
- Reduce request frequency
- Check if IP is correct

**Database errors:**
- Check database file exists
- Verify file permissions
- Run migrations if needed
- Check disk space

### Logs

**Backend logs:**
- `backend/logs/app.log` - Application logs
- `backend/logs/api.log` - API request logs
- `backend/logs/errors.db` - Error database

**View recent errors:**
```bash
sqlite3 backend/logs/errors.db "SELECT * FROM error_logs ORDER BY created_at DESC LIMIT 10;"
```

**Clear old errors:**
```bash
sqlite3 backend/logs/errors.db "DELETE FROM error_logs WHERE created_at < datetime('now', '-30 days');"
```

### Reset System

**Reset all progress:**
```http
POST /api/admin/reset-global
Authorization: Bearer <token>
```

**Reset user password:**
```python
from auth import get_auth_manager
auth = get_auth_manager()
auth.change_password('admin', 'old_password', 'new_password')
```

---

## 📞 Support

### Documentation Files
- `README.md` - Project overview
- `HOW_TO_RUN.md` - Detailed setup guide
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `AI_INTEGRATION_GUIDE.md` - AI features guide
- `FRONTEND_UPDATES.md` - Frontend changes
- `NEW_FEATURES.md` - Latest features

### Quick Commands

**Start all services:**
```bash
# Terminal 1 - Backend
bash start-backend.sh

# Terminal 2 - Frontend
bash start-frontend.sh

# Terminal 3 - Scheduler
bash start-scheduler.sh
```

**Run tests:**
```bash
cd backend
pytest
```

**Check system health:**
```bash
curl http://localhost:8000/api/health
```

---

## 🎯 Best Practices

### Security
- Change default admin password immediately
- Use strong JWT secret (32+ characters)
- Enable HTTPS in production
- Regular security audits
- Keep dependencies updated

### Performance
- Enable database indexing
- Use connection pooling
- Implement caching where needed
- Monitor resource usage
- Optimize queries

### Maintenance
- Daily: Check error logs
- Weekly: Review analytics, check disk space
- Monthly: Security audit, update dependencies, backup testing
- Quarterly: Performance review, documentation update

---

**Version:** 2.0.0
**Last Updated:** 2026-02-26
**Status:** Production Ready ✅
