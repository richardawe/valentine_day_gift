from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
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

github_pages_url = "https://richardawe.github.io/valentine_day_gift/"

# Unsplash API for backgrounds - REMOVED, using local images instead
# UNSPLASH_API_KEY = "c8_5R0M4ePKN5g-tH0hLMkLlZZTIhX_Y06m2ujfMr7w"
# UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Background themes with local image paths
BACKGROUND_THEMES = {
    "roses": {"image": "static/backgrounds/roses_2.jpg", "color": "#ff6b6b"},
    "sunset": {"image": "static/backgrounds/roses_1.jpg", "color": "#ff9f43"},
    "hearts": {"image": "static/backgrounds/heart_bokeh.jpg", "color": "#ff69b4"},
    "nature": {"image": "static/backgrounds/pink_flower.jpg", "color": "#2ecc71"},
    "wedding": {"image": "static/backgrounds/hearts_sparklers.jpg", "color": "#c39bd3"},
    "stars": {"image": "static/backgrounds/heart_bokeh.jpg", "color": "#3498db"},
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
    """Load background image from local files"""
    try:
        theme_data = BACKGROUND_THEMES.get(theme, BACKGROUND_THEMES["roses"])
        image_path = theme_data["image"]
        
        # Check if file exists
        if os.path.exists(image_path):
            return Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error loading background image: {e}")
    
    # Fallback to solid color if image loading fails
    theme_data = BACKGROUND_THEMES.get(theme, BACKGROUND_THEMES["roses"])
    img = Image.new('RGB', (1200, 1600), theme_data["color"])
    return img

def create_poem_image(poem, theme="roses"):
    try:
        bg_img = get_background_image(theme)
        bg_img = bg_img.resize((1200, 1600), Image.Resampling.LANCZOS)
        
        overlay = Image.new('RGBA', bg_img.size, (255, 255, 255, 200))
        if bg_img.mode != 'RGBA':
            bg_img = bg_img.convert('RGBA')
        bg_img = Image.alpha_composite(bg_img, overlay)
        bg_img = bg_img.convert('RGB')
    except:
        bg_img = Image.new('RGB', (1200, 1600), (102, 126, 234))
    
    draw = ImageDraw.Draw(bg_img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        poem_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        poem_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    title = "Your AI-Generated Valentine's Gift"
    draw.text((100, 80), title, font=title_font, fill=(200, 20, 147))
    draw.text((100, 160), "✨ 💕 ✨", font=poem_font, fill=(200, 20, 147))
    
    y_pos = 280
    line_height = 70
    
    for line in poem.split('\n'):
        if line.strip():
            for wrapped_line in textwrap.wrap(line, width=35):
                draw.text((100, y_pos), wrapped_line, font=poem_font, fill=(20, 20, 20))
                y_pos += line_height
        else:
            y_pos += line_height // 2
    
    footer_y = 1520
    draw.text((100, footer_y), FOOTER_TEXT, font=footer_font, fill=(80, 80, 80))
    
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

def generate_poem(prompt, twitter_handle=None):
    if openai_client is None:
        # Fallback poem if API client not configured
        poem = f"A Valentine's Ode\n\nYour beauty shines like morning light,\nYour presence makes my heart take flight.\n{prompt},\nIn your embrace, I find my home.\nTogether, never more alone.\nWith love so true and ever bright,\nYou are my heart's eternal light.\n\nForever yours, with love so true."
    else:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a romantic poet. Generate ONLY a short, beautiful Valentine's poem (8-12 lines). No explanations, no commentary, just the poem itself."},
                    {"role": "user", "content": f"Write a romantic Valentine's poem based on: {prompt}"}
                ]
            )
            poem = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating poem: {e}")
            # Return fallback poem
            poem = f"A Valentine's Ode\n\nYour beauty shines like morning light,\nYour presence makes my heart take flight.\n{prompt},\nIn your embrace, I find my home.\nTogether, never more alone.\nWith love so true and ever bright,\nYou are my heart's eternal light.\n\nForever yours, with love so true."
    
    # Add Twitter handle tag at the end if provided
    if twitter_handle:
        # Clean up the handle
        handle = twitter_handle.strip()
        if not handle.startswith('@'):
            handle = '@' + handle
        poem = poem + f"\n\n- {handle}"
    
    return poem

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
        'twitter_configured': bool(twitter_client is not None),
        'openai_configured': bool(openai_client is not None)
    }), 200

@app.route('/api/generate-poem', methods=['POST'])
def api_generate_poem():
    try:
        data = request.json
        twitter_handle = data.get('twitter_handle', '').strip()
        poem_prompt = data.get('prompt', '').strip()
        theme = data.get('theme', 'roses')
        share_on_twitter = data.get('share_on_twitter', False)
        
        if not twitter_handle or not poem_prompt:
            return jsonify({'error': 'Twitter handle and prompt are required'}), 400
        
        # Validate Twitter handle format (should start with @ or be alphanumeric)
        if not twitter_handle.replace('@', '').replace('_', '').isalnum():
            return jsonify({'error': 'Invalid Twitter handle format'}), 400
        
        # Generate poem with Twitter handle tag
        poem = generate_poem(poem_prompt, twitter_handle)
        
        if not poem:
            return jsonify({'error': 'Failed to generate poem'}), 500
        
        response_data = {
            'success': True,
            'message': f'Poem generated and tagged with {twitter_handle}!',
            'poem': poem,
            'theme': theme
        }
        
        # Try to post to Twitter (optional)
        if share_on_twitter and twitter_client:
            try:
                tweet_url = post_to_twitter(poem_prompt)
                if tweet_url:
                    response_data['tweet_url'] = tweet_url
                    response_data['message'] += f"\n\nAlso posted to Twitter: {tweet_url}"
            except Exception as tweet_error:
                print(f"Tweet posting error (non-blocking): {tweet_error}")
        
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
