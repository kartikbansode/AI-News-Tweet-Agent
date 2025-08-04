import os
import json
import random
import requests
import tweepy

# Load prompt configs
with open("config.json") as f:
    config = json.load(f)

# --- Generate Content (you can upgrade this with real AI later)
def generate_caption():
    prompts = config["prompts"]
    return random.choice(prompts)

def generate_image_url():
    return "https://picsum.photos/512"  # use real AI API later

# --- Post to Twitter
def post_to_twitter(text, image=None):
    print("Posting to Twitter...")

    auth = tweepy.OAuth1UserHandler(
        os.environ['TWITTER_API_KEY'],
        os.environ['TWITTER_API_SECRET'],
        os.environ['TWITTER_ACCESS_TOKEN'],
        os.environ['TWITTER_ACCESS_SECRET']
    )
    api = tweepy.API(auth)

    # ✅ POST TEXT ONLY (no media)
    api.update_status(status=text)

# --- MAIN
if __name__ == "__main__":
    if open("status.txt").read().strip() == "ON":
        caption = generate_caption()
        image = generate_image_url()
        post_to_twitter(caption, image)
    else:
        print("Bot is OFF")
