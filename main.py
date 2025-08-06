import os
import requests
import json
import random
from datetime import datetime
from twitter_api import TwitterClient  # Custom Twitter API wrapper

# Environment variables (set in GitHub Secrets)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# Initialize Twitter client
twitter = TwitterClient(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)

# List of countries for varied news (fallback if main query fails)
COUNTRIES = ["us", "gb", "ca", "au", "in", "fr", "de", "jp", "cn", "br"]

def load_posted_urls():
    """Load previously posted article URLs."""
    try:
        with open("posted_articles.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_posted_url(url):
    """Save a new article URL to the list."""
    posted_urls = load_posted_urls()
    posted_urls.append(url)
    # Limit to last 100 URLs to prevent file growth
    with open("posted_articles.json", "w") as f:
        json.dump(posted_urls[-100:], f)

def fetch_news():
    """Fetch latest global news from NewsAPI, ensuring variety."""
    posted_urls = load_posted_urls()
    # Try general query first
    queries = [
        f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?category=general&language=en&country={country}&apiKey={NEWS_API_KEY}" for country in COUNTRIES]
    ]
    for url in queries:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"NewsAPI error for {url}: {response.status_code} {response.text}")
                continue
            articles = response.json().get("articles", [])
            if not articles:
                print(f"No articles found for {url}")
                continue
            # Filter out previously posted articles
            available_articles = [a for a in articles if a["url"] not in posted_urls]
            if not available_articles:
                print(f"No new articles available for {url}")
                continue
            article = random.choice(available_articles)  # Pick a random new article
            return {
                "title": article["title"],
                "description": article["description"] or "",
                "content": article.get("content", "") or "",
                "url": article["url"],
                "published_at": article["publishedAt"]
            }
        except Exception as e:
            print(f"Error fetching news from {url}: {str(e)}")
            continue
    raise Exception("No articles found after trying all queries")

def generate_summary(text):
    """Generate a 4-6 line summary (50-80 words)."""
    sentences = text.split(". ")
    summary_sentences = sentences[:6]  # Take up to 6 sentences
    summary = ". ".join([s for s in summary_sentences if s])[:500]  # Limit to 500 chars
    words = summary.split()
    if len(words) > 80:
        summary = " ".join(words[:80]) + "..."  # Truncate to ~80 words
    elif len(words) < 50:
        summary = summary + " " + (article["content"][:100] if article["content"] else "")  # Add content if short
    return summary.strip()

def generate_hashtags(text):
    """Generate relevant hashtags from text."""
    words = text.lower().split()
    keywords = [word.strip(".,!?") for word in words if len(word) > 4 and word.isalpha()]
    hashtags = [f"#{word.capitalize()}" for word in keywords[:3]]  # Pick top 3 keywords
    trending = ["#BreakingNews", "#WorldNews", "#NewsUpdate"]
    return hashtags + trending

def create_tweet(article):
    """Create a properly structured tweet from the article."""
    text = f"{article['title']} {article['description']}"
    summary = generate
