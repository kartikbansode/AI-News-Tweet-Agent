import os
import requests

def generate_post():
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        print("❌ COHERE_API_KEY not found.")
        return None

    prompt = "Write a fresh, concise, and insightful social media post about today's global news or trending topic."

    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command",
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.8
    }

    response = requests.post(url, json=data, headers=headers)

    try:
        result = response.json()
        print("Cohere response:", result)
        return result['generations'][0]['text']
    except Exception as e:
        print("❌ Cohere failed to return valid response.")
        return None
