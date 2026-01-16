from flask import Flask, render_template, request, jsonify, send_file
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
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Clients
try:
    openai_client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY', 'not-needed'),
        base_url='https://api.3d7tech.com/v1'
    )
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    openai_client = None

try:
    twitter_client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
except Exception as e:
    print(f"Warning: Twitter client initialization failed: {e}")
    twitter_client = None

gmail_user = os.getenv('GMAIL_USER')
gmail_password = os.getenv('GMAIL_APP_PASSWORD')
github_pages_url = "https://richardawe.github.io/valentine_day_gift/"

# Unsplash API for backgrounds
UNSPLASH_API_KEY = "c8_5R0M4ePKN5g-tH0hLMkLlZZTIhX_Y06m2ujfMr7w"
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Background themes
BACKGROUND_THEMES = {
    "roses": {"query": "red roses love", "color": "#ff6b6b"},
    "sunset": {"query": "romantic sunset love", "color": "#ff9f43"},
    "hearts": {"query": "heart bokeh romantic", "color": "#ff69b4"},
    "nature": {"query": "nature love romantic", "color": "#2ecc71"},
    "wedding": {"query": "wedding couple romance", "color": "#c39bd3"},
    "stars": {"query": "night stars romantic", "color": "#3498db"},
}

TWEETS_LOG = "tweets_log.json"
FOOTER_TEXT = "With love from 3d7 technologies ❤️"

def load_tweets_log():
    if os.path.exists(TWEETS_LOG):
        with open(TWEETS_LOG, 'r') as f:
            return json.load(f)
    return []

def save_tweets_log(tweets):
    with open(TWEETS_LOG, 'w') as f:
        json.dump(tweets, f, indent=2)

def get_background_image(theme="roses"):
    try:
        theme_data = BACKGROUND_THEMES.get(theme, BACKGROUND_THEMES["roses"])
        params = {
            "query": theme_data["query"],
            "per_page": 1,
            "client_id": UNSPLASH_API_KEY
        }
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                image_url = data["results"][0]["urls"]["regular"]
                img_response = requests.get(image_url, timeout=5)
                return Image.open(BytesIO(img_response.content))
    except Exception as e:
        print(f"Error fetching background: {e}")
    
    theme_data = BACKGROUND_THEMES.get(theme, BACKGROUND_THEMES["roses"])
    img = Image.new('RGB', (1200, 1600), theme_data["color"])
    return img

def create_poem_image(poem, theme="roses"):
    try:
        bg_img = get_background_image(theme)
        bg_img = bg_img.resize((1200, 1600), Image.Resampling.LANCZOS)
        
        overlay = Image.new('RGBA', bg_img.size, (255, 255, 255, 180))
        if bg_img.mode != 'RGBA':
            bg_img = bg_img.convert('RGBA')
        bg_img = Image.alpha_composite(bg_img, overlay)
        bg_img = bg_img.convert('RGB')
    except:
        bg_img = Image.new('RGB', (1200, 1600), (102, 126, 234))
    
    draw = ImageDraw.Draw(bg_img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        poem_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        poem_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    title = "Your AI-Generated Valentine's Gift"
    draw.text((100, 100), title, font=title_font, fill=(255, 20, 147))
    draw.text((100, 180), "✨ 💕 ✨", font=poem_font, fill=(255, 20, 147))
    
    y_pos = 280
    line_height = 60
    
    for line in poem.split('\n'):
        if line.strip():
            for wrapped_line in textwrap.wrap(line, width=40):
                draw.text((100, y_pos), wrapped_line, font=poem_font, fill=(40, 40, 40))
                y_pos += line_height
        else:
            y_pos += line_height // 2
    
    footer_y = 1500
    draw.text((100, footer_y), FOOTER_TEXT, font=footer_font, fill=(100, 100, 100))
    
    return bg_img

def create_poem_pdf(poem, theme="roses"):
    pdf_path = "temp_poem.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "Your AI-Generated Valentine's Gift")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "✨ 💕 ✨")
    
    c.setFont("Helvetica", 11)
    y_position = 700
    line_height = 20
    
    for line in poem.split('\n'):
        if line.strip():
            for wrapped_line in textwrap.wrap(line, width=80):
                c.drawString(100, y_position, wrapped_line)
                y_position -= line_height
        else:
            y_position -= line_height // 2
    
    y_position -= 30
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(100, y_position, FOOTER_TEXT)
    
    c.save()
    return pdf_path

def generate_poem(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a romantic poet. Generate ONLY a short, beautiful Valentine's poem (8-12 lines). No explanations, no commentary, just the poem itself."},
            {"role": "user", "content": f"Write a romantic Valentine's poem based on: {prompt}"}
        ]
    )
    return response.choices[0].message.content.strip()

def send_email_with_poem(recipient_email, poem, theme="roses"):
    try:
        pdf_path = create_poem_pdf(poem, theme)
        poem_image = create_poem_image(poem, theme)
        
        img_bytes = BytesIO()
        poem_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient_email
        msg['Subject'] = "Your AI-Generated Valentine's Poem 💝"
        
        body = f"""Hello,

Your personalized AI-generated Valentine's poem has been created with love!

Check out our Valentine's AI at: {github_pages_url}

With love,
The AI Valentine's Team 💕
"""
        msg.attach(MIMEText(body, 'plain'))
        
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='valentine_poem.pdf')
        msg.attach(part)
        
        img_part = MIMEBase('image', 'png')
        img_part.set_payload(img_bytes.getvalue())
        encoders.encode_base64(img_part)
        img_part.add_header('Content-Disposition', 'attachment', filename='valentine_poem.png')
        msg.attach(img_part)
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        
        os.remove(pdf_path)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def post_to_twitter(poem_preview):
    try:
        tweet_text = f"✨ New AI Valentine's Poem Generated! 💕\n\n{poem_preview[:100]}...\n\nCreate your own: {github_pages_url}\n\n#ValentinesAI #Love"
        response = twitter_client.create_tweet(text=tweet_text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://x.com/i/web/status/{tweet_id}"
        
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
    return render_template('index.html', github_url=github_pages_url)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'gmail_configured': bool(gmail_user and gmail_password),
        'twitter_configured': bool(twitter_client is not None),
        'openai_configured': bool(openai_client is not None)
    }), 200

@app.route('/api/generate-poem', methods=['POST'])
def api_generate_poem():
    try:
        data = request.json
        user_email = data.get('email', '').strip()
        poem_prompt = data.get('prompt', '').strip()
        theme = data.get('theme', 'roses')
        share_on_twitter = data.get('share_on_twitter', False)
        
        if not user_email or not poem_prompt:
            return jsonify({'error': 'Email and prompt are required'}), 400
        
        if '@' not in user_email:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Check if required environment variables are set
        if not gmail_user or not gmail_password:
            return jsonify({'error': 'Email service not configured on server'}), 503
        
        poem = generate_poem(poem_prompt)
        
        if not poem:
            return jsonify({'error': 'Failed to generate poem'}), 500
        
        email_sent = send_email_with_poem(user_email, poem, theme)
        
        if not email_sent:
            return jsonify({'error': 'Failed to send email. Check server logs.'}), 500
        
        response_data = {
            'success': True,
            'message': f'Poem generated and sent to {user_email}!',
            'poem': poem,
            'theme': theme
        }
        
        if share_on_twitter and twitter_client:
            try:
                tweet_url = post_to_twitter(poem_prompt)
                if tweet_url:
                    response_data['tweet_url'] = tweet_url
                    response_data['message'] += f"\n\nAlso posted to Twitter: {tweet_url}"
            except Exception as tweet_error:
                print(f"Tweet posting error: {tweet_error}")
                # Don't fail the whole request if tweeting fails
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/download-poem/<format>/<theme>', methods=['POST'])
def api_download_poem(format, theme):
    try:
        data = request.json
        poem = data.get('poem', '')
        
        if format == 'png':
            poem_image = create_poem_image(poem, theme)
            img_bytes = BytesIO()
            poem_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return send_file(img_bytes, mimetype='image/png', as_attachment=True, download_name='valentine_poem.png')
        
        elif format == 'pdf':
            pdf_path = create_poem_pdf(poem, theme)
            return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name='valentine_poem.pdf')
        
        return jsonify({'error': 'Invalid format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/themes', methods=['GET'])
def api_get_themes():
    return jsonify(list(BACKGROUND_THEMES.keys())), 200

@app.route('/api/tweets')
def api_get_tweets():
    tweets = load_tweets_log()
    return jsonify(tweets), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
