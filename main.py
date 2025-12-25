import os
import requests
import json
import random
import re
import hashlib
import logging
import time
from datetime import datetime
from twitter_api import TwitterClient
import urllib.parse

# =========================
# Logging
# =========================
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# Environment Variables
# =========================
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

twitter = TwitterClient(
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

# =========================
# Config
# =========================
COUNTRIES = ["us", "gb", "ca", "au", "in"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn", "the-guardian-uk"]
POSTED_FILE = "posted_articles.json"
TWEET_HASH_FILE = "posted_tweets.json"
MAX_HISTORY = 400
MAX_TRIES = 5

# =========================
# Utils
# =========================
def safe_request(url, retries=3):
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r
        except Exception as e:
            logging.warning(f"NewsAPI request error: {e}")
        time.sleep(2)
    return None

def make_hash(text):
    return hashlib.md5(text.lower().encode()).hexdigest()

def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data[-MAX_HISTORY:], f, indent=2)

# =========================
# History
# =========================
def load_articles():
    data = load_json(POSTED_FILE)
    fixed = []
    for i in data:
        if isinstance(i, dict):
            fixed.append(i)
        elif isinstance(i, str):
            fixed.append({"url": i, "hash": make_hash(i), "time": ""})
    return fixed

def save_article(article):
    data = load_articles()
    data.append(article)
    save_json(POSTED_FILE, data)

def load_tweet_hashes():
    return set(load_json(TWEET_HASH_FILE))

def save_tweet_hash(h):
    data = load_json(TWEET_HASH_FILE)
    data.append(h)
    save_json(TWEET_HASH_FILE, data)

# =========================
# Summarize
# =========================
def summarize(text, max_sentences=2):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:max_sentences])

# =========================
# Hashtags
# =========================
def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    stop = {
        "about","their","there","which","would","could","should",
        "after","before","where","these","other","first","latest"
    }
    keywords = [w for w in words if w not in stop]
    unique = list(dict.fromkeys(keywords))[:3]
    tags = [f"#{w.capitalize()}" for w in unique]
    tags.append("#theverixanews")
    return tags

# =========================
# Fetch News
# =========================
def fetch_news():
    posted = load_articles()
    posted_urls = {p["url"] for p in posted}
    posted_hashes = {p["hash"] for p in posted}

    queries = [
        f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?country={c}&apiKey={NEWS_API_KEY}" for c in COUNTRIES],
        *[f"https://newsapi.org/v2/top-headlines?sources={s}&apiKey={NEWS_API_KEY}" for s in SOURCES]
    ]

    for q in queries:
        r = safe_request(q)
        if not r:
            continue
        for a in r.json().get("articles", []):
            if not a.get("title") or not a.get("url"):
                continue

            url = urllib.parse.unquote(a["url"])
            full = f"{a.get('title','')} {a.get('description','')} {a.get('content','')}"
            h = make_hash(full)

            if url in posted_urls or h in posted_hashes:
                continue

            return {
                "title": a["title"].strip(),
                "description": (a.get("description") or "").strip(),
                "content": (a.get("content") or "").strip(),
                "url": url,
                "hash": h
            }
    return None

# =========================
# Build Tweet
# =========================
def create_tweet(article):
    base = f"{article['title']}. {article['description']} {article['content']}"
    summary = summarize(base, max_sentences=2)
    hashtags = generate_hashtags(base)

    tweet = (
        f"{summary}\n\n"
        f"Read full news - {article['url']}\n\n"
        f"{' '.join(hashtags)}"
    )
    return tweet.strip()

# =========================
# Main
# =========================
def main():
    print("Starting Verixa News Bot...")
    logging.info("Bot started")

    tweet_hashes = load_tweet_hashes()

    for attempt in range(1, MAX_TRIES + 1):
        article = fetch_news()
        if not article:
            logging.warning("No new article found.")
            break

        tweet = create_tweet(article)
        h = make_hash(tweet)

        if h in tweet_hashes:
            logging.info("Local duplicate tweet detected. Retrying...")
            continue

        try:
            result = twitter.post_tweet(tweet)
            logging.info(f"Tweet posted successfully: {result}")
            print("Tweet successfully posted.")

            save_article({
                "url": article["url"],
                "hash": article["hash"],
                "time": datetime.utcnow().isoformat()
            })
            save_tweet_hash(h)
            return

        except Exception as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
            time.sleep(10)

    # IMPORTANT: Exit cleanly so workflow shows success
    logging.error("No tweet posted this run (Twitter blocked or duplicates). Exiting gracefully.")
    print("No tweet posted this run. Will try again next schedule.")

if __name__ == "__main__":
    main()
