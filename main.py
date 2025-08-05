import os
import json
import requests
from typefully_bot import post_to_typefully

def generate_post():
    print("Generating post with Cohere...")
    api_key = os.getenv("COHERE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "command-r+",
        "prompt": "Write a fresh, concise, and insightful social media post about today's global news or trending topic.",
        "max_tokens": 300,
        "temperature": 0.9,
    }

    response = requests.post("https://api.cohere.ai/v1/generate", headers=headers, json=data)
    result = response.json()
    print("Cohere response:", result)

    try:
        return result["generations"][0]["text"]
    except Exception as e:
        print("❌ Cohere failed to return valid response.")
        return None

if __name__ == "__main__":
    tweet = generate_post()
    if tweet:
        post_to_typefully(tweet.strip())
    else:
        print("❌ No tweet was generated.")
