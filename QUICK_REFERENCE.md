# 🚀 Railway Deployment - Quick Reference

## What Changed & Why

Your app was built for **localhost** development. Railway deployment requires:

✅ **Database**: SQLite → PostgreSQL (Railway native)
✅ **URLs**: Hardcoded `http://localhost:8000` → Environment variables  
✅ **Port**: Hardcoded 8000 → Dynamic (Railway assigns PORT)
✅ **Server**: Development (uvicorn) → Production (gunicorn)
✅ **Config**: Hardcoded values → Environment variables

## All Files Modified ✓

| File | Change | Impact |
|------|--------|--------|
| `config.py` | Added env vars | Makes app configurable |
| `main.py` | Uses config vars | Works with Railway |
| `api/router.py` | Uses config vars | Works with Railway |
| `db/database.py` | Dual DB support | Works with SQLite + PostgreSQL |
| `db/models.py` | SQL compatibility | Works with both databases |
| `emailer/send.py` | Configurable email | Works with any email domain |
| `requirements.txt` | Added gunicorn, psycopg2 | Production ready |
| `Procfile` | NEW | Tells Railway how to run app |
| `.env.example` | NEW | Config template |

## 3-Step Deployment

### Step 1: Prepare (5 minutes)
```bash
# Commit changes
git add .
git commit -m "Prepare for Railway deployment"
git push
```

### Step 2: Create on Railway (10 minutes)
1. Go to **railway.app** → Sign up/Login
2. **"New Project"** → Select your GitHub repo
3. **"Create"** → Select branch (main/master)
4. Railway auto-installs dependencies from requirements.txt

### Step 3: Configure Variables (10 minutes)

In Railway dashboard, add these to **Variables** tab:

#### API Keys
```
TAVILY_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
RESEND_API_KEY=your_key_here
```

#### Email Settings  
```
EMAIL_FROM=newsletter@yourdomain.com
APPROVAL_EMAIL=your-email@domain.com
```

#### Database
1. Click **"Create"** in Railway
2. Select **"PostgreSQL"**
3. Copy the `DATABASE_URL` from PostgreSQL service
4. Add it to web service variables

#### Deployment URL
```
BASE_URL=https://your-app-name.up.railway.app
```
(Railway shows the URL after deploying)

**That's it!** Railway auto-deploys when you push code.

## Do This Before Production! 

⚠️ **Comment out test scheduler** in `main.py` line ~220:

```python
# scheduler.add_job(run_newsletter_job, "interval", minutes=2)
```

This runs newsletter every 2 minutes! Only for testing.

Then:
```bash
git add main.py
git commit -m "Disable test scheduler for production"
git push
```

## Verify Deployment

Once deployed, test:

```bash
# Get your Railway URL (shown in dashboard)
RAILWAY_URL=https://your-app-name.up.railway.app

# Test homepage
curl $RAILWAY_URL/

# Test subscription
curl -X POST $RAILWAY_URL/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

Expected response: `{"message": "Subscribed successfully"}`

## Key Differences from Local Dev

| Local (Your Computer) | Railway (Production) |
|---|---|
| `newsletter.db` (SQLite) | PostgreSQL database |
| `http://localhost:8000` | `https://your-domain.up.railway.app` |
| Running via `python main.py` | Running via gunicorn (Procfile) |
| Approval emails → your computer | Approval emails → exact configured email |
| Test scheduler runs every 2 mins | Real scheduler weekly Monday 8 AM |

## Your App Architecture After Deployment

```
┌─────────────────────────────────────┐
│     Your Browser                     │
│  https://your-app.up.railway.app/   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│     Railway Web Service              │
│  (Running Gunicorn + FastAPI)        │
│  - /subscribe                        │
│  - /approve                          │
│  - /reject                           │
│  - Scheduled jobs (Mon 8 AM UTC)     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│     Railway PostgreSQL Database       │
│  - subscribers table                 │
│  - editions table                    │
│  - sends table                       │
└─────────────────────────────────────┘
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| App won't start | Check Logs tab → look for errors |
| "ModuleNotFoundError" | Requirements.txt missing module |
| Database connection fails | Check DATABASE_URL is correct |
| Emails not sending | Verify RESEND_API_KEY and EMAIL_FROM |
| "Port already in use" | Railway handles ports - shouldn't happen |

## Files to Reference

- 📚 **RAILWAY_DEPLOYMENT.md** - Full detailed guide (read if stuck)
- 📋 **DEPLOYMENT_CHECKLIST.md** - Step-by-step checklist while deploying
- 📝 **CHANGES_SUMMARY.md** - What was changed and why
- 📋 **.env.example** - All environment variables you need

## Support

- **Railway Docs**: https://docs.railway.app
- **FastAPI + Railway**: https://docs.railway.app/guides/fastapi
- **This Project**: Feel free to export PostgreSQL backups regularly

## Local Development Still Works ✓

Everything works locally with SQLite:
```bash
. .venv/Scripts/Activate
pip install -r requirements.txt
python main.py
# or
uvicorn main:app --reload
```

No DATABASE_URL needed → uses SQLite automatically.

---

**Ready to deploy? Go to [railway.app](https://railway.app) and start! 🚀**
