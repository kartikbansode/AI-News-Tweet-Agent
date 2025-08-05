import os
import requests
import json
from datetime import datetime

# Load Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Use Gemini Pro model
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Prompt
PROMPT = "Write a short, tweet-sized post (under 280 characters) about the latest global ideas or innovations."

def generate_post():
    print("Generating post with Gemini...")

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [{"text": PROMPT}]
            }
        ]
    }

    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(data))
    res_json = response.json()

    print("Gemini response:", res_json)

    try:
        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except:
        print("❌ Gemini failed to return valid response.")
        return None

def save_to_typefully(text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"typefully_post_{now}.txt"

    with open(filename, "w") as f:
        f.write(text)

    print(f"✅ Saved tweet as: {filename}")

if __name__ == "__main__":
    tweet = generate_post()

    if tweet:
        print("Generated Tweet:")
        print(tweet)
        save_to_typefully(tweet)
    else:
        print("❌ No tweet was generated.")
