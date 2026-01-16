# 💝 AI Valentine's Day Gift Generator

An AI-powered application that generates personalized love poems and sends them to your email. Built with Flask, OpenAI API (via 3d7tech), Gmail, and Twitter integration.

## Features

✨ **AI-Generated Poems** - Create unique, romantic love poems using advanced AI
📧 **Email Delivery** - Receive your poems as beautifully formatted PDFs via Gmail
🐦 **Social Sharing** - Share your poems on Twitter/X with one click
🎨 **Beautiful Design** - Modern, responsive web interface
📱 **Mobile Friendly** - Works on all devices
🔒 **Privacy First** - Your data is secure

## Live Demo

🌐 **GitHub Pages**: https://richardawe.github.io/valentine_day_gift/

## Setup Instructions

### Prerequisites

- Python 3.8+
- Gmail account with app-specific password
- Twitter/X API credentials
- 3d7tech API access (free tier available)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/richardawe/valentine_day_gift.git
cd valentine_day_gift
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```
OPENAI_API_KEY=not-needed
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
TEST_EMAIL=your_email@gmail.com
API_BASE_URL=https://api.3d7tech.com/v1
```

5. Run the Flask app:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

### Gmail Setup

1. Enable 2-factor authentication on your Google Account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in your `.env` file

### Twitter/X API Setup

1. Create a Developer Account at [Twitter Developer Portal](https://developer.twitter.com)
2. Create a new app and get your API credentials
3. Add credentials to `.env` file

### 3d7tech API

The app uses the free 3d7tech API for AI poem generation. It's OpenAI-compatible and runs Ollama models.

Website: https://api.3d7tech.com/

## Usage

### Via Web Interface

1. Visit http://localhost:5000
2. Enter your email address
3. Describe your love story or poem idea
4. Optionally enable Twitter sharing
5. Click "Generate & Send Poem"
6. Check your email for the PDF poem

### Command Line (Original Script)

```bash
python ai_valentine.py "Your poem prompt here"
```

This will:
- Fetch Valentine's Day trends
- Ideate a product concept
- Post to Twitter
- Generate a love poem
- Create a PDF
- Send via Gmail

## Project Structure

```
valentine_day_gift/
├── app.py                 # Flask backend application
├── ai_valentine.py        # Original CLI script
├── templates/
│   └── index.html        # Web frontend
├── docs/
│   └── index.html        # GitHub Pages landing page
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## APIs Used

- **3d7tech API** - AI poem generation (OpenAI-compatible)
- **Gmail SMTP** - Email delivery
- **Twitter API v2** - Social sharing
- **Google Trends API** - Trend analysis (original script)

## Files

- `app.py` - Flask web application with API endpoints
- `ai_valentine.py` - Original CLI version with full workflow
- `templates/index.html` - Web interface
- `docs/index.html` - GitHub Pages landing page

## API Endpoints

### POST `/api/generate-poem`

Generate a poem and send via email.

**Request:**
```json
{
  "email": "recipient@example.com",
  "prompt": "Your love story or poem idea",
  "share_on_twitter": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Poem generated and sent!",
  "poem": "The generated poem text...",
  "tweet_url": "https://x.com/status/..."
}
```

### GET `/api/tweets`

Retrieve all tweets sent.

**Response:**
```json
[
  {
    "timestamp": "2026-01-16T...",
    "poem_preview": "Your love story...",
    "tweet_id": "...",
    "url": "https://x.com/status/..."
  }
]
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub or contact the maintainers.

---

Made with ❤️ by the AI Valentine's Team