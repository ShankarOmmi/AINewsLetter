# Railway Deployment Guide

## Prerequisites
1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Push your code to GitHub, GitLab, or another Git provider
3. **Environment Variables**: Have all API keys ready

## Step 1: Prepare Your Code

✅ **All code changes have been completed:**
- `config.py` - Updated with environment variables
- `database.py` - Now supports both PostgreSQL and SQLite
- `models.py` - Compatible with both SQL dialects
- `router.py` - Uses proper placeholders for both databases
- `main.py` - Uses environment variables for URLs
- `emailer/send.py` - Configurable email sender
- `Procfile` - Added for Railway deployment
- `requirements.txt` - Updated with production dependencies

## Step 2: Setup PostgreSQL on Railway

1. **Create a Railway Project**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Create a new service"

2. **Add PostgreSQL Database**:
   - Click "Create" → Search for "PostgreSQL"
   - Wait for PostgreSQL to initialize
   - Copy the connection string from the PostgreSQL service

## Step 3: Create Your Web Service

1. **Connect Your Git Repository**:
   - In Railway, create a new service
   - Select "GitHub" (or your Git provider)
   - Connect your repository
   - Select your branch (typically `main` or `master`)

2. **Configure Environment Variables**:
   Click on your web service → "Variables" tab and add:

   ```
   TAVILY_API_KEY=your_tavily_api_key
   GROQ_API_KEY=your_groq_api_key
   RESEND_API_KEY=your_resend_api_key
   
   EMAIL_FROM=newsletter@yourdomain.com
   APPROVAL_EMAIL=your-approval-email@domain.com
   ```

3. **PostgreSQL Connection**:
   - In Railway, go to PostgreSQL service
   - Copy the connection string (it should appear in Variables)
   - Add to your web service:
   ```
   DATABASE_URL=postgresql://...
   ```

4. **Set BASE_URL**:
   ```
   BASE_URL=https://your-app-name.up.railway.app
   ```
   Replace `your-app-name` with the actual service name Railway assigns

## Step 4: Configure Port and Host

Railway automatically sets the `PORT` environment variable. Your app is already configured to use it:

```python
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
```

The `Procfile` tells Railway how to run your app:
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT main:app
```

## Step 5: Deploy

1. **Push Code to Git**:
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

2. **Railway Auto-Deploy**:
   - Railway will automatically detect changes and redeploy
   - Monitor the deployment in the "Deployments" tab

3. **Check Logs**:
   - Click on your web service → "Logs" tab
   - Watch for any errors during startup

## Step 6: Verify Deployment

1. **Access Your App**:
   - Railway will assign a URL like `https://your-app-name.up.railway.app`
   - Visit the URL and test the `/` endpoint

2. **Test Subscription**:
   ```bash
   curl -X POST https://your-app-name.up.railway.app/subscribe \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

3. **Check Database**:
   - In Railway, click PostgreSQL service
   - Use the "Connect" button to open database client
   - Run: `SELECT * FROM subscribers;`

## Important Notes

### Database Migration
- Your existing SQLite database (`newsletter.db`) won't transfer to Railway
- Data will be fresh (clean slate) on PostgreSQL
- Scheduled jobs will start fresh

### Email Configuration
- Update `EMAIL_FROM` to match your Resend domain
- Update `APPROVAL_EMAIL` to your email address for approvals
- Test email sending after deployment

### Scheduled Jobs
- Jobs are configured in `main.py`:
  - Weekly: Monday 8 AM UTC
  - Test: Every 2 minutes (disable in production!)
- Comment out the test schedule in production:
  ```python
  # scheduler.add_job(run_newsletter_job, "interval", minutes=2)
  ```

### Environment-Specific Configuration

**For LOCAL Development** (keep using SQLite):
```bash
# .env file
TAVILY_API_KEY=xxx
GROQ_API_KEY=xxx
RESEND_API_KEY=xxx
EMAIL_FROM=newsletter@shankarommi.in
APPROVAL_EMAIL=n200179@rguktn.ac.in
# DATABASE_URL is not set, so SQLite will be used
BASE_URL=http://localhost:8000
```

**For RAILWAY** (uses PostgreSQL):
```
Set via Railway dashboard:
DATABASE_URL=postgresql://...
BASE_URL=https://your-app-name.up.railway.app
```

## Troubleshooting

### App Won't Start
- Check logs: Railway Deployments → Logs
- Common issues:
  - Missing environment variables
  - Invalid DATABASE_URL
  - Port binding issues

### Database Connection Failed
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running (green status)
- Ensure database name exists

### Emails Not Sending
- Verify `RESEND_API_KEY` is correct
- Check `EMAIL_FROM` domain is verified in Resend
- Check logs for error details

### Scheduled Jobs Not Running
- Check `/logs/app.log` in your app
- Ensure the scheduler is not commented out
- Verify timezone settings (use UTC in cron)

## Next Steps

1. **Monitor Performance**:
   - Use Railway's built-in monitoring
   - Check logs regularly for errors

2. **Enable Auto-Deploy**:
   - Railway does this by default
   - Push to main branch = automatic deploy

3. **Set Up Health Checks** (Optional):
   - Add a simple health endpoint
   - Configure in Railway settings

4. **Backup Strategy**:
   - Export PostgreSQL data regularly
   - Use Railway's built-in backup features (Pro plan)

## Useful Railway Commands

```bash
# Deploy using Railway CLI
railway up

# View logs
railway logs

# Set environment variable
railway variables set KEY=value
```

Install Railway CLI: https://docs.railway.app/guides/cli

---

**Need Help?**
- 📚 [Railway Docs](https://docs.railway.app)
- 📚 [FastAPI + Railway Guide](https://docs.railway.app/guides/fastapi)
- 🐛 Check Railway Support Dashboard
