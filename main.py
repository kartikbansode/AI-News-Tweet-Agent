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
# Logging Setup
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

# =========================
# Twitter Client
# =========================
twitter = TwitterClient(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
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
# Utilities
# =========================
def safe_request(url, retries=3, timeout=10):
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r
            logging.warning(f"Request failed {r.status_code}: {r.text}")
        except Exception as e:
            logging.error(f"Request error: {e}")
        time.sleep(2)
    return None

def make_hash(text):
    return hashlib.md5(text.lower().encode("utf-8")).hexdigest()

# =========================
# History Handling
# =========================
def load_json_file(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data[-MAX_HISTORY:], f, indent=2)

def load_posted_articles():
    data = load_json_file(POSTED_FILE)
    fixed = []
    for item in data:
        if isinstance(item, dict):
            fixed.append(item)
        elif isinstance(item, str):
            fixed.append({"url": item, "hash": make_hash(item), "time": ""})
    return fixed

def save_posted_article(entry):
    data = load_posted_articles()
    data.append(entry)
    save_json_file(POSTED_FILE, data)

def load_posted_tweets():
    return load_json_file(TWEET_HASH_FILE)

def save_posted_tweet(tweet_hash):
    data = load_posted_tweets()
    data.append(tweet_hash)
    save_json_file(TWEET_HASH_FILE, data)

# =========================
# Topic Detection
# =========================
TOPIC_KEYWORDS = {
    "Tech": ["ai", "tech", "software", "startup", "robot", "chip", "google", "microsoft"],
    "World": ["war", "conflict", "election", "government", "country", "minister"],
    "Business": ["market", "stock", "economy", "company", "finance", "trade"],
    "Health": ["health", "covid", "virus", "disease", "medical", "vaccine"],
    "Climate": ["climate", "environment", "carbon", "warming", "pollution", "green"],
    "Sports": ["match", "tournament", "league", "goal", "win", "team"]
}

def detect_topic(text):
    t = text.lower()
    for topic, words in TOPIC_KEYWORDS.items():
        if any(w in t for w in words):
            return topic
    return "📰 News"

# =========================
# Summarization
# =========================
def summarize_text(text, max_sentences=4):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:max_sentences])

# =========================
# Hashtags
# =========================
def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    stop = {"about","their","there","which","would","could","should","after","before","where","these"}
    keywords = [w for w in words if w not in stop]
    uniq = list(dict.fromkeys(keywords))[:2]
    tags = [f"#{w.capitalize()}" for w in uniq]
    return tags + ["#verixanews", "#verixa"]

# =========================
# Fetch News (generator)
# =========================
def fetch_news_generator():
    posted = load_posted_articles()
    posted_urls = {p.get("url") for p in posted}
    posted_hashes = {p.get("hash") for p in posted}

    queries = [
        f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?country={c}&apiKey={NEWS_API_KEY}" for c in COUNTRIES],
        *[f"https://newsapi.org/v2/top-headlines?sources={s}&apiKey={NEWS_API_KEY}" for s in SOURCES]
    ]

    seen = set()

    for q in queries:
        r = safe_request(q)
        if not r:
            continue
        data = r.json()
        for a in data.get("articles", []):
            if not a.get("title") or not a.get("url"):
                continue

            url = urllib.parse.unquote(a["url"])
            if url in seen or url in posted_urls:
                continue

            full = f"{a.get('title','')} {a.get('description','')} {a.get('content','')}"
            h = make_hash(full)
            if h in posted_hashes:
                continue

            seen.add(url)
            yield {
                "title": a.get("title", "").strip(),
                "description": (a.get("description") or "").strip(),
                "content": (a.get("content") or "").strip(),
                "url": url,
                "hash": h
            }

# =========================
# Tweet Builder
# =========================
def trim_to_limit(summary, url, hashtags):
    base_len = len(f"\nRead full article - {url}\n{' '.join(hashtags)}")
    max_len = 280 - base_len

    sentences = re.split(r'(?<=[.!?]) +', summary)
    out = ""
    for s in sentences:
        if len(out) + len(s) + 1 <= max_len:
            out += s + " "
        else:
            break
    return out.strip()

def create_tweet(article):
    raw = f"{article['title']}. {article['description']} {article['content']}".strip()
    topic = detect_topic(raw)
    summary = summarize_text(raw, max_sentences=5)

    hashtags = generate_hashtags(raw)
    clean = trim_to_limit(summary, article["url"], hashtags)

    tweet = f"{topic}\n{clean}\nRead full article - {article['url']}\n{' '.join(hashtags)}"

    # Small variation to reduce duplicate detection
    tweet += random.choice(["", " ", " 🔹", " 📢", " 🗞️"])

    return tweet

# =========================
# Main
# =========================
def main():
    logging.info("🤖 Bot started")

    posted_tweet_hashes = set(load_posted_tweets())
    tries = 0

    for article in fetch_news_generator():
        if tries >= MAX_TRIES:
            break
        tries += 1

        tweet = create_tweet(article)
        tweet_hash = make_hash(tweet)

        # Local duplicate check
        if tweet_hash in posted_tweet_hashes:
            logging.info("⚠️ Local duplicate tweet detected. Trying next article.")
            continue

                try:
            twitter.post_tweet(tweet)
            logging.info("✅ Tweet posted")

            save_posted_article({
                "url": article["url"],
                "hash": article["hash"],
                "time": datetime.utcnow().isoformat()
            })

            save_posted_tweet(tweet_hash)
            logging.info("💾 Saved article & tweet hash")
            return

        except Exception as e:
            msg = str(e).lower()
            if "duplicate" in msg:
                logging.warning("⚠️ Duplicate tweet rejected by Twitter. Trying next article.")
            else:
                logging.warning(f"⚠️ Twitter API blocked or error. Trying next article. Error: {e}")
            continue


    logging.warning("⚠️ No suitable article found to post after retries.")

if __name__ == "__main__":
    main()
