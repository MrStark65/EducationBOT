# Render Data Import Guide

## Problem
Render free tier uses ephemeral storage - the SQLite database resets on every restart/redeploy.

## Solution
Import data from `database_export.sql` after each restart to restore user progress.

---

## Current Data State (March 1, 2026)

### Users
- **Priya** (5809062020): Day 2, Streak 🔥 2, English #2, History #1
- **Lakshay** (1913237845): Day 1, Streak 🔥 0, English #1, History #1

### Day 1 Delivery (March 1, 06:00 AM)
- ✅ English Video #1 + History Video #1 sent to both users
- ✅ Priya completed → Streak increased to 1
- ❌ Lakshay did not complete → Streak stayed at 0

### Global State
- Current Day: 2
- Next delivery: Day 2 content (English #2 + Polity #1) on Monday March 2, 06:00 AM

---

## Method 1: Import via Render Shell (Recommended)

### Step 1: Access Render Shell
1. Go to https://dashboard.render.com
2. Select your service: `officer-priya-backend`
3. Click **Shell** tab (top right)
4. Wait for shell to connect

### Step 2: Run Import Script
```bash
cd /opt/render/project/src/backend
python3 import_data.py
```

### Step 3: Verify Import
You should see:
```
✅ IMPORT COMPLETE
📊 DATABASE CONTENTS:
   Users: 2
   Configs: 2
   Daily logs: 2
   Schedules: 6

👥 USER STATUS:
   Priya (5809062020): Day 2, Streak 🔥 2, English #2, History #1
   Lakshay (1913237845): Day 1, Streak 🔥 0, English #1, History #1
```

### Step 4: Restart Service
```bash
# Exit shell (Ctrl+D or type 'exit')
# Then click "Manual Deploy" → "Clear build cache & deploy"
```

---

## Method 2: Automatic Import on Startup

### Update render.yaml
Add import command to startup:

```yaml
services:
  - type: web
    name: officer-priya-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && python3 import_data.py && python3 main.py"
```

This will automatically import data every time the service starts.

---

## Method 3: Manual SQL Import

### Step 1: Access Render Shell
```bash
cd /opt/render/project/src/backend
sqlite3 officer_priya_multi.db
```

### Step 2: Run SQL Commands
```sql
-- Copy and paste contents from database_export.sql
-- Or use:
.read database_export.sql
.quit
```

---

## Verify Data After Import

### Check via API
```bash
curl https://officer-priya-backend.onrender.com/api/admin/users
```

### Check via Frontend
1. Go to https://cdsbot.netlify.app
2. Login with admin credentials
3. Check Analytics Dashboard:
   - Priya should show: Day 2, Streak 🔥 2
   - Lakshay should show: Day 1, Streak 🔥 0

### Check via Bot
Send `/stats` to @OfficerPriyaBot:
- Priya should see: "Day 2, Streak 🔥 2"
- Lakshay should see: "Day 1, Streak 🔥 0"

---

## When to Import

### Required:
- ✅ After service restart
- ✅ After redeploy
- ✅ After database reset

### Not Required:
- ❌ During normal operation (data persists in memory)
- ❌ After cron job health check (doesn't restart service)

---

## Troubleshooting

### Import Script Not Found
```bash
# Check current directory
pwd
# Should be: /opt/render/project/src

# Navigate to backend
cd backend
ls -la import_data.py
```

### Permission Denied
```bash
chmod +x import_data.py
python3 import_data.py
```

### Database Locked
```bash
# Stop the service first
# Then run import
# Then restart service
```

### Wrong Data After Import
```bash
# Delete database and reimport
rm officer_priya_multi.db
python3 import_data.py
```

---

## Update SQL File for Future Days

When Priya completes Day 2, update `database_export.sql`:

```sql
-- Update Priya's config
UPDATE user_config SET day_count=3, streak=3, english_index=3 WHERE user_id=2;

-- Add Day 2 log
INSERT INTO user_daily_logs (user_id, day_number, date, status) 
VALUES (2, 2, '2026-03-02', 'DONE');
```

---

## Alternative: PostgreSQL Migration

For permanent storage without manual imports, migrate to PostgreSQL:
- See `POSTGRESQL_MIGRATION.md` for full guide
- PostgreSQL on Render has persistent storage
- No data loss on restart
- Free tier available until March 31, 2026

---

## Quick Reference

| Action | Command |
|--------|---------|
| Import data | `python3 import_data.py` |
| Check database | `sqlite3 officer_priya_multi.db` |
| View users | `SELECT * FROM users;` |
| View configs | `SELECT * FROM user_config;` |
| View logs | `SELECT * FROM user_daily_logs;` |
| Exit SQLite | `.quit` |
| Restart service | Manual Deploy button |

---

## Notes

- Import is idempotent (safe to run multiple times)
- Uses `ON CONFLICT DO NOTHING` to avoid duplicates
- Preserves existing data if already present
- Takes ~2 seconds to complete
- No downtime required
