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

# List of countries and sources for varied news
COUNTRIES = ["us", "gb", "ca", "au", "in", "fr", "de", "jp", "cn", "br"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn", "the-guardian-uk"]

def load_posted_urls():
    """Load previously posted article URLs."""
    try:
        with open("posted_articles.json", "r") as f:
            content = f.read().strip()
            print(f"Content of posted_articles.json: {content}")  # Log file content
            if not content:
                print("posted_articles.json is empty, initializing with []")
                return []
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading posted_articles.json: {str(e)}. Initializing with []")
        with open("posted_articles.json", "w") as f:
            json.dump([], f)  # Initialize with empty array
        return []

def save_posted_url(url):
    """Save a new article URL to the list."""
    posted_urls = load_posted_urls()
    posted_urls.append(url)
    with open("posted_articles.json", "w") as f:
        json.dump(posted_urls[-100:], f)  # Limit to last 100 URLs

def fetch_news():
    """Fetch latest global news from NewsAPI, ensuring variety."""
    posted_urls = load_posted_urls()
    queries = [
        f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?category=general&language=en&country={country}&apiKey={NEWS_API_KEY}" for country in COUNTRIES],
        f"https://newsapi.org/v2/everything?q=news&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?sources={source}&apiKey={NEWS_API_KEY}" for source in SOURCES]
    ]
    for url in queries:
        try:
            response = requests.get(url)
            print(f"NewsAPI request: {url}")
            if response.status_code != 200:
                print(f"NewsAPI error: {response.status_code} {response.text}")
                continue
            data = response.json()
            articles = data.get("articles", [])
            if not articles:
                print(f"No articles found for {url}")
                continue
            available_articles = [a for a in articles if a["url"] not in posted_urls]
            if not available_articles:
                print(f"No new articles available for {url}")
                continue
            article = random.choice(available_articles)
            print(f"Selected article: {article['title']}")
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
    # Fallback default tweet
    print("All queries failed, using fallback tweet")
    return {
        "title": "Latest News Update",
        "description": "Stay tuned for the latest global news stories.",
        "content": "Follow @verixanews",
        "url": "",
        "published_at": datetime.utcnow().isoformat()
    }

def generate_summary(text):
    """Generate a 4-6 line summary (50-80 words)."""
    sentences = text.split(". ")
    summary_sentences = sentences[:6]  # Take up to 6 sentences
    summary = ". ".join([s for s in summary_sentences if s])[:500]  # Limit to 500 chars
    words = summary.split()
    if len(words) > 80:
        summary = " ".join(words[:80]) + "..."  # Truncate to ~80 words
    elif len(words) < 50 and len(text) > len(summary):
        summary = summary + " " + text[len(summary):len(summary)+100]
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
    text = f"{article['title']} {article['description']} {article['content']}"
    summary = generate_summary(text)
    hashtags = generate_hashtags(text)
    tweet = f"{article['title']}\n\n{summary}\n\nRead more: {article['url']}\n{' '.join(hashtags)}"
    if len(tweet) > 280:
        max_summary_len = 280 - len(f"🌍 {article['title']}\n\nRead more: {article['url']}\n{' '.join(hashtags)}") - 3
        summary = summary[:max_summary_len] + "..."
        tweet = f"{article['title']}\n\n{summary}\n\nRead more: {article['url']}\n{' '.join(hashtags)}"
    return tweet

def main():
    try:
        # Fetch and process news
        article = fetch_news()
        tweet = create_tweet(article)
        # Post to Twitter
        twitter.post_tweet(tweet)
        print(f"Posted tweet: {tweet}")
        # Save the posted article URL
        save_posted_url(article["url"])
    except Exception as e:
        print(f"Error: {str(e)}")
        raise  # Raise to fail the workflow for debugging

if __name__ == "__main__":
    main()
