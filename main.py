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

LOG_FILE = "logs.json"

COUNTRIES = ["us", "gb", "ca", "au", "in"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn"]

# ---------------- Logs & Stats ---------------- #

def init_logs():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps({"stats": {
                "total": 0,
                "success": 0,
                "failed": 0
            }}) + "\n")

def read_stats_and_urls():
    init_logs()
    stats = {"total": 0, "success": 0, "failed": 0}
    urls = set()

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            obj = json.loads(line)
            if i == 0 and "stats" in obj:
                stats = obj["stats"]
            elif "url" in obj:
                urls.add(obj["url"])

    return stats, urls

def write_stats(stats):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    lines[0] = json.dumps({"stats": stats}) + "\n"

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

def append_log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ---------------- News ---------------- #

def fetch_news(posted_urls):
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
            fresh = [a for a in articles if a.get("url") and a["url"] not in posted_urls]
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

    return None

# ---------------- Tweet Formatting ---------------- #

def extract_source(url):
    try:
        domain = urllib.parse.urlparse(url).netloc.replace("www.", "")
        base = domain.split(".")[0]
        return base.replace("-", " ").upper()
    except:
        return "News"

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
    return main + ["#theverixanews", "#news", "viral", "trending"]

def create_tweet(article):
    title = article["title"].strip()
    url = article["url"].strip()

    source = extract_source(url)

    # If title already contains a source, don't append again
    if re.search(r"\s-\s.+$", title):
        headline = title.rstrip(".") + "."
    else:
        headline = f"{title} - {source}."

    hashtags = generate_hashtags(title)

    tweet = (
        f"{headline}\n\n"
        f"Read full article - {url}\n\n"
        f"{' '.join(hashtags)}"
    )

    if len(tweet) > 280:
        reserve = len(f"\n\nRead full article - {url}\n\n{' '.join(hashtags)}")
        allowed = 280 - reserve - 3
        short_title = title[:allowed]
        if " " in short_title:
            short_title = short_title.rsplit(" ", 1)[0]
        headline = f"{short_title}... - {source}."

        tweet = (
            f"{headline}\n\n"
            f"Read full article - {url}\n\n"
            f"{' '.join(hashtags)}"
        )

    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-'*50}\n{tweet}\n{'-'*50}")
    return tweet


def normalize_error(err: str) -> str:
    e = err.lower()

    if "cloudflare" in e or "<html" in e:
        return "Cloudflare Blocked"
    if "403" in e:
        return "403 API Forbidden"
    if "429" in e:
        return "429 Rate Limited"
    if "duplicate" in e:
        return "Duplicate Tweet"
    if "401" in e or "authentication" in e:
        return "Auth Error"
    if "timeout" in e:
        return "Request Timeout"

    return "Unknown Error"


# ---------------- Main ---------------- #

def main():
    print("🤖 Starting AI News Agent...")

    init_logs()
    stats, posted_urls = read_stats_and_urls()

    article = fetch_news(posted_urls)
    if not article:
        print("📰 No new articles found.")
        return

    title = article["title"]
    url = article["url"]

    try:
        tweet = create_tweet(article)
        print("📤 Posting tweet...")
        twitter.post_tweet(tweet)

        print("✅ Tweet posted successfully!")

        stats["total"] += 1
        stats["success"] += 1
        write_stats(stats)

        append_log({
            "time": datetime.utcnow().isoformat() + "Z",
            "status": "success",
            "title": title,
            "url": url
        })

    except Exception as e:
    raw_err = str(e)
    clean_err = normalize_error(raw_err)

    print(f"❌ Error posting tweet: {clean_err}")

    stats["total"] += 1
    stats["failed"] += 1
    write_stats(stats)

    append_log({
        "time": datetime.utcnow().isoformat() + "Z",
        "status": "failed",
        "title": title,
        "url": url,
        "error": clean_err
    })


if __name__ == "__main__":
    main()
