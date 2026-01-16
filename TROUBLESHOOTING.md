# Troubleshooting Guide - Valentine's Day Gift App

## 502 Bad Gateway Error

### What it means
The Flask backend is crashing or not responding properly.

### Quick Fix - Check Environment Variables

1. **Open Railway Dashboard**
   - Go to: https://railway.app/dashboard
   - Click on your project
   - Click "Variables" tab

2. **Verify these variables are set:**
   ```
   GMAIL_USER = your-gmail@gmail.com
   GMAIL_APP_PASSWORD = your-app-password
   ```

3. **Optional but recommended:**
   ```
   TWITTER_API_KEY = your_key
   TWITTER_API_SECRET = your_secret
   TWITTER_ACCESS_TOKEN = your_token
   TWITTER_ACCESS_SECRET = your_token_secret
   ```

### Testing the Deployment

1. **Check Health Status**
   - Visit: `https://your-railway-app.up.railway.app/health`
   - You should see:
   ```json
   {
     "status": "ok",
     "gmail_configured": true,
     "twitter_configured": true,
     "openai_configured": true
   }
   ```

2. **Diagnose Issues**
   - If `gmail_configured` is `false`: Add GMAIL_USER and GMAIL_APP_PASSWORD
   - If `twitter_configured` is `false`: Twitter is optional, but tweets won't work
   - If `openai_configured` is `false`: The app will use a fallback poem generator

### Fixing Gmail Configuration

1. **Get Gmail App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google generates a 16-character password
   - Copy this password

2. **Add to Railway**
   - In Railway Variables:
     - `GMAIL_USER`: your-gmail@gmail.com
     - `GMAIL_APP_PASSWORD`: paste-the-16-char-password-here

3. **Redeploy**
   - Click "Redeploy" button in Railway dashboard
   - Wait for deployment to complete (2-3 minutes)

### Common Issues

**Issue:** Still getting 502 after setting variables
- **Solution:** 
  1. Check Railway build logs for errors
  2. Click "Redeploy" again
  3. Wait 5 minutes for it to fully restart

**Issue:** Health check says Gmail is not configured
- **Solution:**
  1. Double-check variable names (must be exact case)
  2. Make sure passwords don't have trailing spaces
  3. Redeploy after fixing

**Issue:** App loads but poem generation fails
- **Solution:**
  - The app has fallback poems enabled
  - Check if you want email delivery - needs Gmail configured
  - If no email needed, the fallback poem will display

### Local Testing Before Deployment

To test locally before pushing to Railway:

```bash
# Set environment variables
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"

# Run the app
python app.py

# Visit http://localhost:5000
```

### Monitoring Railway Logs

1. Go to your Railway project
2. Click "Logs" tab
3. Look for error messages
4. Common errors:
   - `ImportError`: Missing Python package
   - `KeyError`: Missing environment variable
   - `ConnectionError`: API connection issue

### Need More Help?

Check these endpoints to diagnose:

- `/` - Main page
- `/health` - Server status check
- `/api/themes` - List available themes
- `/api/tweets` - Recent tweets (if configured)

### Environment Variables Reference

| Variable | Required | Example | Where to Get |
|----------|----------|---------|--------------|
| GMAIL_USER | Yes | your@gmail.com | Your Gmail address |
| GMAIL_APP_PASSWORD | Yes | xxxx xxxx xxxx xxxx | [Google Account](https://myaccount.google.com/apppasswords) |
| TWITTER_API_KEY | No | abc123... | [Twitter Developer](https://developer.twitter.com) |
| TWITTER_API_SECRET | No | xyz789... | [Twitter Developer](https://developer.twitter.com) |
| TWITTER_ACCESS_TOKEN | No | 123-abc... | [Twitter Developer](https://developer.twitter.com) |
| TWITTER_ACCESS_SECRET | No | 456-def... | [Twitter Developer](https://developer.twitter.com) |

---

**Last Updated:** January 16, 2026
