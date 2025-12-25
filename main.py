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
MAX_HISTORY = 200

# =========================
# Utilities
# =========================
def safe_request(url, retries=3, timeout=10):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r
            logging.warning(f"Request failed {r.status_code}: {r.text}")
        except Exception as e:
            logging.error(f"Request error: {e}")
        time.sleep(2)
    return None

def load_posted():
    try:
        if not os.path.exists(POSTED_FILE):
            return []
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_posted(entry):
    data = load_posted()
    data.append(entry)
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(data[-MAX_HISTORY:], f, indent=2)

def make_hash(text):
    return hashlib.md5(text.lower().encode("utf-8")).hexdigest()

# =========================
# Topic Detection
# =========================
TOPIC_KEYWORDS = {
    "🧠 Tech": ["ai", "tech", "software", "startup", "robot", "chip", "google", "microsoft"],
    "🌍 World": ["war", "conflict", "election", "government", "country", "minister"],
    "💼 Business": ["market", "stock", "economy", "company", "finance", "trade"],
    "🏥 Health": ["health", "covid", "virus", "disease", "medical", "vaccine"],
    "🌱 Climate": ["climate", "environment", "carbon", "warming", "pollution", "green"],
    "⚽ Sports": ["match", "tournament", "league", "goal", "win", "team"]
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
# Fetch News
# =========================
def fetch_news():
    posted = load_posted()
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
        data = r.json()
        for a in data.get("articles", []):
            if not a.get("title") or not a.get("url"):
                continue
            url = urllib.parse.unquote(a["url"])
            full = f"{a.get('title','')} {a.get('description','')} {a.get('content','')}"
            h = make_hash(full)
            if url not in posted_urls and h not in posted_hashes:
                return {
                    "title": a.get("title", "").strip(),
                    "description": (a.get("description") or "").strip(),
                    "content": (a.get("content") or "").strip(),
                    "url": url,
                    "hash": h
                }
    return None

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
    logging.info(f"Tweet ({len(tweet)} chars): {tweet}")
    return tweet

# =========================
# Main
# =========================
def main():
    logging.info("🤖 Bot started")
    try:
        article = fetch_news()
        if not article:
            logging.warning("No new articles found.")
            return

        tweet = create_tweet(article)
        twitter.post_tweet(tweet)
        logging.info("✅ Tweet posted")

        save_posted({
            "url": article["url"],
            "hash": article["hash"],
            "time": datetime.utcnow().isoformat()
        })

        logging.info("💾 Article saved")

        # 👉 Future: call post_to_instagram(tweet, article["title"])

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
