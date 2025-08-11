import os
import requests
import json
import random
import re
from datetime import datetime
from twitter_api import TwitterClient
import urllib.parse

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
        with open("posted_articles.json", "r", encoding='utf-8') as f:
            content = f.read().strip()
            print(f"📂 Content of posted_articles.json: {content}")
            if not content:
                print("📂 posted_articles.json is empty, initializing with []")
                return []
            return [urllib.parse.unquote(url.encode().decode('unicode_escape')) for url in json.loads(content)]
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"📂 Error loading posted_articles.json: {str(e)}. Initializing with []")
        with open("posted_articles.json", "w", encoding='utf-8') as f:
            json.dump([], f)
        return []

def save_posted_url(url):
    """Save a new article URL to the list."""
    posted_urls = load_posted_urls()
    decoded_url = urllib.parse.unquote(url.encode().decode('unicode_escape'))
    posted_urls.append(decoded_url)
    with open("posted_articles.json", "w", encoding='utf-8') as f:
        json.dump(posted_urls[-100:], f)

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
                if a.get("url") and urllib.parse.unquote(a["url"].encode().decode('unicode_escape')) not in posted_urls and a.get("title") and len(a.get("title", "")) > 10
            ]
            if not available_articles:
                print(f"📰 No new quality articles available for {url}")
                continue
            article = random.choice(available_articles)
            print(f"✅ Selected article: {article['title']}")
            return {
                "title": (article.get("title") or "Untitled News").strip(),
                "description": (article.get("description") or "").strip(),
                "content": (article.get("content") or "").strip(),
                "url": urllib.parse.unquote(article.get("url").encode().decode('unicode_escape') or "").strip(),
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
            "title": "Tech Innovation Surges Globally",
            "description": "Companies push AI and sustainability.",
            "content": "Tech firms invest heavily in AI. Green tech drives growth. Efficiency improves with new tools. Industries adopt eco-solutions. Global markets evolve rapidly. Updates are ongoing. Stay informed.",
            "url": "https://example.com/tech-news",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Climate Summit Sets New Goals",
            "description": "Leaders pledge carbon cuts.",
            "content": "Summit agreements reduce emissions. Countries boost green projects. Funding increases for sustainability. Climate action is key. Progress is tracked globally. More details to come. Stay updated.",
            "url": "https://example.com/climate-news",
            "published_at": datetime.utcnow().isoformat()
        }
    ]
    return random.choice(mock_articles)

def generate_hashtags(text):
    """Generate 3-4 relevant hashtags from text, including #verixanews and #verixa."""
    words = text.lower().split()
    stop_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should', 'news', 'more', 'than', 'when', 'where', 'what', 'which', 'their'}
    keywords = [word.strip(".,!?()[]{}\"\'") for word in words if len(word) > 4 and word.isalpha() and word not in stop_words]
    hashtags = [f"#{word.capitalize()}" for word in list(dict.fromkeys(keywords))[:1]]  # One content hashtag
    trending = random.sample([
        "#BreakingNews", "#GlobalNews", "#Headlines", "#TechUpdate", "#SpaceNews"
    ], 2)  # Pick 2 trending hashtags
    return hashtags + trending + ["#verixanews", "#verixa"]  # Always include #verixanews and #verixa

def summarize_text(text, max_sentences=5):
    """Summarize text to a set number of sentences without cutting mid-sentence."""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:max_sentences])

def trim_to_twitter_limit(text, url, hashtags):
    """Trim text so that tweet stays under 280 chars, cutting at sentence boundaries."""
    hashtag_str = " ".join(hashtags)
    max_len = 280 - (len(url) + len(hashtag_str) + 18)  # 18 = len("Read full article - ") + spaces/newlines

    sentences = re.split(r'(?<=[.!?]) +', text)
    trimmed = ""
    for s in sentences:
        if len(trimmed) + len(s) + 1 <= max_len:
            trimmed += (s + " ")
        else:
            break
    return trimmed.strip()

def create_tweet(article):
    """Create a summarized tweet ensuring no mid-sentence cuts."""
    title = article.get('title', 'Breaking News')
    description = article.get('description', '').strip()
    content = article.get('content', '').strip()
    url = urllib.parse.unquote(article.get('url', 'https://example.com').encode().decode('unicode_escape'))

    # Merge text for summarization
    raw_text = f"{title}. {description} {content}".strip()
    summary = summarize_text(raw_text, max_sentences=6)

    # Generate hashtags
    hashtags = generate_hashtags(raw_text)[:4]

    # Trim summary so tweet fits and ends at a sentence boundary
    clean_summary = trim_to_twitter_limit(summary, url, hashtags)

    # Build tweet
    tweet = f"{clean_summary}\nRead full article - {url}\n{' '.join(hashtags)}"

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
