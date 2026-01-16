# 🚀 Quick Start Guide - AI Valentine's Poem Generator

## What You Have

A complete AI-powered Valentine's Day poem generator with:
- ✅ Web frontend (Flask app)
- ✅ AI poem generation (3d7tech API)
- ✅ Email delivery (Gmail)
- ✅ Twitter/X sharing with GitHub Pages links
- ✅ GitHub Pages for hosting

## Running the Application

### 1. Start the Flask Server

```bash
cd /workspaces/valentine_day_gift
source .venv/bin/activate
python app.py
```

The app will run at: **http://localhost:5000**

### 2. Access the Web Interface

Open your browser and visit:
- **Local**: http://localhost:5000
- **GitHub Pages**: https://richardawe.github.io/valentine_day_gift/

### 3. Create a Poem

1. Enter your email address
2. Describe your love story or poem idea
3. (Optional) Check the box to share on Twitter
4. Click "Generate & Send Poem"
5. Check your email for the PDF

## File Structure

```
valentine_day_gift/
├── app.py                    # Flask backend (main app)
├── ai_valentine.py           # CLI version (original script)
├── templates/
│   └── index.html           # Web interface
├── docs/
│   └── index.html           # GitHub Pages landing page
├── .env                     # Your credentials (create this)
├── requirements.txt         # Python dependencies
├── tweets_log.json          # Tracks tweets sent
├── product.pdf              # Generated poems
└── README.md                # Full documentation
```

## API Endpoints

### Create a Poem (POST)
```bash
curl -X POST http://localhost:5000/api/generate-poem \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "prompt": "Your love story or poem idea",
    "share_on_twitter": true
  }'
```

### Get All Tweets (GET)
```bash
curl http://localhost:5000/api/tweets
```

## Features

### 🎨 Web Interface
- Beautiful, responsive design
- Real-time poem generation
- Error handling and validation
- Success notifications

### 📧 Email Delivery
- Gmail SMTP integration
- PDF attachments with formatted poems
- Automatic cleanup of temp files

### 🐦 Twitter Integration
- Share poems on Twitter/X
- Each tweet includes GitHub Pages link
- Tweet tracking and logging

### 💾 Data Management
- tweets_log.json tracks all shared poems
- Each entry includes timestamp, preview, and URL

## Deployment Options

### Option 1: Local (Development)
```bash
python app.py
# Visit http://localhost:5000
```

### Option 2: GitHub Pages (Static Content)
The docs/index.html is hosted at:
https://richardawe.github.io/valentine_day_gift/

### Option 3: Production Deployment
For production, use:
- Gunicorn or uWSGI (WSGI server)
- Heroku, Railway, or DigitalOcean (hosting)
- Environment variables for credentials

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Troubleshooting

### Email Not Sending
- Verify Gmail app password in .env
- Check email address format
- Ensure 2FA is enabled on Gmail

### Twitter Not Posting
- Verify Twitter API credentials
- Check Twitter API rate limits
- Ensure app has write permissions

### Poem Not Generating
- Check 3d7tech API availability
- Verify internet connection
- Try a different poem prompt

## Next Steps

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: main, Folder: /docs
   - Click Save

2. **Share Your Link**:
   - Local: http://localhost:5000
   - GitHub Pages: https://richardawe.github.io/valentine_day_gift/

3. **Monitor Activity**:
   - Check tweets_log.json for posted poems
   - Monitor emails received

## Support

For questions or issues:
1. Check README.md for full documentation
2. Review app.py for code structure
3. Check error messages in console
4. Open an issue on GitHub

---

**Enjoy creating love poems with AI!** 💝
