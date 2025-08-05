import os
import requests
import json

def generate_post():
    print("Generating post with Cohere...")
    api_key = os.getenv("COHERE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "command-r",
        "chat_history": [],
        "message": "Write a fresh, concise, and insightful social media post about today's global news or trending topic."
    }

    response = requests.post(
        "https://api.cohere.ai/v1/chat",
        headers=headers,
        data=json.dumps(data)
    )

    try:
        response_data = response.json()
        print("Cohere response:", response_data)
        return response_data['text'].strip()
    except Exception as e:
        print("❌ Cohere failed to return valid response.")
        return None

def submit_to_typefully(text):
    print("Submitting post to Typefully (open in browser)...")
    if text:
        url = f"https://typefully.com/new?text={requests.utils.quote(text)}"
        print(f"✅ Open this link to post: {url}")
    else:
        print("❌ No post to submit.")

if __name__ == "__main__":
    post = generate_post()
    submit_to_typefully(post)
