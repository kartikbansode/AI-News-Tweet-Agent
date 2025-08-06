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
    try:
        with open("posted_articles.json", "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        with open("posted_articles.json", "w") as f:
            json.dump([], f)
        return []

def save_posted_url(url):
    posted_urls = load_posted_urls()
    posted_urls.append(url)
    with open("posted_articles.json", "w") as f:
        json.dump(posted_urls[-100:], f)

def fetch_news():
    if not NEWS_API_KEY:
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
            if response.status_code != 200:
                continue
            data = response.json()
            articles = data.get("articles", [])
            available_articles = [
                a for a in articles
                if a.get("url") and a["url"] not in posted_urls and a.get("title") and len(a.get("title", "")) > 10
            ]
            if not available_articles:
                continue
            article = random.choice(available_articles)
            return {
                "title": (article.get("title") or "Untitled News").strip(),
                "description": (article.get("description") or "").strip(),
                "content": (article.get("content") or "").strip(),
                "url": urllib.parse.unquote(article.get("url") or "").strip(),
                "published_at": article.get("publishedAt", datetime.utcnow().isoformat())
            }
        except Exception:
            continue
    return create_mock_article()

def create_mock_article():
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

def generate_summary(text):
    full_text = text.replace('\n', ' ').strip() or "Breaking news update from our sources."
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    summary = ""
    sentence_count = 0
    for sentence in sentences:
        if sentence_count < 7 and len(summary + sentence + ". ") <= 700:
            summary += sentence + ". "
            sentence_count += 1
        if sentence_count >= 7:
            break

    if sentence_count < 5:
        fallback_text = "This news highlights critical developments. Authorities are responding actively. Ongoing updates are being tracked. Further details are anticipated. Stay tuned for more. The situation is evolving rapidly. Public awareness is increasing."
        fallback_sentences = re.split(r'[.!?]+', fallback_text)
        fallback_sentences = [s.strip() for s in fallback_sentences if s.strip()]
        for sentence in fallback_sentences:
            if sentence_count < 7 and len(summary + sentence + ". ") <= 700:
                summary += sentence + ". "
                sentence_count += 1
            if sentence_count >= 7:
                break

    summary = summary.strip()
    words = summary.split()
    word_count = len(words)

    if word_count > 100:
        temp_summary = ""
        temp_count = 0
        for sentence in re.split(r'[.!?]+', summary):
            sentence = sentence.strip()
            if sentence and temp_count + len(sentence.split()) <= 100:
                temp_summary += sentence + ". "
                temp_count += len(sentence.split())
            else:
                break
        summary = temp_summary.strip()

    if word_count < 60:
        summary += " " + full_text[len(summary):len(summary)+500]
        words = summary.split()
        if len(words) > 100:
            summary = " ".join(words[:100]) + "..."

    return summary.strip()

def generate_hashtags(text):
    words = text.lower().split()
    stop_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should', 'news', 'more', 'than', 'when', 'where', 'what', 'which', 'their'}
    keywords = [word.strip(".,!?()[]{}\"\'") for word in words if len(word) > 4 and word.isalpha() and word not in stop_words]
    hashtags = [f"#{word.capitalize()}" for word in list(dict.fromkeys(keywords))[:1]]
    trending = random.choice([
        ["#BreakingNews"],
        ["#GlobalNews"],
        ["#Headlines"]
    ])
    return hashtags + trending

def create_tweet(article):
    """Create a properly structured tweet from the article."""
    title = article.get('title', 'Breaking News').strip()
    description = article.get('description', '').strip()
    content = article.get('content', '').strip()
    url = urllib.parse.unquote(article.get('url', 'https://example.com'))

    # Combine all available text to generate summary
    full_text = f"{title}. {description} {content}".strip()

    # Generate summary
    summary = generate_summary(full_text)

    # If summary is too short or missing, use fallback
    if not summary or len(summary.split()) < 30:
        summary = (
            "This update covers significant developments. "
            "Stakeholders are reacting as details emerge. "
            "More updates will follow as the story evolves. "
            "Stay tuned for further information."
        )

    # Hashtags from title + summary
    hashtags = generate_hashtags(f"{title} {summary}")
    hashtag_string = " ".join(hashtags[:2])  # limit to 2

    # Structure the tweet
    tweet_parts = [
        f"📰 {title}",
        "",
        summary,
        "",
        f"🔗 Source: {url}",
        hashtag_string
    ]
    tweet = "\n".join(tweet_parts).strip()

    # Ensure tweet is within 280 chars
    if len(tweet) > 280:
        allowed_summary_len = 280 - (len(f"📰 {title}\n\n🔗 Source: {url}\n{hashtag_string}") + 6)
        summary_sentences = re.split(r'(?<=[.!?]) +', summary)
        short_summary = ""
        for sentence in summary_sentences:
            if len(short_summary) + len(sentence) <= allowed_summary_len:
                short_summary += sentence + " "
            else:
                break
        tweet_parts[2] = short_summary.strip()
        tweet = "\n".join(tweet_parts).strip()

    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-' * 50}\n{tweet}\n{'-' * 50}")
    return tweet

def main():
    try:
        print("🤖 Starting AI News Agent...")
        article = fetch_news()
        print("✍️ Creating tweet...")
        tweet = create_tweet(article)
        print("📤 Posting tweet...")
        twitter.post_tweet(tweet)
        print("✅ Tweet posted successfully!")
        if article.get("url"):
            save_posted_url(article["url"])
            print("💾 Saved article URL to history")
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
