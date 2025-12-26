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
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)

COUNTRIES = ["us", "gb", "ca", "au", "in"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn", "the-guardian-uk"]

# -------------------------
# History (supports old + new formats)
# -------------------------
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
    except Exception as e:
        print(f"📂 Error loading history: {e}. Initializing []")
        with open("posted_articles.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_posted_url(url):
    posted = load_posted_urls()
    posted.append(url)
    with open("posted_articles.json", "w", encoding="utf-8") as f:
        json.dump(posted[-100:], f, indent=2)

# -------------------------
# Fetch News
# -------------------------
def fetch_news():
    if not NEWS_API_KEY:
        return create_mock_article()

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
            continue

    return create_mock_article()

def create_mock_article():
    return {
        "title": "Tech Innovation Surges Globally",
        "description": "Companies push AI and sustainability.",
        "content": "Tech firms invest heavily in AI. Green tech drives growth.",
        "url": "https://example.com/tech-news",
        "published_at": datetime.utcnow().isoformat()
    }

# -------------------------
# Helpers
# -------------------------
def summarize_text(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:max_sentences])

def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    stop = {'about','their','there','which','would','could','should','after','before','where','these'}
    keywords = [w for w in words if w not in stop]
    uniq = list(dict.fromkeys(keywords))[:3]
    tags = [f"#{w.capitalize()}" for w in uniq]
    return tags + ["#theverixanews"]

def trim_to_limit(text, url, hashtags):
    tag_str = " ".join(hashtags)
    max_len = 280 - (len(url) + len(tag_str) + len("Read full article - ") + 4)
    sentences = re.split(r'(?<=[.!?]) +', text)
    out = ""
    for s in sentences:
        if len(out) + len(s) + 1 <= max_len:
            out += s + " "
        else:
            break
    return out.strip()

def create_tweet(article):
    title = article.get("title", "").strip()
    desc = article.get("description", "").strip()
    content = article.get("content", "").strip()
    url = article.get("url")

    raw = f"{title}. {desc} {content}".strip()
    summary = summarize_text(raw, 5)
    if not summary:
        summary = title

    hashtags = generate_hashtags(raw)
    clean = trim_to_limit(summary, url, hashtags)

    tweet = f"{clean}\nRead full article - {url}\n{' '.join(hashtags)}"
    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-'*50}\n{tweet}\n{'-'*50}")
    return tweet

# -------------------------
# Main
# -------------------------
def main():
    print("🤖 Starting AI News Agent...")
    print("📰 Fetching news...")
    article = fetch_news()

    print("✍️ Creating tweet...")
    tweet = create_tweet(article)

    print("📤 Posting tweet...")
    try:
        twitter.post_tweet(tweet)
        print("✅ Tweet posted successfully!")
        if article.get("url"):
            save_posted_url(article["url"])
            print("💾 Saved article URL")
    except Exception as e:
        msg = str(e)
        print(f"⚠️ Twitter post failed: {msg}")
        if "429" in msg:
            print("⏱ Rate limit hit. Will retry next run.")
        elif "html" in msg.lower():
            print("🛡 Twitter/Cloudflare blocked the request. Will retry next run.")
        else:
            print("❌ Unexpected Twitter error.")
        # Exit gracefully (do NOT crash Actions)
        return

if __name__ == "__main__":
    main()
