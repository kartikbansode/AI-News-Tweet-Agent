import json
import random
import requests
import tweepy

# Load config
with open('config.json') as f:
    config = json.load(f)

# ---- 1. Generate content using Hugging Face (text + image) ---- #
def generate_caption():
    prompts = ["inspirational quote", "fun fact", "daily tip"]
    prompt = random.choice(prompts)
    return f"Here's your {prompt} of the day! 🌟"

def generate_image():
    return "https://picsum.photos/512"  # Replace with real AI image generator later

caption = generate_caption()
image_url = generate_image()

# ---- 2. Post to Twitter ---- #
def post_to_twitter(caption, image_url):
    auth = tweepy.OAuth1UserHandler(
        config["twitter"]["api_key"],
        config["twitter"]["api_secret"],
        config["twitter"]["access_token"],
        config["twitter"]["access_secret"]
    )
    api = tweepy.API(auth)
    img_data = requests.get(image_url).content
    with open("temp.jpg", "wb") as f:
        f.write(img_data)
    media = api.media_upload("temp.jpg")
    api.update_status(status=caption, media_ids=[media.media_id])

# ---- 3. Post to Instagram (requires setup) ---- #
def post_to_instagram(caption, image_url):
    print("Instagram posting is complex; see instructions below")

# Post
post_to_twitter(caption, image_url)
post_to_instagram(caption, image_url)

