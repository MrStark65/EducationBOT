# 🚀 Deploy Now - Quick Guide

## ⚡ Fastest Way: Railway (5 Minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Click "Deploy Now"

### Step 3: Add Environment Variable
1. Click on your project
2. Go to "Variables" tab
3. Add: `TELEGRAM_BOT_TOKEN` = `your_bot_token`
4. Click "Add"

### Step 4: Get Your URL
1. Go to "Settings" tab
2. Click "Generate Domain"
3. Copy the URL (e.g., `https://your-app.up.railway.app`)

### Step 5: Deploy Frontend to Vercel
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Set Root Directory: `frontend`
5. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://your-app.up.railway.app`
6. Click "Deploy"

### Step 6: Test!
1. Open your Vercel URL
2. Send `/start` to your bot on Telegram
3. Refresh dashboard - you're live! 🎉

---

## 🎯 Alternative: Render (More Control)

### Backend (3 Services)

#### Service 1: API
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Name: `officer-priya-api`
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add env: `TELEGRAM_BOT_TOKEN`

#### Service 2: Bot
1. New → Background Worker
2. Connect same repo
3. Settings:
   - Name: `officer-priya-bot`
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `python bot_simple.py`
   - Add env: `TELEGRAM_BOT_TOKEN`

#### Service 3: Scheduler
1. New → Background Worker
2. Connect same repo
3. Settings:
   - Name: `officer-priya-scheduler`
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `python multi_user_scheduler.py`
   - Add env: `TELEGRAM_BOT_TOKEN`

### Frontend (Vercel)
Same as Railway method above!

---

## 📋 Pre-Deployment Checklist

- [ ] Git repository created
- [ ] Code pushed to GitHub
- [ ] Telegram bot token ready
- [ ] `.env` files NOT committed (in .gitignore)
- [ ] All dependencies in requirements.txt
- [ ] Frontend builds locally (`npm run build`)
- [ ] Backend runs locally (`uvicorn main:app`)

---

## 🔍 Verify Deployment

### Check Backend
```bash
curl https://your-api-url.com/api/health
```
Should return: `{"status":"healthy"}`

### Check Bot
1. Open Telegram
2. Send `/start` to bot
3. Should receive welcome message

### Check Dashboard
1. Open your Vercel URL
2. Should see dashboard
3. Click user selector
4. Should see registered users

### Check Scheduler
1. Set schedule in dashboard
2. Enable automation
3. Wait for scheduled time
4. Check Telegram for message

---

## 🐛 Common Issues

### "Application Error" on Railway
- Check logs in Railway dashboard
- Verify environment variables
- Ensure requirements.txt is complete

### Bot Not Responding
- Verify bot token is correct
- Check bot worker is running
- Look at worker logs

### Frontend Can't Connect to API
- Check CORS settings in backend
- Verify API URL in frontend env
- Check API is running

### Database Resets
- Free tier may reset on sleep
- Upgrade to paid tier for persistence
- Or use external PostgreSQL

---

## 💡 Tips

1. **Test Locally First**
   - Run all services locally
   - Verify everything works
   - Then deploy

2. **Monitor Logs**
   - Check Railway/Render logs regularly
   - Look for errors
   - Monitor performance

3. **Use Environment Variables**
   - Never commit secrets
   - Use platform env vars
   - Keep .env in .gitignore

4. **Auto-Deploy**
   - Push to GitHub
   - Platforms auto-deploy
   - No manual steps needed

---

## 🎉 Success!

Once deployed, share with users:

```
🎖️ Officer Priya CDS System is LIVE!

📱 Telegram Bot: @YourBotName
🌐 Dashboard: https://your-app.vercel.app

How to use:
1. Send /start to the bot
2. Open dashboard
3. Get daily study videos!
```

---

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs

**Your bot is ready to go live! 🚀**
