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

POSTED_FILE = "posted_articles.json"
LOG_FILE = "bot.log"

COUNTRIES = ["us", "gb", "ca", "au", "in"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn"]

# ---------------- Logging ---------------- #

def init_log():
    if not os.path.exists(LOG_FILE):
        stats = {"total": 0, "success": 0, "failed": 0, "errors": 0}
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps({"stats": stats}) + "\n")

def read_stats():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.loads(f.readline()).get("stats", {})
    except:
        return {"total": 0, "success": 0, "failed": 0, "errors": 0}

def write_stats(stats):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines[0] = json.dumps({"stats": stats}) + "\n"
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

def log_event(status, title, url, error=None):
    init_log()
    stats = read_stats()
    stats["total"] += 1

    if status == "success":
        stats["success"] += 1
    else:
        stats["failed"] += 1
        stats["errors"] += 1

    write_stats(stats)

    entry = {
        "time": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "title": title,
        "url": url
    }
    if error:
        entry["error"] = error

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ---------------- Posted URLs ---------------- #

def load_posted_urls():
    if not os.path.exists(POSTED_FILE):
        return []
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posted_url(url):
    urls = load_posted_urls()
    urls.append(url)
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(urls[-200:], f, indent=2)

# ---------------- News ---------------- #

def fetch_news():
    posted = set(load_posted_urls())
    queries = [
        f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?country={c}&apiKey={NEWS_API_KEY}" for c in COUNTRIES],
        *[f"https://newsapi.org/v2/top-headlines?sources={s}&apiKey={NEWS_API_KEY}" for s in SOURCES],
    ]

    for q in queries:
        try:
            r = requests.get(q, timeout=10)
            if r.status_code != 200:
                continue
            articles = r.json().get("articles", [])
            fresh = [a for a in articles if a.get("url") and a["url"] not in posted]
            if fresh:
                a = random.choice(fresh)
                return {
                    "title": a.get("title", "").strip(),
                    "description": a.get("description", "").strip(),
                    "content": a.get("content", "").strip(),
                    "url": a.get("url", "").strip()
                }
        except:
            continue

    raise Exception("No fresh articles found")

# ---------------- Text ---------------- #

def summarize_text(text, max_sentences=4):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    clean = [s.strip() for s in sentences if len(s.strip()) > 30]
    return " ".join(clean[:max_sentences])

def generate_hashtags(text):
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    stop = {"about","after","before","their","there","which","would","could",
            "should","while","where","when","these","those","other","under",
            "major","state","states","people","today","news"}

    tags = []
    for w in words:
        if w not in stop and w not in tags:
            tags.append(w)

    main = [f"#{w.capitalize()}" for w in tags[:3]]
    return main + ["#theverixanews", "#news"]

def create_tweet(article):
    title = article["title"]
    desc = article["description"]
    cont = article["content"]
    url = article["url"]

    raw = f"{title}. {desc} {cont}".strip()
    summary = summarize_text(raw, 4)

    if not summary.lower().startswith(title.lower()):
        summary = f"{title}. {summary}"

    hashtags = generate_hashtags(raw)

    tweet = f"{summary}\n\nRead full article - {url}\n\n{' '.join(hashtags)}"

    if len(tweet) > 280:
        reserve = len(f"\n\nRead full article - {url}\n\n{' '.join(hashtags)}")
        allowed = 280 - reserve - 3
        short = summary[:allowed].rsplit(" ", 1)[0] + "..."
        tweet = f"{short}\n\nRead full article - {url}\n\n{' '.join(hashtags)}"

    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-'*50}\n{tweet}\n{'-'*50}")
    return tweet

# ---------------- Main ---------------- #

def main():
    init_log()
    print("🤖 Starting AI News Agent...")
    print("📰 Fetching news...")

    article = fetch_news()
    title = article["title"]
    url = article["url"]

    try:
        tweet = create_tweet(article)
        print("📤 Posting tweet...")
        twitter.post_tweet(tweet)
        print("✅ Tweet posted successfully!")

        log_event("success", title, url)
        save_posted_url(url)

    except Exception as e:
        err = str(e)
        print(f"❌ Error posting tweet: {err}")

        if "cloudflare" in err.lower() or "<html" in err.lower():
            print("🛡 Cloudflare blocked this IP. Will retry next run.")

        log_event("failed", title, url, error=err)

if __name__ == "__main__":
    main()
