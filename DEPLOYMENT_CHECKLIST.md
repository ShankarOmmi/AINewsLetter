# Railway Deployment Checklist

Use this checklist as you deploy your AI Newsletter app to Railway.

## ✅ Pre-Deployment Setup

- [ ] All code changes have been made (see RAILWAY_DEPLOYMENT.md)
- [ ] You have all API keys ready:
  - [ ] TAVILY_API_KEY
  - [ ] GROQ_API_KEY  
  - [ ] RESEND_API_KEY
- [ ] Your code is pushed to GitHub/GitLab
- [ ] You have a Railway account (railway.app)

## ✅ Railway Setup Phase

- [ ] Create a new Railway project
- [ ] Add PostgreSQL database service
  - [ ] Copy the PostgreSQL connection string
- [ ] Create web service from your Git repository
  - [ ] Select your GitHub/GitLab repository
  - [ ] Select main/master branch
  - [ ] Railway will auto-detect Python and requirements.txt

## ✅ Environment Variables Configuration

In Railway dashboard, add these variables to your web service:

**API Keys:**
- [ ] `TAVILY_API_KEY` = (your key)
- [ ] `GROQ_API_KEY` = (your key)
- [ ] `RESEND_API_KEY` = (your key)

**Email Configuration:**
- [ ] `EMAIL_FROM` = (your verified Resend domain email)
- [ ] `APPROVAL_EMAIL` = (your email for approvals)

**Database (from PostgreSQL service):**
- [ ] `DATABASE_URL` = (copy from PostgreSQL service variables)

**Deployment:**
- [ ] `BASE_URL` = `https://{your-railway-app-name}.up.railway.app`
  - Railway will show your app name in the service title
  - Or check the "Deployments" tab for the deployed URL

**Port (Optional - Railway sets automatically):**
- [ ] `PORT` will be auto-set by Railway
- [ ] `HOST` = `0.0.0.0`

## ✅ Verification After Deployment

1. **Check Deployment Status:**
   - [ ] Go to Railway dashboard
   - [ ] Click your web service
   - [ ] Check "Deployments" tab - should show "Success" (green)

2. **Test the Application:**
   - [ ] Visit `https://{your-app-name}.up.railway.app/`
   - [ ] Should see the signup page (from static/signup.html)

3. **Test Subscription Endpoint:**
   ```bash
   curl -X POST https://{your-app-name}.up.railway.app/subscribe \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```
   - [ ] Should return: `{"message": "Subscribed successfully"}`

4. **Check Database:**
   - [ ] In Railway, click PostgreSQL service
   - [ ] Click "Connect" button
   - [ ] Run: `SELECT * FROM subscribers;`
   - [ ] Should see your test email

5. **Check Logs:**
   - [ ] In Railway, click web service
   - [ ] Click "Logs" tab
   - [ ] Should see: "Database initialised"
   - [ ] Should see: "Scheduler started"

## ✅ Production Configuration

Before considering this production-ready:

- [ ] **Disable Test Scheduler** (optional, depends on your needs):
  - In `main.py`, line ~176, comment out:
    ```python
    # scheduler.add_job(run_newsletter_job, "interval", minutes=2)
    ```
  - This runs the full pipeline every 2 minutes - only for testing!

- [ ] **Verify Email Settings:**
  - [ ] Test sending an approval email
  - [ ] Check that unsubscribe links work: `{BASE_URL}/unsubscribe?token=...`

- [ ] **Set Up Backups** (optional):
  - [ ] Railway Pro: Enable auto-backups
  - [ ] Or: Set up scheduled exports of PostgreSQL data

## ✅ Troubleshooting

If deployment fails:

1. **Check Logs** (most important):
   - Go to web service → Logs
   - Look for error messages

2. **Common Issues:**
   - `ModuleNotFoundError`: Check requirements.txt is installed
   - `DATABASE_URL invalid`: Check PostgreSQL connection string
   - `Port already in use`: Railway handles this - shouldn't happen
   - Missing environment variables: Add them to web service "Variables" tab

3. **Database Issues:**
   - If `CREATE TABLE` fails: Check database name and permissions
   - PostgreSQL might need initialization: First deployment takes longer

4. **Get Help:**
   ```
   Check Railway logs for exact error
   → Paste error in Railway support
   → Or check railway.app/docs
   ```

## ✅ After Successful Deployment

- [ ] Test the scheduled newsletter job (set to Monday 8 AM UTC)
- [ ] Verify all endpoints work at production URL
- [ ] Set proper monitoring/alerts
- [ ] Document your Railway service setup
- [ ] Keep .env settings secure (never commit to git)

## ✅ Local Development

Continue using SQLite locally:

```bash
# No DATABASE_URL needed - will use SQLite
BASE_URL=http://localhost:8000
TAVILY_API_KEY=xxx
GROQ_API_KEY=xxx
RESEND_API_KEY=xxx
EMAIL_FROM=newsletter@yourdomain.com
APPROVAL_EMAIL=your-email@domain.com
```

Then run:
```bash
python main.py
# or
uvicorn main:app --reload
```

---

**Next Steps:**
1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Follow the Railway Setup Phase above
4. Come back and mark items as complete!
