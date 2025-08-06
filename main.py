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

# Different post structure templates
POST_TEMPLATES = [
    {
        "name": "headline_first",
        "emoji": "📰",
        "structure": "{emoji} {title}\n\n{summary}\n\n{hashtags}\n\n🔗 Read more: {url}"
    },
    {
        "name": "breaking_style", 
        "emoji": "🚨",
        "structure": "{emoji} BREAKING: {title}\n\n📋 What's happening:\n{summary}\n\n{hashtags}\n\n📖 Full story: {url}"
    },
    {
        "name": "world_update",
        "emoji": "🌍", 
        "structure": "{emoji} Global Update\n\n📢 {title}\n\n💡 Key details:\n{summary}\n\n{hashtags}\n\n👉 More info: {url}"
    },
    {
        "name": "news_flash",
        "emoji": "⚡",
        "structure": "{emoji} NEWS FLASH\n\n{title}\n\n🔍 Here's what we know:\n{summary}\n\n{hashtags}\n\n📰 Continue reading: {url}"
    },
    {
        "name": "daily_briefing",
        "emoji": "📊",
        "structure": "{emoji} Today's Brief\n\n{title}\n\n📝 Summary for you:\n{summary}\n\n{hashtags}\n\n🌐 Source: {url}"
    },
    {
        "name": "story_spotlight",
        "emoji": "🔦",
        "structure": "{emoji} Story Spotlight\n\n📰 {title}\n\n💬 What you need to know:\n{summary}\n\n{hashtags}\n\n📱 Read the full article: {url}"
    }
]

def load_posted_urls():
    """Load previously posted article URLs."""
    try:
        with open("posted_articles.json", "r") as f:
            content = f.read().strip()
            print(f"Content of posted_articles.json: {content}")  # Log file content
            if not content:
                print("posted_articles.json is empty, initializing with []")
                return []
            return json.loads(content)
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
        "content": "We're unable to fetch a new article right now, but check back for breaking news and updates from around the world.",
        "url": "https://newsapi.org",
        "published_at": datetime.utcnow().isoformat()
    }

def generate_enhanced_summary(text):
    """Generate a more comprehensive 6-10 line summary (80-120 words) for better understanding."""
    # Combine all available text sources
    full_text = text.strip()
    
    # Split into sentences and clean them
    sentences = [s.strip() for s in full_text.split(". ") if s.strip()]
    
    # Take more sentences for better context (8-12 sentences)
    summary_sentences = sentences[:12]
    
    # Join sentences and ensure proper formatting
    summary = ". ".join(summary_sentences)
    if summary and not summary.endswith('.'):
        summary += "."
    
    # Limit to reasonable length but allow more content
    if len(summary) > 600:
        summary = summary[:600] + "..."
    
    # Ensure we have enough words for newcomers to understand
    words = summary.split()
    if len(words) < 80 and len(full_text) > len(summary):
        # Add more context if summary is too short
        remaining_text = full_text[len(summary):len(summary)+200]
        if remaining_text:
            summary = summary + " " + remaining_text.strip()
            if len(summary) > 600:
                summary = summary[:600] + "..."
    elif len(words) > 120:
        # Trim if too long but keep it informative
        summary = " ".join(words[:120]) + "..."
    
    return summary.strip()

def generate_contextual_hashtags(text, article_title):
    """Generate more relevant and varied hashtags based on content."""
    # Extract keywords from both title and content
    all_text = f"{article_title} {text}".lower()
    words = all_text.split()
    
    # Filter for meaningful keywords
    keywords = []
    for word in words:
        clean_word = word.strip(".,!?()[]{}\"'")
        if (len(clean_word) > 4 and 
            clean_word.isalpha() and 
            clean_word not in ['the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should']):
            keywords.append(clean_word)
    
    # Remove duplicates and get top keywords
    unique_keywords = list(dict.fromkeys(keywords))[:4]
    content_hashtags = [f"#{word.capitalize()}" for word in unique_keywords]
    
    # Varied trending hashtags pools
    trending_pools = [
        ["#BreakingNews", "#WorldNews", "#NewsUpdate"],
        ["#GlobalNews", "#NewsAlert", "#CurrentEvents"],
        ["#NewsToday", "#Breaking", "#WorldUpdate"],
        ["#Headlines", "#NewsFlash", "#GlobalUpdate"],
        ["#TodayNews", "#WorldEvents", "#NewsNow"]
    ]
    
    # Randomly select a trending pool
    trending = random.choice(trending_pools)
    
    # Combine and limit total hashtags
    all_hashtags = content_hashtags + trending
    return all_hashtags[:6]  # Limit to 6 total hashtags

def create_tweet(article):
    """Create a tweet with variable structure and enhanced content."""
    # Combine all available text for better summary
    full_text = f"{article['title']} {article['description']} {article['content']}".strip()
    
    # Generate enhanced summary with more content
    summary = generate_enhanced_summary(full_text)
    
    # Generate contextual hashtags
    hashtags = generate_contextual_hashtags(full_text, article['title'])
    hashtag_string = " ".join(hashtags)
    
    # Randomly select a post template
    template = random.choice(POST_TEMPLATES)
    print(f"Using template: {template['name']}")
    
    # Format the tweet using the selected template
    tweet = template['structure'].format(
        emoji=template['emoji'],
        title=article['title'],
        summary=summary,
        hashtags=hashtag_string,
        url=article['url']
    )
    
    # Ensure tweet fits within character limit
    if len(tweet) > 280:
        # Calculate available space for summary
        template_without_summary = template['structure'].replace('{summary}', '')
        other_content_length = len(template_without_summary.format(
            emoji=template['emoji'],
            title=article['title'],
            hashtags=hashtag_string,
            url=article['url']
        ))
        
        max_summary_length = 280 - other_content_length - 5  # 5 chars buffer
        
        if max_summary_length > 50:  # Ensure minimum meaningful summary length
            summary = summary[:max_summary_length].rsplit(' ', 1)[0] + "..."
            tweet = template['structure'].format(
                emoji=template['emoji'],
                title=article['title'],
                summary=summary,
                hashtags=hashtag_string,
                url=article['url']
            )
        else:
            # Fallback to simpler format if content is too long
            simple_tweet = f"{template['emoji']} {article['title']}\n\n{summary[:150]}...\n\n{hashtag_string}\n\n{article['url']}"
            tweet = simple_tweet[:280]
    
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
