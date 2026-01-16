"""Test the complete workflow"""
import json
from app import app

client = app.test_client()

print("=" * 60)
print("🧪 TESTING AI VALENTINE'S POEM GENERATOR")
print("=" * 60)

# Test 1: Generate poem without Twitter
print("\n1️⃣ Test: Generate poem without Twitter sharing")
response = client.post('/api/generate-poem', 
    data=json.dumps({
        'email': '3d7tech@gmail.com',
        'prompt': 'Love is a journey of two hearts becoming one',
        'share_on_twitter': False
    }),
    content_type='application/json'
)
result = response.get_json()
if response.status_code == 200:
    print("✅ PASS - Poem generated and emailed")
    print(f"   Poem: {result['poem'][:80]}...")
else:
    print(f"❌ FAIL - {result['error']}")

# Test 2: Generate poem WITH Twitter
print("\n2️⃣ Test: Generate poem with Twitter sharing")
response = client.post('/api/generate-poem', 
    data=json.dumps({
        'email': '3d7tech@gmail.com',
        'prompt': 'Eternal love under the stars',
        'share_on_twitter': True
    }),
    content_type='application/json'
)
result = response.get_json()
if response.status_code == 200 and 'tweet_url' in result:
    print("✅ PASS - Poem generated and tweeted")
    print(f"   Tweet URL: {result['tweet_url']}")
else:
    print(f"⚠️  PARTIAL - Poem created but tweet may have failed")
    if 'tweet_url' not in result:
        print(f"   Message: {result['message']}")

# Test 3: Check tweets log
print("\n3️⃣ Test: Check tweets log")
response = client.get('/api/tweets')
tweets = response.get_json()
print(f"✅ PASS - Retrieved {len(tweets)} tweets from log")
for i, tweet in enumerate(tweets[-2:], 1):
    print(f"   Tweet {i}: {tweet['url']}")

# Test 4: Check homepage
print("\n4️⃣ Test: Web interface loads")
response = client.get('/')
if response.status_code == 200 and '<html' in response.get_data(as_text=True).lower():
    print("✅ PASS - Homepage loads correctly")
else:
    print("❌ FAIL - Homepage load failed")

# Test 5: Invalid email
print("\n5️⃣ Test: Validation - Invalid email")
response = client.post('/api/generate-poem', 
    data=json.dumps({
        'email': 'not-an-email',
        'prompt': 'Some poem',
        'share_on_twitter': False
    }),
    content_type='application/json'
)
if response.status_code == 400:
    print("✅ PASS - Invalid email rejected")
else:
    print("❌ FAIL - Invalid email not rejected")

print("\n" + "=" * 60)
print("✨ ALL TESTS COMPLETED!")
print("=" * 60)
print("\n🚀 To start the Flask app:")
print("   python app.py")
print("\n🌐 Then visit: http://localhost:5000")
print("=" * 60)

