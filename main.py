import os
import requests
import datetime

def generate_post():
    print("Generating post...")

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": "Write a tweet summarizing today’s biggest idea global news. Keep it under 280 characters."
        }]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    # Print the full response for debugging
    print("Response JSON:", response.json())

    return response.json()['choices'][0]['message']['content']


def post_to_typefully(text):
    zapier_webhook = "https://hooks.zapier.com/hooks/catch/24088830/u4qbkjx/"
    response = requests.post(zapier_webhook, json={"text": text})
    if response.status_code == 200:
        print("✅ Sent to Zapier (Typefully/Twitter).")
    else:
        print("❌ Failed:", response.text)


if __name__ == "__main__":
    print("Generating post...")
    tweet = generate_post()
    print("Tweet:", tweet)
    print("Posting to Typefully...")
    post_to_typefully(tweet)
