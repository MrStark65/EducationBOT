# 🚀 Deployment Guide - Make Your Bot Live!

## Overview

We'll deploy:
- **Backend + Bot + Scheduler** → Render (Free)
- **Frontend** → Vercel (Free)
- **Database** → SQLite on Render (or upgrade to PostgreSQL)

Total Cost: **₹0 (100% Free)**

---

## 🎯 Step 1: Prepare for Deployment

### Update Backend for Production

Create `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
bot: python bot_simple.py
scheduler: python multi_user_scheduler.py
```

### Update requirements.txt
Make sure all dependencies are listed:
```bash
cd backend
pip freeze > requirements.txt
```

---

## 🌐 Step 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Connect your repository

### 2.2 Create Web Service (API)
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `officer-priya-api`
   - **Region**: Singapore (closest to India)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

4. Add Environment Variables:
   - `TELEGRAM_BOT_TOKEN` = your_bot_token
   - `PYTHON_VERSION` = 3.11.0

5. Click "Create Web Service"

### 2.3 Create Background Worker (Bot)
1. Click "New +" → "Background Worker"
2. Connect same repository
3. Configure:
   - **Name**: `officer-priya-bot`
   - **Region**: Singapore
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot_simple.py`
   - **Instance Type**: Free

4. Add same environment variables
5. Click "Create Background Worker"

### 2.4 Create Background Worker (Scheduler)
1. Click "New +" → "Background Worker"
2. Connect same repository
3. Configure:
   - **Name**: `officer-priya-scheduler`
   - **Region**: Singapore
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python multi_user_scheduler.py`
   - **Instance Type**: Free

4. Add same environment variables
5. Click "Create Background Worker"

### 2.5 Note Your API URL
After deployment, you'll get a URL like:
`https://officer-priya-api.onrender.com`

**Save this URL!** You'll need it for the frontend.

---

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Import your repository

### 3.2 Configure Frontend
1. Click "Import Project"
2. Select your repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://officer-priya-api.onrender.com`

5. Click "Deploy"

### 3.3 Get Your Live URL
After deployment, you'll get a URL like:
`https://officer-priya.vercel.app`

**This is your live dashboard!**

---

## 🔧 Step 4: Update Frontend API URL

Update `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://officer-priya-api.onrender.com
```

Commit and push:
```bash
git add .
git commit -m "Add production environment"
git push
```

Vercel will auto-deploy!

---

## ✅ Step 5: Test Your Live System

### 5.1 Test Backend
```bash
curl https://officer-priya-api.onrender.com/api/health
```

Should return: `{"status":"healthy"}`

### 5.2 Test Bot
1. Open Telegram
2. Send `/start` to your bot
3. Should receive welcome message

### 5.3 Test Dashboard
1. Open `https://officer-priya.vercel.app`
2. Should see dashboard
3. Register via Telegram
4. Refresh dashboard - see your profile!

### 5.4 Test Scheduler
1. Set schedule in dashboard
2. Wait for scheduled time
3. Check Telegram for message

---

## 🎯 Alternative: Deploy to Railway (Easier!)

Railway is simpler - one service for everything!

### Railway Deployment

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway auto-detects Python
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `PORT` = 8000

7. Railway gives you a URL automatically!

---

## 🗄️ Database Considerations

### Option 1: SQLite (Current - Simple)
- Works on Render/Railway
- Data persists on disk
- **Limitation**: Resets on free tier restarts

### Option 2: PostgreSQL (Recommended for Production)

#### Update Backend for PostgreSQL

1. Install psycopg2:
```bash
pip install psycopg2-binary
```

2. Update `multi_user_database.py`:
```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if DATABASE_URL:
        # PostgreSQL
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        # SQLite (local)
        conn = sqlite3.connect("officer_priya_multi.db")
        conn.row_factory = sqlite3.Row
    return conn
```

3. Create free PostgreSQL on Render:
   - Click "New +" → "PostgreSQL"
   - Copy "Internal Database URL"
   - Add to environment variables as `DATABASE_URL`

---

## 🔐 Security Best Practices

### 1. Environment Variables
Never commit `.env` files! Use platform environment variables.

### 2. CORS Configuration
Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://officer-priya.vercel.app",
        "http://localhost:5173"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. API Rate Limiting
Add rate limiting to prevent abuse:
```bash
pip install slowapi
```

---

## 📊 Monitoring Your Live System

### Render Dashboard
- View logs for each service
- Monitor uptime
- Check resource usage

### Vercel Dashboard
- View deployment logs
- Monitor traffic
- Check build status

### Telegram Bot
- Test with `/start` command
- Check message delivery
- Monitor button responses

---

## 🐛 Troubleshooting

### Backend Not Starting
1. Check Render logs
2. Verify environment variables
3. Check Python version
4. Verify requirements.txt

### Bot Not Responding
1. Check bot worker logs
2. Verify bot token
3. Ensure worker is running
4. Check Telegram API status

### Frontend Not Loading
1. Check Vercel deployment logs
2. Verify API URL in environment
3. Check CORS settings
4. Test API endpoint directly

### Database Issues
1. Check if database file exists (SQLite)
2. Verify DATABASE_URL (PostgreSQL)
3. Check connection logs
4. Verify migrations ran

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

Both Render and Vercel support auto-deployment:

1. Push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
```

2. Platforms auto-detect and deploy!

### Manual Deploy
- **Render**: Click "Manual Deploy" → "Deploy latest commit"
- **Vercel**: Click "Redeploy"

---

## 💰 Cost Breakdown

### Free Tier Limits

**Render Free Tier:**
- 750 hours/month per service
- 3 services = API + Bot + Scheduler
- Sleeps after 15 min inactivity
- Wakes on request

**Vercel Free Tier:**
- Unlimited deployments
- 100 GB bandwidth/month
- Automatic HTTPS
- Global CDN

**Total Cost: ₹0/month**

### Upgrade Options (Optional)

**Render Starter ($7/month per service):**
- No sleep
- More resources
- Better performance

**Vercel Pro ($20/month):**
- More bandwidth
- Advanced analytics
- Team features

---

## 🎉 Your Live URLs

After deployment, you'll have:

- **Dashboard**: `https://officer-priya.vercel.app`
- **API**: `https://officer-priya-api.onrender.com`
- **API Docs**: `https://officer-priya-api.onrender.com/docs`
- **Bot**: @YourBotName on Telegram

Share the dashboard URL with users!

---

## 📱 Share with Users

Create a simple guide:

```
🎖️ Officer Priya CDS System

1. Open Telegram
2. Search: @OfficerPriyaBot
3. Send: /start
4. Dashboard: https://officer-priya.vercel.app

Daily study videos delivered automatically!
```

---

## 🚀 Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test all features
4. ✅ Share with users
5. ✅ Monitor and maintain

**Your bot is now LIVE! 🎉**
