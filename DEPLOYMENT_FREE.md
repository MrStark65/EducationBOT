# Free Deployment Guide

Deploy your Officer Priya bot completely free using Render.com + Vercel.

## Prerequisites
- GitHub account
- Render.com account (free)
- Vercel account (free)

## Step 1: Deploy Backend on Render.com

1. **Go to Render.com**
   - Visit https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `MrStark65/EducationBOT`
   - Render will auto-detect `render.yaml`

3. **Configure Environment Variables**
   Click "Environment" and add:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ADMIN_PASSWORD=your_admin_password_here
   ```

4. **Create Database**
   - Render will auto-create PostgreSQL database from `render.yaml`
   - Database URL will be auto-injected as `DATABASE_URL`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note your backend URL: `https://officer-priya-backend.onrender.com`

## Step 2: Deploy Frontend on Vercel

1. **Go to Vercel**
   - Visit https://vercel.com
   - Sign up/Login with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import `MrStark65/EducationBOT`

3. **Configure Build Settings**
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variable**
   ```
   VITE_API_BASE_URL=https://officer-priya-backend.onrender.com
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend URL: `https://your-app.vercel.app`

## Step 3: Update Telegram Bot Webhook (Optional)

If you want to use webhooks instead of polling:

1. Go to your Render backend URL
2. Call: `https://officer-priya-backend.onrender.com/set-webhook`

## Important Notes

### Free Tier Limitations

**Render.com:**
- 750 hours/month (enough for 24/7 if only 1 service)
- Spins down after 15 minutes of inactivity
- Takes 30-60 seconds to wake up on first request
- 512 MB RAM
- PostgreSQL: 1 GB storage

**Vercel:**
- Unlimited bandwidth
- 100 GB bandwidth/month
- Serverless functions (not used in this setup)

### Database Migration

Your local SQLite database needs to be migrated to PostgreSQL:

1. **Automatic Migration**
   - Render will run migrations automatically on first deploy
   - All tables will be created from scratch

2. **Manual Data Import** (if you want to keep existing data)
   - Export SQLite data: `sqlite3 backend/officer_priya_multi.db .dump > data.sql`
   - Convert to PostgreSQL format
   - Import to Render database

### Keeping Backend Alive

Free tier spins down after 15 min inactivity. To keep it alive:

1. **Use a Cron Job Service** (free)
   - https://cron-job.org
   - Ping your backend every 10 minutes: `https://officer-priya-backend.onrender.com/health`

2. **Or use UptimeRobot** (free)
   - https://uptimerobot.com
   - Monitor your backend URL

## Troubleshooting

### Backend not starting
- Check Render logs: Dashboard → Logs
- Verify all environment variables are set
- Check database connection

### Frontend can't connect to backend
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in backend
- Ensure backend is running (not spun down)

### Bot not responding
- Check Render logs for errors
- Verify Telegram bot token is correct
- Ensure backend is awake (ping /health endpoint)

## Cost Breakdown

- **Backend (Render)**: $0/month (free tier)
- **Database (Render)**: $0/month (free tier)
- **Frontend (Vercel)**: $0/month (free tier)
- **Total**: $0/month 🎉

## Upgrading Later

If you need more resources:
- **Render**: $7/month for 24/7 uptime + more RAM
- **Vercel**: Free tier is usually enough for frontend
- **Database**: $7/month for 10 GB storage

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Issues: https://github.com/MrStark65/EducationBOT/issues
