import os
import requests
from datetime import datetime
from twitter_api import TwitterClient  # Custom Twitter API wrapper
from transformers import pipeline  # Hugging Face transformers for summarization

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

def summarize_text(text):
    """Summarize text to fit within 280 characters using Hugging Face."""
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    max_length = 50  # Adjust to keep tweet under 280 chars with URL
    summary = summarizer(text, max_length=max_length, min_length=20, do_sample=False)
    return summary[0]["summary_text"]

def create_tweet(article):
    """Create a tweet from the article."""
    text = f"{article['title']} {article['description']}"
    summary = summarize_text(text)
    tweet = f"🌍 {summary}\nRead more: {article['url']}"
    if len(tweet) > 280:
        summary = summarize_text(text[:500])  # Truncate and retry
        tweet = f"🌍 {summary}\nRead more: {article['url']}"
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
