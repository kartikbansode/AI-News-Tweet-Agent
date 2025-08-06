import os
import requests
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

def fetch_news():
    """Fetch latest global news from NewsAPI."""
    url = f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"NewsAPI error: {response.status_code} {response.text}")
    articles = response.json().get("articles", [])
    if not articles:
        raise Exception("No articles found")
    # Pick the first article
    article = articles[0]
    return {
        "title": article["title"],
        "description": article["description"] or "",
        "url": article["url"],
        "published_at": article["publishedAt"]
    }

def generate_hashtags(text):
    """Generate relevant hashtags from text."""
    # Simple keyword extraction (replace with AI API call if available)
    words = text.lower().split()
    keywords = [word.strip(".,!?") for word in words if len(word) > 4 and word.isalpha()]
    hashtags = [f"#{word.capitalize()}" for word in keywords[:3]]  # Pick top 3 keywords
    # Add trending hashtags relevant to news
    trending = ["#BreakingNews", "#WorldNews", "#NewsUpdate"]
    return hashtags + trending

def create_tweet(article):
    """Create a tweet from the article with hashtags."""
    text = f"{article['title']} {article['description']}"
    hashtags = generate_hashtags(text)
    tweet = f"🌍 {article['title']}\nRead more: {article['url']} {' '.join(hashtags)}"
    if len(tweet) > 280:
        # Truncate title to fit within 280 characters
        max_title_len = 280 - len(f"\nRead more: {article['url']} {' '.join(hashtags)}") - 3
        tweet = f"🌍 {article['title'][:max_title_len]}...\nRead more: {article['url']} {' '.join(hashtags)}"
    return tweet

def main():
    try:
        # Fetch and process news
        article = fetch_news()
        tweet = create_tweet(article)
        # Post to Twitter
        twitter.post_tweet(tweet)
        print(f"Posted tweet: {tweet}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
