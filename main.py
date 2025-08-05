import os
import requests
import json
from datetime import datetime

# Use Gemini Pro model
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Prompt
PROMPT = "Write a short, tweet-sized post (under 280 characters) about the latest global ideas or innovations."


GEMINI_API_KEY = "AIzaSyAV-6bF4UOkyjlD0nSDwVMECFMfQ6DxmrE"  # Replace with your actual key

def generate_post():
    print("Generating post with Gemini...")

    endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Write a short, engaging Twitter post about a recent global innovation or idea."
                    }
                ]
            }
        ]
    }

    response = requests.post(endpoint, headers=headers, json=data)
    res_json = response.json()
    print("Gemini response:", res_json)

    if "candidates" in res_json:
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
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
