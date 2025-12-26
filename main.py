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

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

COUNTRIES = ["us", "gb", "ca", "au", "in"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn", "the-guardian-uk"]
POSTED_FILE = "posted_articles.json"
TWEET_HASH_FILE = "posted_tweets.json"

MAX_HISTORY = 400
MAX_ARTICLE_TRIES = 10
MAX_POST_RETRIES = 3
MAX_RUNTIME = 300  # seconds (5 minutes)

# =========================
# Utils
# =========================
def safe_request(url, retries=2):
    for _ in range(retries):
        try:
            return requests.get(url, timeout=10)
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

def save_article(entry):
    data = load_articles()
    data.append(entry)
    save_json(POSTED_FILE, data)

def load_tweet_hashes():
    return set(load_json(TWEET_HASH_FILE))

def save_tweet_hash(h):
    data = load_json(TWEET_HASH_FILE)
    data.append(h)
    save_json(TWEET_HASH_FILE, data)

# =========================
# Summarize & Hashtags
# =========================
def summarize(text, max_sentences=2):
    s = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(s[:max_sentences])

def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    stop = {"about","their","there","which","would","could","should","after","before","where","these"}
    keywords = [w for w in words if w not in stop]
    uniq = list(dict.fromkeys(keywords))[:3]
    tags = [f"#{w.capitalize()}" for w in uniq]
    tags.append("#theverixanews")
    return tags

# =========================
# Fetch Articles
# =========================
def fetch_articles():
    posted = load_articles()
    urls = {p["url"] for p in posted}
    hashes = {p["hash"] for p in posted}

    queries = [
        f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?country={c}&apiKey={NEWS_API_KEY}" for c in COUNTRIES],
        *[f"https://newsapi.org/v2/top-headlines?sources={s}&apiKey={NEWS_API_KEY}" for s in SOURCES]
    ]

    for q in queries:
        r = safe_request(q)
        if not r or r.status_code != 200:
            continue
        for a in r.json().get("articles", []):
            if not a.get("title") or not a.get("url"):
                continue
            url = urllib.parse.unquote(a["url"])
            full = f"{a.get('title','')} {a.get('description','')} {a.get('content','')}"
            h = make_hash(full)
            if url not in urls and h not in hashes:
                yield {
                    "title": a["title"].strip(),
                    "description": (a.get("description") or "").strip(),
                    "content": (a.get("content") or "").strip(),
                    "url": url,
                    "hash": h
                }

# =========================
# Tweet Builder
# =========================
def create_tweet(article):
    base = f"{article['title']}. {article['description']} {article['content']}"
    summary = summarize(base, 2)
    hashtags = generate_hashtags(base)
    variation = random.choice(["", " Update.", " Breaking.", " Latest report."])

    tweet = (
        f"{summary}{variation}\n\n"
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

    start_time = time.time()
    tweet_hashes = load_tweet_hashes()
    article_count = 0

    for article in fetch_articles():
        if time.time() - start_time > MAX_RUNTIME:
            break
        if article_count >= MAX_ARTICLE_TRIES:
            break
        article_count += 1

        tweet = create_tweet(article)
        h = make_hash(tweet)

        if h in tweet_hashes:
            continue

        for post_try in range(1, MAX_POST_RETRIES + 1):
            if time.time() - start_time > MAX_RUNTIME:
                break
            try:
                print("Trying to post tweet...")
                result = twitter.post_tweet(tweet)
                print("Tweet posted.")
                logging.info(f"Tweet posted: {result}")

                save_article({
                    "url": article["url"],
                    "hash": article["hash"],
                    "time": datetime.utcnow().isoformat()
                })
                save_tweet_hash(h)
                return
            except Exception as e:
                print(f"Post attempt {post_try} failed: {e}")
                logging.warning(f"Post attempt {post_try} failed: {e}")
                time.sleep(10)

    print("No tweet posted this run. Exiting.")
    logging.error("No tweet posted this run.")

if __name__ == "__main__":
    main()
