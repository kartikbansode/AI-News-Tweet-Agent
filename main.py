import os
import requests
import json
import random
import re
from datetime import datetime
from twitter_api import TwitterClient
import urllib.parse

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

def load_posted_urls():
    try:
        with open("posted_articles.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            print(f"📂 Content of posted_articles.json: {content}")
            if not content:
                return []
            data = json.loads(content)
            urls = []
            for item in data:
                if isinstance(item, str):
                    urls.append(urllib.parse.unquote(item))
                elif isinstance(item, dict) and "url" in item:
                    urls.append(urllib.parse.unquote(item["url"]))
            return urls
    except Exception:
        with open("posted_articles.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_posted_url(url):
    posted = load_posted_urls()
    posted.append(url)
    with open("posted_articles.json", "w", encoding="utf-8") as f:
        json.dump(posted[-100:], f, indent=2)

def fetch_news():
    posted_urls = load_posted_urls()
    queries = [
        f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?country={c}&apiKey={NEWS_API_KEY}" for c in COUNTRIES],
        *[f"https://newsapi.org/v2/top-headlines?sources={s}&apiKey={NEWS_API_KEY}" for s in SOURCES]
    ]

    for url in queries:
        try:
            r = requests.get(url, timeout=10)
            print(f"🌐 NewsAPI request: {url.replace(NEWS_API_KEY, '***')}")
            if r.status_code != 200:
                continue
            articles = r.json().get("articles", [])
            available = [
                a for a in articles
                if a.get("url") and a.get("title")
                and urllib.parse.unquote(a["url"]) not in posted_urls
            ]
            if available:
                a = random.choice(available)
                return {
                    "title": a.get("title", "").strip(),
                    "description": (a.get("description") or "").strip(),
                    "content": (a.get("content") or "").strip(),
                    "url": urllib.parse.unquote(a.get("url", "")),
                    "published_at": a.get("publishedAt", datetime.utcnow().isoformat())
                }
        except Exception as e:
            print(f"❌ News fetch error: {e}")

    return None

def summarize_text(text, max_sentences=5):
    s = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(s[:max_sentences])

def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    uniq = list(dict.fromkeys(words))[:3]
    return [f"#{w.capitalize()}" for w in uniq] + ["#theverixanews"]

def create_tweet(article):
    raw = f"{article['title']}. {article['description']} {article['content']}".strip()
    summary = summarize_text(raw, 5) or article["title"]
    hashtags = generate_hashtags(raw)
    tweet = f"{summary}\nRead full article - {article['url']}\n{' '.join(hashtags)}"
    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-'*50}\n{tweet}\n{'-'*50}")
    return tweet

def main():
    print("🤖 Starting AI News Agent...")
    print("📰 Fetching news...")
    article = fetch_news()

    if not article:
        print("⚠️ No article found.")
        return

    print("✍️ Creating tweet...")
    tweet = create_tweet(article)

    print("📤 Posting tweet...")
    try:
        twitter.post_tweet(tweet)
        print("✅ Tweet posted successfully!")
        save_posted_url(article["url"])
    except Exception as e:
        msg = str(e)
        if msg == "CLOUDFLARE_BLOCK":
            print("🛡 Cloudflare blocked this GitHub Action IP. Will retry next run.")
        elif msg == "RATE_LIMIT":
            print("⏱ Rate limit hit. Will retry next run.")
        else:
            print(f"❌ Twitter error: {msg}")
        return

if __name__ == "__main__":
    main()
