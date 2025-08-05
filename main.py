import os
import json
import requests
from typefully_bot import post_to_typefully

def generate_post():
    print("Generating post with Cohere...")
    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command-light",  # or command-r-plus if you have access
        "prompt": "Write a fresh, concise, and insightful social media post about today's global news or trending topic.",
        "max_tokens": 300,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        result = response.json()
        print("Cohere response:", result)

        if "generations" in result and len(result["generations"]) > 0:
            return result["generations"][0]["text"]
        else:
            print("❌ Cohere failed to return valid response.")
            return None

    except Exception as e:
        print("❌ Error decoding JSON from Cohere:", str(e))
        print("Raw response:", response.text)
        return None

if __name__ == "__main__":
    tweet = generate_post()
    if tweet:
        post_to_typefully(tweet.strip())
    else:
        print("❌ No tweet was generated.")
