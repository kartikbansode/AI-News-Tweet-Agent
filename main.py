import os
import requests
import urllib.parse
import webbrowser

def generate_post():
    print("Generating post with Cohere...")

    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "message": "Write a fresh, concise, and insightful social media post about today's global news or trending topic.",
        "chat_history": [],
        "temperature": 0.7,
        "preamble": "",
        "model": "command-r-plus",
        "max_tokens": 300
    }

    response = requests.post("https://api.cohere.ai/v1/chat", headers=headers, json=data)

    try:
        response_json = response.json()
        print("Cohere response:", response_json)
        return response_json.get("text", "").strip()
    except Exception as e:
        print("❌ Error decoding response:", e)
        return None

def open_typefully(tweet_text):
    if not tweet_text:
        print("❌ No tweet to submit.")
        return

    encoded = urllib.parse.quote(tweet_text)
    url = f"https://typefully.com/new?text={encoded}"
    print("Submitting post to Typefully (open in browser)...")
    print(f"✅ Open this link to post: {url}")
    try:
        webbrowser.open(url)
    except:
        pass

if __name__ == "__main__":
    tweet = generate_post()
    open_typefully(tweet)
