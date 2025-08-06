import os
import requests
import json
import random
import re
from datetime import datetime
from twitter_api import TwitterClient  # Use original Twitter API wrapper

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
            print(f"📂 Content of posted_articles.json: {content}")
            if not content:
                print("📂 posted_articles.json is empty, initializing with []")
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"📂 Error loading posted_articles.json: {str(e)}. Initializing with []")
        with open("posted_articles.json", "w") as f:
            json.dump([], f)
        return []

def save_posted_url(url):
    """Save a new article URL to the list."""
    posted_urls = load_posted_urls()
    posted_urls.append(url)
    with open("posted_articles.json", "w") as f:
        json.dump(posted_urls[-100:], f)  # Limit to last 100 URLs

def fetch_news():
    """Fetch latest global news from NewsAPI, ensuring variety."""
    if not NEWS_API_KEY:
        print("❌ NEWS_API_KEY not found. Using mock data...")
        return create_mock_article()
    
    posted_urls = load_posted_urls()
    queries = [
        f"https://newsapi.org/v2/top-headlines?category=general&language=en&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?category=general&language=en&country={country}&apiKey={NEWS_API_KEY}" for country in COUNTRIES],
        f"https://newsapi.org/v2/everything?q=news&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
        *[f"https://newsapi.org/v2/top-headlines?sources={source}&apiKey={NEWS_API_KEY}" for source in SOURCES]
    ]
    for url in queries:
        try:
            response = requests.get(url, timeout=10)
            print(f"🌐 NewsAPI request: {url.replace(NEWS_API_KEY, '***')}")
            if response.status_code != 200:
                print(f"❌ NewsAPI error: {response.status_code} {response.text}")
                continue
            data = response.json()
            articles = data.get("articles", [])
            if not articles:
                print(f"📰 No articles found for {url}")
                continue
            available_articles = [
                a for a in articles
                if a.get("url") and a["url"] not in posted_urls and a.get("title") and len(a.get("title", "")) > 10
            ]
            if not available_articles:
                print(f"�新聞 No new quality articles available for {url}")
                continue
            article = random.choice(available_articles)
            print(f"✅ Selected article: {article['title']}")
            return {
                "title": article.get("title", "Untitled News").strip(),
                "description": article.get("description", "").strip(),
                "content": article.get("content", "").strip(),
                "url": article.get("url", "").strip(),
                "published_at": article.get("publishedAt", datetime.utcnow().isoformat())
            }
        except Exception as e:
            print(f"❌ Error fetching news from {url}: {str(e)}")
            continue
    print("📰 All queries failed, using mock article")
    return create_mock_article()

def create_mock_article():
    """Create a mock article when API fails."""
    mock_articles = [
        {
            "title": "Global Tech Innovation Reaches New Heights",
            "description": "Technology companies worldwide are pushing boundaries with AI and sustainable solutions.",
            "content": "Major tech firms are investing billions in AI and green technology, driving growth in the sector. New advancements promise enhanced efficiency and eco-friendly solutions across industries. This trend is reshaping global markets.",
            "url": "https://example.com/tech-news",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "title": "International Climate Summit Yields Promising Results",
            "description": "World leaders announce new commitments to reduce carbon emissions.",
            "content": "The latest climate summit concluded with agreements on carbon reduction and renewable energy. Countries pledged to accelerate green initiatives and fund sustainable projects globally. These steps aim to combat climate change effectively.",
            "url": "https://example.com/climate-news",
            "published_at": datetime.utcnow().isoformat()
        }
    ]
    return random.choice(mock_articles)

def generate_summary(text):
    """Generate a 5-7 line summary (60-100 words), ensuring completeness."""
    full_text = text.strip() or "Breaking news update from our sources."
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
    
    # Build summary with at least 5 sentences, up to 7
    summary = ""
    sentence_count = 0
    for sentence in sentences:
        if sentence_count < 7 and len(summary + sentence + ". ") <= 500:
            summary += sentence + ". "
            sentence_count += 1
        if sentence_count >= 7:
            break
    
    # If too few sentences, add more content
    if sentence_count < 5 and len(full_text) > len(summary):
        remaining_text = full_text[len(summary):]
        remaining_sentences = re.split(r'[.!?]+', remaining_text)
        remaining_sentences = [s.strip() for s in remaining_sentences if s.strip() and len(s.strip()) > 15]
        for sentence in remaining_sentences:
            if sentence_count < 7 and len(summary + sentence + ". ") <= 500:
                summary += sentence + ". "
                sentence_count += 1
            if sentence_count >= 7:
                break
    
    summary = summary.strip()
    words = summary.split()
    word_count = len(words)
    
    # Adjust word count to 60-100
    if word_count > 100:
        summary = " ".join(words[:100]) + "..."
    elif word_count < 60 and len(full_text) > len(summary):
        summary += " " + full_text[len(summary):len(summary)+200]
        words = summary.split()
        if len(words) > 100:
            summary = " ".join(words[:100]) + "..."
    
    # Ensure summary ends cleanly
    if summary and not summary.endswith(('.', '!', '?')):
        summary += "..."
    
    # Count lines (approximate by splitting on periods, assuming each sentence is a line)
    lines = [s for s in re.split(r'[.!?]+', summary) if s.strip()]
    line_count = len(lines)
    
    print(f"📝 Summary ({len(summary)} chars, {word_count} words, {line_count} lines): {summary}")
    return summary.strip()

def generate_hashtags(text):
    """Generate relevant hashtags from text."""
    words = text.lower().split()
    stop_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should', 'news', 'more', 'than', 'when', 'where', 'what', 'which', 'their'}
    keywords = [word.strip(".,!?()[]{}\"\'") for word in words if len(word) > 4 and word.isalpha() and word not in stop_words]
    hashtags = [f"#{word.capitalize()}" for word in list(dict.fromkeys(keywords))[:3]]
    trending = random.choice([
        ["#BreakingNews", "#WorldNews"],
        ["#GlobalNews", "#NewsAlert"],
        ["#Headlines", "#NewsFlash"]
    ])
    return hashtags + trending

def create_tweet(article):
    """Create a properly structured tweet from the article."""
    title = article.get('title', 'Breaking News')
    description = article.get('description', '')
    content = article.get('content', '')
    url = article.get('url', 'https://example.com')
    full_text = f"{title} {description} {content}".strip()
    
    # Generate summary and hashtags
    summary = generate_summary(full_text)
    hashtags = generate_hashtags(full_text)
    hashtag_string = " ".join(hashtags[:3])  # Limit to 3 hashtags to save space
    
    # Shorten title to prioritize summary (1-2 lines, ~60 chars max)
    display_title = title if len(title) <= 60 else title[:57] + "..."
    
    # Calculate available space for summary
    base_parts = f"🌍 {display_title}\n\nSource: {url}\n{hashtag_string}"
    base_length = len(base_parts) + 4  # Account for newlines
    max_summary_len = 280 - base_length
    
    # Trim summary only if absolutely necessary, preserving completeness
    if len(summary) > max_summary_len:
        words = summary.split()
        summary = " ".join(words[:int(max_summary_len/5)]) + "..."  # Rough word-based trim
        lines = [s for s in re.split(r'[.!?]+', summary) if s.strip()]
        if len(lines) < 5:
            # Rebuild summary to ensure 5 lines
            summary = generate_summary(full_text[:max_summary_len-3]) + "..."
    
    tweet = f"🌍 {display_title}\n\n{summary}\nSource: {url}\n{hashtag_string}"
    
    # Final safety check
    if len(tweet) > 280:
        # Reduce hashtags to 2
        hashtags = hashtags[:2]
        hashtag_string = " ".join(hashtags)
        base_parts = f"🌍 {display_title}\n\nSource: {url}\n{hashtag_string}"
        base_length = len(base_parts) + 4
        max_summary_len = 280 - base_length
        summary = summary[:max_summary_len-3] + "..."
        tweet = f"🌍 {display_title}\n\n{summary}\nSource: {url}\n{hashtag_string}"
    
    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-' * 50}\n{tweet}\n{'-' * 50}")
    return tweet

def main():
    try:
        print("🤖 Starting AI News Agent...")
        print("📰 Fetching news...")
        article = fetch_news()
        print("✍️ Creating tweet...")
        tweet = create_tweet(article)
        print("📤 Posting tweet...")
        twitter.post_tweet(tweet)
        print("✅ Tweet posted successfully!")
        if article.get("url"):
            save_posted_url(article["url"])
            print(f"💾 Saved article URL to history")
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
