# 🚀 Terminal Deployment Guide

Deploy your entire project using only terminal commands!

## 📋 Prerequisites

Install required CLIs:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Install Vercel CLI
npm install -g vercel

# Verify installations
railway --version
vercel --version
```

---

## 🎯 Step 1: Prepare Your Project

### 1.1 Initialize Git (if not already)
```bash
# Check if git is initialized
git status

# If not, initialize
git init
git add .
git commit -m "Initial commit for deployment"
```

### 1.2 Create GitHub Repository
```bash
# Install GitHub CLI (optional but recommended)
brew install gh  # macOS
# OR
# Go to github.com and create repo manually

# Login to GitHub CLI
gh auth login

# Create repository
gh repo create officer-priya-bot --public --source=. --remote=origin --push
```

---

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Login to Railway
```bash
railway login
```
This will open a browser for authentication.

### 2.2 Create New Project
```bash
# Create project
railway init

# When prompted:
# - Project name: officer-priya-bot
# - Select: Empty Project
```

### 2.3 Link to GitHub (Optional)
```bash
railway link
```

### 2.4 Add Environment Variables
```bash
# Add bot token
railway variables set TELEGRAM_BOT_TOKEN=your_bot_token_here

# Add Python version
railway variables set PYTHON_VERSION=3.11.0

# Verify variables
railway variables
```

### 2.5 Deploy Backend
```bash
# Deploy from backend directory
cd backend

# Create railway.toml for configuration
cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT & python bot_simple.py & python multi_user_scheduler.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
EOF

# Deploy
railway up

# Get your deployment URL
railway domain
```

### 2.6 Generate Public Domain
```bash
# Generate a public URL
railway domain

# Copy the URL (e.g., officer-priya-bot.up.railway.app)
```

---

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Login to Vercel
```bash
vercel login
```

### 3.2 Navigate to Frontend
```bash
cd ../frontend
```

### 3.3 Update Environment Variable
```bash
# Create production env file
echo "VITE_API_BASE_URL=https://your-railway-url.up.railway.app" > .env.production

# Replace 'your-railway-url' with your actual Railway URL
```

### 3.4 Deploy to Vercel
```bash
# Deploy (first time)
vercel

# When prompted:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? officer-priya-bot
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

### 3.5 Add Environment Variable via CLI
```bash
# Add production environment variable
vercel env add VITE_API_BASE_URL production

# When prompted, paste your Railway URL:
# https://your-railway-url.up.railway.app

# Redeploy with new env
vercel --prod
```

---

## ✅ Step 4: Verify Deployment

### 4.1 Test Backend
```bash
# Get Railway URL
RAILWAY_URL=$(railway domain)

# Test health endpoint
curl https://$RAILWAY_URL/api/health

# Should return: {"status":"healthy","timestamp":"..."}
```

### 4.2 Test API Endpoints
```bash
# Test users endpoint
curl https://$RAILWAY_URL/api/admin/users

# Should return: {"users":[],"total":0}
```

### 4.3 Test Frontend
```bash
# Get Vercel URL
VERCEL_URL=$(vercel inspect --json | jq -r '.url')

# Open in browser
open https://$VERCEL_URL
# OR on Linux:
xdg-open https://$VERCEL_URL
```

### 4.4 Test Telegram Bot
```bash
# Test bot via Telegram
# 1. Open Telegram
# 2. Search for your bot
# 3. Send /start
# 4. Should receive welcome message
```

---

## 🔄 Step 5: Update and Redeploy

### Update Backend
```bash
cd backend

# Make changes to your code
# ...

# Commit changes
git add .
git commit -m "Update backend"
git push

# Redeploy to Railway
railway up

# Or if linked to GitHub, Railway auto-deploys on push
```

### Update Frontend
```bash
cd frontend

# Make changes to your code
# ...

# Commit changes
git add .
git commit -m "Update frontend"
git push

# Redeploy to Vercel
vercel --prod

# Or Vercel auto-deploys on push to main branch
```

---

## 📊 Step 6: Monitor Your Deployment

### View Railway Logs
```bash
# View live logs
railway logs

# View logs for specific service
railway logs --service web
```

### View Vercel Logs
```bash
# View deployment logs
vercel logs

# View production logs
vercel logs --prod
```

### Check Railway Status
```bash
# Get project info
railway status

# List all services
railway service
```

---

## 🛠️ Useful Commands

### Railway Commands
```bash
# View all projects
railway list

# Switch project
railway link

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# Delete environment variable
railway variables delete KEY

# Open dashboard
railway open

# View logs
railway logs

# Restart service
railway restart
```

### Vercel Commands
```bash
# List all deployments
vercel list

# View project info
vercel inspect

# View domains
vercel domains

# Add domain
vercel domains add yourdomain.com

# View environment variables
vercel env ls

# Pull environment variables
vercel env pull

# Remove deployment
vercel remove [deployment-url]
```

---

## 🔐 Environment Variables Management

### Railway - Add Multiple Variables
```bash
# Create .env file (don't commit!)
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_token_here
PYTHON_VERSION=3.11.0
DATABASE_URL=your_db_url_here
EOF

# Load from .env file
railway variables set $(cat .env | xargs)
```

### Vercel - Add Multiple Variables
```bash
# Add environment variables
vercel env add VITE_API_BASE_URL production
vercel env add VITE_ANOTHER_VAR production

# Or use vercel.json
cat > vercel.json << 'EOF'
{
  "env": {
    "VITE_API_BASE_URL": "https://your-api.up.railway.app"
  }
}
EOF
```

---

## 🐛 Troubleshooting

### Railway Deployment Failed
```bash
# Check logs
railway logs

# Check build logs
railway logs --build

# Restart service
railway restart

# Check variables
railway variables
```

### Vercel Deployment Failed
```bash
# Check logs
vercel logs

# Check build logs
vercel inspect

# Redeploy
vercel --prod --force
```

### Can't Connect to API
```bash
# Check if Railway is running
railway status

# Check Railway URL
railway domain

# Test API directly
curl https://your-railway-url.up.railway.app/api/health

# Check CORS settings in backend/main.py
```

---

## 🎯 Complete Deployment Script

Create `deploy.sh`:
```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Deploy Backend to Railway
echo -e "${BLUE}📦 Deploying backend to Railway...${NC}"
cd backend
railway up
RAILWAY_URL=$(railway domain)
echo -e "${GREEN}✅ Backend deployed: $RAILWAY_URL${NC}"

# Step 2: Update Frontend Environment
echo -e "${BLUE}🔧 Updating frontend environment...${NC}"
cd ../frontend
echo "VITE_API_BASE_URL=https://$RAILWAY_URL" > .env.production

# Step 3: Deploy Frontend to Vercel
echo -e "${BLUE}🎨 Deploying frontend to Vercel...${NC}"
vercel --prod --yes
VERCEL_URL=$(vercel inspect --json | jq -r '.url')
echo -e "${GREEN}✅ Frontend deployed: https://$VERCEL_URL${NC}"

# Step 4: Test Deployment
echo -e "${BLUE}🧪 Testing deployment...${NC}"
curl -s https://$RAILWAY_URL/api/health | jq

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "Backend: https://$RAILWAY_URL"
echo -e "Frontend: https://$VERCEL_URL"
echo -e "API Docs: https://$RAILWAY_URL/docs"
```

Make it executable and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📱 Share Your Live App

After deployment, share these URLs:

```bash
# Get URLs
RAILWAY_URL=$(railway domain)
VERCEL_URL=$(vercel inspect --json | jq -r '.url')

# Print share message
echo "
🎖️ Officer Priya CDS System is LIVE!

📱 Telegram Bot: @YourBotName
🌐 Dashboard: https://$VERCEL_URL
🔧 API: https://$RAILWAY_URL
📚 API Docs: https://$RAILWAY_URL/docs

How to use:
1. Send /start to @YourBotName on Telegram
2. Open dashboard at https://$VERCEL_URL
3. Get daily study videos automatically!
"
```

---

## 🎉 Success Checklist

- [ ] Railway CLI installed
- [ ] Vercel CLI installed
- [ ] Logged into both platforms
- [ ] Backend deployed to Railway
- [ ] Environment variables set
- [ ] Frontend deployed to Vercel
- [ ] API URL updated in frontend
- [ ] Health check passes
- [ ] Bot responds to /start
- [ ] Dashboard loads
- [ ] Can register users
- [ ] Can send messages

**Your app is now LIVE! 🚀**
