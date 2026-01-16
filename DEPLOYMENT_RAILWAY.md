# 🚀 Deployment Guide - Railway

## Quick Deploy to Railway

Railway is a modern platform for deploying applications. Follow these steps:

### Step 1: Create Railway Account
1. Visit https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your GitHub account

### Step 2: Deploy the App
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Find and select `richardawe/valentine_day_gift`
5. Click "Deploy"

### Step 3: Set Environment Variables
Railway will automatically detect the Procfile and requirements.txt.

1. Go to your project settings
2. Click "Variables"
3. Add these environment variables:

```
OPENAI_API_KEY=not-needed
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
TEST_EMAIL=your_email@gmail.com
```

### Step 4: Deploy
1. Click the "Deploy" button
2. Watch the logs to confirm deployment
3. Once deployed, you'll get a URL like: `https://valentine-day-gift-production.up.railway.app`

### Step 5: Update GitHub Pages Link (Optional)
If you want tweets to link to your Railway deployment instead of GitHub Pages:
1. Edit `app.py`
2. Change `github_pages_url` to your Railway URL
3. Redeploy

## Environment Variables Needed

| Variable | Description |
|----------|-------------|
| OPENAI_API_KEY | Can be "not-needed" for 3d7tech API |
| TWITTER_API_KEY | Your Twitter API key |
| TWITTER_API_SECRET | Your Twitter API secret |
| TWITTER_ACCESS_TOKEN | Your Twitter access token |
| TWITTER_ACCESS_SECRET | Your Twitter token secret |
| GMAIL_USER | Gmail address for sending emails |
| GMAIL_APP_PASSWORD | Gmail app-specific password |
| TEST_EMAIL | Default recipient email |

## Files Created for Railway

- `Procfile` - Tells Railway how to run the app
- `runtime.txt` - Specifies Python 3.12.3
- `requirements.txt` - Updated with production dependencies
- `.railwayignore` - Files to ignore during deployment

## Troubleshooting

### Port Issues
Railway automatically assigns a PORT environment variable. The app uses `$PORT` in Procfile.

### Build Failures
1. Check the build logs in Railway dashboard
2. Verify all environment variables are set
3. Make sure requirements.txt is up to date

### Runtime Errors
1. Check the logs in Railway dashboard
2. Verify environment variables are correct
3. Test locally first with: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

## Testing Production Build Locally

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (like Railway does)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Visit http://localhost:5000
```

## Update Your README with Railway Link

Once deployed, update README.md to include:
- GitHub Pages (landing page): https://richardawe.github.io/valentine_day_gift/
- Railway App (live app): https://your-railway-url.up.railway.app

## Next Steps After Deployment

1. Test the live app thoroughly
2. Create sample poems
3. Verify emails are being sent
4. Check tweets are posting
5. Share the Railway link with users!

---

**Happy deploying! 🚀💝**
