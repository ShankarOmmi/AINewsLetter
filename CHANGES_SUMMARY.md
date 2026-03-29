# 🚀 Railway Deployment - Summary of Changes

## Files Modified for Production

### 1. **config.py** ✅
Added environment variables for production deployment:
```python
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///newsletter.db")
EMAIL_FROM = os.getenv("EMAIL_FROM", "newsletter@shankarommi.in")
APPROVAL_EMAIL = os.getenv("APPROVAL_EMAIL", "n200179@rguktn.ac.in")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
```

### 2. **main.py** ✅
- Imports `BASE_URL`, `APPROVAL_EMAIL` from config
- Replaced hardcoded `http://localhost:8000` with `BASE_URL`
- Replaced hardcoded email `n200179@rguktn.ac.in` with `APPROVAL_EMAIL`
- Updated `save_edition()` to work with both SQLite and PostgreSQL

### 3. **api/router.py** ✅
- Imports `BASE_URL` and `APPROVAL_EMAIL` from config
- Replaced hardcoded localhost URL with `BASE_URL` variable
- Updated SQL queries to work with both databases (SQLite `?` and PostgreSQL `%s`)

### 4. **db/database.py** ✅
**Major upgrade:** Now supports both SQLite (local) and PostgreSQL (production):
- Detects which DB to use via `DATABASE_URL` environment variable
- If `DATABASE_URL` contains `postgresql`:
  - Uses psycopg2 for PostgreSQL connection
  - Creates PostgreSQL-compatible tables (SERIAL, RETURNING)
- If `DATABASE_URL` not set or local:
  - Falls back to SQLite (existing behavior)
  - Maintains backward compatibility

### 5. **db/models.py** ✅
Updated all SQL queries to work with both databases:
- Uses `%s` placeholder for PostgreSQL
- Uses `?` placeholder for SQLite
- Automatically detects which to use via `IS_POSTGRES` flag

### 6. **emailer/send.py** ✅
- `EMAIL_FROM` is now configurable from environment
- Was hardcoded: `"newsletter@shankarommi.in"`
- Now: `EMAIL_FROM = os.getenv("EMAIL_FROM", "...")`

### 7. **requirements.txt** ✅
Added production dependencies:
- `gunicorn` - Production WSGI server
- `psycopg2-binary` - PostgreSQL driver
- `uvicorn[standard]` - Enhanced Uvicorn with more features

### 8. **Procfile** (NEW) ✅
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT main:app
```
Tells Railway how to start the app with 4 workers on the assigned PORT.

### 9. **.env.example** (NEW) ✅
Template file showing all required environment variables - helps with configuration.

### 10. **RAILWAY_DEPLOYMENT.md** (NEW) ✅
Complete step-by-step deployment guide (read this carefully!).

### 11. **DEPLOYMENT_CHECKLIST.md** (NEW) ✅
Interactive checklist for deployment (use while deploying).

---

## Environment-Specific Behavior

### 🏠 **Local Development** (No DATABASE_URL set)
```
App uses: SQLite (newsletter.db)
Location: Your laptop
Command: python main.py or uvicorn main:app --reload
```

### ☁️ **Railway Production** (DATABASE_URL set to PostgreSQL)
```
App uses: PostgreSQL
Location: Railway servers
Command: gunicorn (via Procfile)
```

---

## 🚨 IMPORTANT: Disable Test Scheduler for Production

The test scheduler runs the newsletter job **every 2 minutes**. This is for testing only!

### Location: `main.py` lines ~217-220

**Current code:**
```python
# Weekly (Monday 8 AM)
scheduler.add_job(run_newsletter_job, "cron", day_of_week="mon", hour=8, minute=0)

# TEST MODE (comment later)
scheduler.add_job(run_newsletter_job, "interval", minutes=2)  # ⚠️ REMOVE THIS!
```

**What you MUST do before deploying to production:**

Option A - Comment it out:
```python
# Weekly (Monday 8 AM)
scheduler.add_job(run_newsletter_job, "cron", day_of_week="mon", hour=8, minute=0)

# TEST MODE (comment later)
# scheduler.add_job(run_newsletter_job, "interval", minutes=2)
```

Option B - Use environment variable:
```python
# TEST MODE (only enable in development)
if os.getenv("ENABLE_TEST_SCHEDULER") == "true":
    scheduler.add_job(run_newsletter_job, "interval", minutes=2)
```

---

## Backward Compatibility ✅

All changes are **backward compatible**:
- ✅ Local SQLite still works (no DATABASE_URL needed)
- ✅ Existing `.env` files still work
- ✅ All endpoints remain the same
- ✅ Database schema is the same

---

## Quick Start on Railway

1. **Commit & Push**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push
   ```

2. **Create Railway Project**
   - Go to railway.app → New Project
   - Select "Deploy from GitHub"
   - Select your repository

3. **Add PostgreSQL Service**
   - Railway → Create → PostgreSQL
   - Copy the connection string

4. **Configure Variables**
   - In web service, add environment variables from DEPLOYMENT_CHECKLIST.md
   - Set `DATABASE_URL` to PostgreSQL connection string
   - Set `BASE_URL` to your Railway app URL

5. **Deploy**
   - Push code → Railway auto-deploys
   - Check logs for any errors
   - Test endpoints

---

## Testing Before Railway

**Test locally with all changes:**
```bash
# Install dependencies
pip install -r requirements.txt

# Test with SQLite (default)
python main.py

# Test subscription endpoint
curl -X POST http://localhost:8000/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## Next Steps

1. **Read**: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Full guide
2. **Follow**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step
3. **Configure**: Environment variables as per checklist
4. **Deploy**: Push to Git → Railway auto-deploys
5. **Monitor**: Watch logs in Railway dashboard

---

**Questions? Check:**
- 📖 RAILWAY_DEPLOYMENT.md for detailed instructions
- 📋 DEPLOYMENT_CHECKLIST.md for what to verify
- 🔗 railway.app/docs for Railway specific help
