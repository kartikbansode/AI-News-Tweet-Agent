import os
import requests
import datetime

def generate_post():
    prompt = "Write a short, engaging, tweet about the latest in Idea Global News."
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
    )
    return response.json()['choices'][0]['message']['content']

def post_to_typefully(text):
    response = requests.post(
        "https://api.typefully.com/v1/drafts",
        headers={
            "Authorization": f"Bearer {os.environ['TYPEFULLY_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "autoPost": True
        }
    )
    if response.status_code == 200:
        print("✅ Successfully sent to Typefully.")
    else:
        print("❌ Failed to send to Typefully:", response.text)

if __name__ == "__main__":
    print("Generating post...")
    tweet = generate_post()
    print("Tweet:", tweet)
    print("Posting to Typefully...")
    post_to_typefully(tweet)
