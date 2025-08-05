import openai
from datetime import datetime

# Load OpenAI key from GitHub Secrets
import os
openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_tweet():
    today = datetime.now().strftime("%A, %d %B %Y")
    prompt = f"Write a short motivational tweet for {today}. Max 280 characters."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def save_to_file(text):
    with open("tweet.txt", "w") as f:
        f.write(text)

tweet = generate_tweet()
save_to_file(tweet)
print(f"Tweet generated:\n{tweet}")
