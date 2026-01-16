import os
import sys
from dotenv import load_dotenv
import pytrends.request as pt
from openai import OpenAI
import tweepy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Load environment variables
load_dotenv()

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
test_email = os.getenv('TEST_EMAIL')

def get_trends():
    """Fetch current trends using Google Trends API (public/free)."""
    try:
        trends = pt.TrendReq(hl='en-US', tz=360)
        trends.build_payload(kw_list=['Valentine\'s Day'], timeframe='now 7-d')
        data = trends.interest_over_time()
        top_trends = data['Valentine\'s Day'].to_dict()  # Simplified; expand for more keywords
        return f"Current Valentine's trends: High interest in personalized gifts. Data: {top_trends}"
    except Exception as e:
        # Fallback if API limit reached
        return f"Valentine's Day trends: High interest in personalized gifts, romantic experiences, and digital gifts. (Note: {str(e)[:50]}...)"

def ideate_product(prompt, trends):
    """Use 3d7tech API to ideate a digital product."""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI entrepreneur. Ideate a simple digital product (e.g., custom poem or image) based on the prompt and trends. Output: Product name, description, how to generate it."},
            {"role": "user", "content": f"Prompt: {prompt}\nTrends: {trends}"}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_demand(product_desc):
    """Post a teaser on X to generate buzz (public API, requires dev account)."""
    tweet_text = "✨ Introducing AI-Generated Valentine's Gifts! 💕 Personalized love poems created just for you. Express your feelings with AI-powered romance. Sign up now! #ValentinesAI #AILove"
    try:
        response = twitter_client.create_tweet(text=tweet_text)
        return f"Posted teaser: https://x.com/status/{response.data['id']}"
    except Exception as e:
        return f"Error posting: {str(e)} (Check API setup)"

def create_product(product_idea):
    """Generate the digital product using 3d7tech API (e.g., poem as PDF)."""
    # Generate a poem - ask for a clean poem without extra commentary
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a romantic poet. Generate ONLY a short, beautiful Valentine's poem (8-12 lines). No explanations, no commentary, just the poem itself."},
            {"role": "user", "content": f"Write a romantic Valentine's poem based on: {product_idea}"}
        ]
    )
    poem = response.choices[0].message.content.strip()
    
    # Create PDF with proper text wrapping
    pdf_path = "product.pdf"
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
    max_width = 500
    
    # Split poem into lines and draw each one
    lines = poem.split('\n')
    for line in lines:
        if line.strip():  # Only draw non-empty lines
            # Simple word wrapping
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) < 80:  # Rough character limit per line
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
            y_position -= line_height // 2  # Extra space for blank lines
    
    # Add footer
    y_position -= 20
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, y_position, "With love, from AI 💝")
    
    c.save()
    return pdf_path, poem

def send_product(email, pdf_path):
    """Send the product via email using Gmail SMTP."""
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = email
        msg['Subject'] = "Your Free AI-Generated Valentine's Product"
        
        # Email body
        body = 'Enjoy your free test product! Attached is your custom AI-generated gift.'
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='valentines_gift.pdf')
        msg.attach(part)
        
        # Send via Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        return f"Sent to {email}. Status: Success"
    except Exception as e:
        return f"Error sending: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_entrepreneur_mvp.py 'Your prompt here'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    print(f"Starting with prompt: {prompt}")
    
    # Step 1: Get trends
    trends = get_trends()
    print(f"Trends: {trends}")
    
    # Step 2: Ideate
    product_idea = ideate_product(prompt, trends)
    print(f"Product Idea: {product_idea}")
    
    # Step 3: Generate demand
    demand_result = generate_demand(product_idea)
    print(demand_result)
    
    # Step 4: Create product
    pdf_path, poem = create_product(product_idea)
    print(f"Product created: {poem}")
    
    # Step 5: Send
    send_result = send_product(test_email, pdf_path)
    print(send_result)
    
    # Clean up
    # os.remove(pdf_path)  # Commented out for testing - PDF saved as product.pdf
    print("MVP run complete. Check X for engagement and your email for the product.")
    print(f"PDF saved at: {pdf_path}")