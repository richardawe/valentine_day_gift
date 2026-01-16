from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openai import OpenAI
import tweepy
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Clients
openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY', 'not-needed'),
    base_url='https://api.3d7tech.com/v1'
)

twitter_client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

gmail_user = os.getenv('GMAIL_USER')
gmail_password = os.getenv('GMAIL_APP_PASSWORD')
github_pages_url = "https://richardawe.github.io/valentine_day_gift/"

# Track tweets in a log file
TWEETS_LOG = "tweets_log.json"

def load_tweets_log():
    """Load the tweets log file."""
    if os.path.exists(TWEETS_LOG):
        with open(TWEETS_LOG, 'r') as f:
            return json.load(f)
    return []

def save_tweets_log(tweets):
    """Save tweets to log file."""
    with open(TWEETS_LOG, 'w') as f:
        json.dump(tweets, f, indent=2)

def generate_poem(prompt):
    """Generate a poem using 3d7tech API."""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a romantic poet. Generate ONLY a short, beautiful Valentine's poem (8-12 lines). No explanations, no commentary, just the poem itself."},
            {"role": "user", "content": f"Write a romantic Valentine's poem based on: {prompt}"}
        ]
    )
    return response.choices[0].message.content.strip()

def create_pdf_with_poem(poem):
    """Create a PDF with the poem."""
    pdf_path = "temp_poem.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "Your AI-Generated Valentine's Gift")
    
    # Add decorative line
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "✨ 💕 ✨")
    
    # Add poem with text wrapping
    c.setFont("Helvetica", 11)
    y_position = 700
    line_height = 20
    
    # Split poem into lines and draw each one
    lines = poem.split('\n')
    for line in lines:
        if line.strip():
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) < 80:
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(100, y_position, current_line)
                        y_position -= line_height
                    current_line = word
            if current_line:
                c.drawString(100, y_position, current_line)
                y_position -= line_height
        else:
            y_position -= line_height // 2
    
    # Add footer
    y_position -= 20
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, y_position, "With love, from AI 💝")
    
    # Add GitHub Pages link
    y_position -= 30
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(100, y_position, f"Created at: {github_pages_url}")
    
    c.save()
    return pdf_path

def send_email_with_poem(recipient_email, poem):
    """Send email with poem PDF."""
    try:
        pdf_path = create_pdf_with_poem(poem)
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = "Your AI-Generated Valentine's Poem 💝"
        
        # Email body
        body = f"""Hello,

Your personalized AI-generated Valentine's poem has been created with love!

Check out our Valentine's AI at: {github_pages_url}

With love,
The AI Valentine's Team 💕
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='valentine_poem.pdf')
        msg.attach(part)
        
        # Send via Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        
        # Clean up temp file
        os.remove(pdf_path)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def post_to_twitter(poem_preview):
    """Post a tweet about the generated poem."""
    try:
        tweet_text = f"✨ New AI Valentine's Poem Generated! 💕\n\n{poem_preview[:100]}...\n\nCreate your own: {github_pages_url}\n\n#ValentinesAI #Love"
        response = twitter_client.create_tweet(text=tweet_text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://x.com/i/web/status/{tweet_id}"
        
        # Save to log
        tweets = load_tweets_log()
        tweets.append({
            "timestamp": datetime.now().isoformat(),
            "poem_preview": poem_preview[:50],
            "tweet_id": tweet_id,
            "url": tweet_url
        })
        save_tweets_log(tweets)
        
        return tweet_url
    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        return None

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html', github_url=github_pages_url)

@app.route('/api/generate-poem', methods=['POST'])
def api_generate_poem():
    """API endpoint to generate a poem and send it via email."""
    try:
        data = request.json
        user_email = data.get('email', '').strip()
        poem_prompt = data.get('prompt', '').strip()
        share_on_twitter = data.get('share_on_twitter', False)
        
        # Validate inputs
        if not user_email or not poem_prompt:
            return jsonify({'error': 'Email and prompt are required'}), 400
        
        if '@' not in user_email:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Generate poem
        poem = generate_poem(poem_prompt)
        
        # Send email
        email_sent = send_email_with_poem(user_email, poem)
        
        if not email_sent:
            return jsonify({'error': 'Failed to send email'}), 500
        
        response_data = {
            'success': True,
            'message': f'Poem generated and sent to {user_email}!',
            'poem': poem
        }
        
        # Post to Twitter if requested
        if share_on_twitter:
            tweet_url = post_to_twitter(poem_prompt)
            if tweet_url:
                response_data['tweet_url'] = tweet_url
                response_data['message'] += f"\n\nAlso posted to Twitter: {tweet_url}"
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tweets')
def api_get_tweets():
    """Get all tweets sent."""
    tweets = load_tweets_log()
    return jsonify(tweets), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
