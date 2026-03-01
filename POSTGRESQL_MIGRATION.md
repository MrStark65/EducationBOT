# PostgreSQL Migration Guide

## Why Migrate to PostgreSQL?

- ✅ Data persists across restarts
- ✅ No data loss on deployments
- ✅ Free on Render (1GB, 90-day retention)
- ✅ Production-ready
- ✅ Better performance

## Step-by-Step Migration

### 1. Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in:
   - **Name:** `officer-priya-db`
   - **Database:** `officer_priya`
   - **User:** `officer_priya_user`
   - **Region:** Same as your web service (Oregon, USA)
   - **Plan:** **Free**
4. Click **"Create Database"**
5. Wait 2-3 minutes

### 2. Get Database URL

1. Click on your new PostgreSQL database
2. Scroll down to **"Connections"**
3. Copy the **"Internal Database URL"**
   - It looks like: `postgresql://officer_priya_user:xxxxx@dpg-xxxxx/officer_priya`

### 3. Add Database URL to Render Environment

1. Go to your web service: https://dashboard.render.com/web/officer-priya-backend
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste the Internal Database URL you copied)
5. Click **"Save Changes"**

### 4. The System Will Auto-Switch

The code is already set up to detect PostgreSQL:
- If `DATABASE_URL` exists → Uses PostgreSQL ✅
- If not → Uses SQLite (current behavior)

### 5. Deploy

The service will automatically restart and:
1. Detect `DATABASE_URL` environment variable
2. Connect to PostgreSQL instead of SQLite
3. Run migrations to create tables
4. Start fresh with PostgreSQL

### 6. Migrate Existing Data (Optional)

If you want to copy your current SQLite data to PostgreSQL:

```bash
# On your local machine
cd backend
python3 migrate_to_postgres.py
```

This will copy all users, logs, schedules, etc. from SQLite to PostgreSQL.

## What Changes?

### Before (SQLite):
- Data stored in `officer_priya_multi.db` file
- File deleted on restart
- Data lost

### After (PostgreSQL):
- Data stored in Render's PostgreSQL database
- Survives all restarts
- Data persists forever (90 days on free tier)

## Testing

After migration:
1. Register a test user
2. Restart the service (deploy new code)
3. Check if user still exists ✅

## Rollback

To go back to SQLite:
1. Remove `DATABASE_URL` from environment variables
2. Service will use SQLite again

## Notes

- PostgreSQL free tier: 1GB storage, 90-day retention
- After 90 days of inactivity, database is deleted
- Keep the cron job running to prevent deletion
- Upgrade to paid plan ($7/month) for unlimited retention
