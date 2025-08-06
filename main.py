import os
import requests
import json
import random
from datetime import datetime

# Environment variables (set in GitHub Secrets)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")  # For free tier
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

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

class SimpleTwitterClient:
    """Simple Twitter client that handles free tier limitations"""
    
    def __init__(self, bearer_token=None, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com/2"
    
    def post_tweet(self, text):
        """Post a tweet with proper error handling for free tier"""
        try:
            # Method 1: Try with Bearer Token (Read-only for free tier)
            if self.bearer_token:
                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "text": text
                }
                
                response = requests.post(
                    f"{self.base_url}/tweets",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    print("✅ Tweet posted successfully!")
                    return response.json()
                elif response.status_code == 403:
                    print("❌ Free tier doesn't allow posting. Saving tweet locally instead...")
                    self.save_tweet_locally(text)
                    return {"status": "saved_locally"}
                else:
                    print(f"⚠️ Twitter API responded with {response.status_code}: {response.text}")
                    self.save_tweet_locally(text)
                    return {"status": "saved_locally", "error": response.text}
            
            # Fallback: Save locally if no valid credentials
            else:
                print("❌ No valid Twitter credentials found. Saving tweet locally...")
                self.save_tweet_locally(text)
                return {"status": "saved_locally"}
                
        except Exception as e:
            print(f"❌ Error posting tweet: {str(e)}")
            print("💾 Saving tweet locally instead...")
            self.save_tweet_locally(text)
            return {"status": "error", "message": str(e)}
    
    def save_tweet_locally(self, text):
        """Save tweet to local file when posting fails"""
        try:
            tweet_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "text": text,
                "length": len(text),
                "status": "pending_post"
            }
            
            # Load existing tweets
            try:
                with open("pending_tweets.json", "r") as f:
                    tweets = json.load(f)
            except FileNotFoundError:
                tweets = []
            
            tweets.append(tweet_data)
            
            # Keep only last 50 tweets
            tweets = tweets[-50:]
            
            # Save updated tweets
            with open("pending_tweets.json", "w") as f:
                json.dump(tweets, f, indent=2)
            
            print(f"💾 Tweet saved to pending_tweets.json")
            print(f"📝 Tweet preview: {text[:100]}...")
            
        except Exception as e:
            print(f"❌ Error saving tweet locally: {str(e)}")

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
                print(f"📰 No articles found for this query")
                continue
            
            # Filter out already posted articles
            available_articles = [a for a in articles if a.get("url") and a["url"] not in posted_urls]
            
            if not available_articles:
                print(f"📰 No new articles available for this query")
                continue
            
            article = random.choice(available_articles)
            print(f"✅ Selected article: {article['title']}")
            
            return {
                "title": article.get("title", "Untitled News"),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", datetime.utcnow().isoformat())
            }
            
        except Exception as e:
            print(f"❌ Error fetching news from query: {str(e)}")
            continue
    
    # Fallback to mock article
    print("📰 All queries failed, using mock article")
    return create_mock_article()

def create_mock_article():
    """Create a mock article when API fails"""
    mock_articles = [
        {
            "title": "Global Tech Innovation Reaches New Heights",
            "description": "Technology companies worldwide are pushing boundaries with artificial intelligence and sustainable solutions.",
            "content": "Major technology firms are investing billions in AI research and green technology. The focus on sustainable innovation is driving unprecedented growth in the sector. Companies are developing solutions that address climate change while advancing digital transformation. This trend is expected to continue throughout the year with significant breakthroughs anticipated.",
            "url": "https://example.com/tech-news",
            "published_at": datetime.utcnow().isoformat()
        },
        {
            "title": "International Climate Summit Yields Promising Results",
            "description": "World leaders announce new commitments to reduce carbon emissions and protect biodiversity.",
            "content": "The latest international climate summit concluded with significant agreements on carbon reduction targets. Countries have committed to accelerating their transition to renewable energy sources. New funding mechanisms for developing nations were established to support green infrastructure projects. Environmental groups have praised the collaborative approach taken by participating nations.",
            "url": "https://example.com/climate-news",
            "published_at": datetime.utcnow().isoformat()
        }
    ]
    return random.choice(mock_articles)

def generate_enhanced_summary(text):
    """Generate a comprehensive summary for better understanding."""
    full_text = text.strip()
    
    if not full_text:
        return "Stay informed with the latest news and updates from around the world."
    
    # Split into sentences and clean them
    sentences = [s.strip() for s in full_text.split(". ") if s.strip() and len(s.strip()) > 10]
    
    # Take more sentences for better context
    summary_sentences = sentences[:8]  # Reduced from 12 to fit better
    
    # Join sentences
    summary = ". ".join(summary_sentences)
    if summary and not summary.endswith('.'):
        summary += "."
    
    # Ensure reasonable length
    if len(summary) > 400:  # Reduced from 600 to fit Twitter better
        summary = summary[:400] + "..."
    
    # Ensure minimum content
    words = summary.split()
    if len(words) < 30 and len(full_text) > len(summary):
        remaining_text = full_text[len(summary):len(summary)+150]
        if remaining_text:
            summary = summary + " " + remaining_text.strip()
            if len(summary) > 400:
                summary = summary[:400] + "..."
    elif len(words) > 80:
        summary = " ".join(words[:80]) + "..."
    
    return summary.strip()

def generate_contextual_hashtags(text, article_title):
    """Generate relevant hashtags based on content."""
    all_text = f"{article_title} {text}".lower()
    words = all_text.split()
    
    # Extract keywords
    keywords = []
    stop_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should', 'news', 'more', 'than', 'when', 'where', 'what', 'which', 'their'}
    
    for word in words:
        clean_word = word.strip(".,!?()[]{}\"'").lower()
        if (len(clean_word) > 3 and 
            clean_word.isalpha() and 
            clean_word not in stop_words):
            keywords.append(clean_word)
    
    # Get unique keywords
    unique_keywords = list(dict.fromkeys(keywords))[:3]
    content_hashtags = [f"#{word.capitalize()}" for word in unique_keywords]
    
    # Trending hashtags
    trending_pools = [
        ["#BreakingNews", "#WorldNews"],
        ["#GlobalNews", "#NewsAlert"],
        ["#Headlines", "#NewsFlash"],
        ["#TodayNews", "#WorldUpdate"],
        ["#NewsNow", "#CurrentEvents"]
    ]
    
    trending = random.choice(trending_pools)
    all_hashtags = content_hashtags + trending
    return all_hashtags[:4]  # Limit to 4 hashtags

def create_tweet(article):
    """Create a tweet with variable structure and enhanced content."""
    full_text = f"{article['title']} {article['description']} {article['content']}".strip()
    
    summary = generate_enhanced_summary(full_text)
    hashtags = generate_contextual_hashtags(full_text, article['title'])
    hashtag_string = " ".join(hashtags)
    
    # Select random template
    template = random.choice(POST_TEMPLATES)
    print(f"🎨 Using template: {template['name']}")
    
    # Format tweet
    tweet = template['structure'].format(
        emoji=template['emoji'],
        title=article['title'],
        summary=summary,
        hashtags=hashtag_string,
        url=article['url']
    )
    
    # Ensure it fits Twitter's limit
    if len(tweet) > 270:  # Leave some buffer
        # Calculate space for summary
        template_without_summary = template['structure'].replace('{summary}', '')
        other_content = template_without_summary.format(
            emoji=template['emoji'],
            title=article['title'],
            hashtags=hashtag_string,
            url=article['url']
        )
        
        max_summary_length = 270 - len(other_content) - 5
        
        if max_summary_length > 30:
            summary = summary[:max_summary_length].rsplit(' ', 1)[0] + "..."
            tweet = template['structure'].format(
                emoji=template['emoji'],
                title=article['title'],
                summary=summary,
                hashtags=hashtag_string,
                url=article['url']
            )
        else:
            # Simplified format
            tweet = f"{template['emoji']} {article['title'][:100]}...\n\n{hashtag_string}\n\n{article['url']}"
    
    return tweet

def main():
    try:
        print("🤖 Starting AI News Agent...")
        
        # Initialize Twitter client
        twitter = SimpleTwitterClient(
            bearer_token=TWITTER_BEARER_TOKEN,
            api_key=TWITTER_API_KEY,
            api_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Fetch news
        print("📰 Fetching news...")
        article = fetch_news()
        
        # Create tweet
        print("✍️ Creating tweet...")
        tweet = create_tweet(article)
        
        print(f"\n📝 Generated tweet ({len(tweet)} chars):")
        print("-" * 50)
        print(tweet)
        print("-" * 50)
        
        # Post tweet
        print("\n📤 Posting tweet...")
        result = twitter.post_tweet(tweet)
        
        # Save article URL
        if article.get("url"):
            save_posted_url(article["url"])
            print(f"💾 Saved article URL to history")
        
        print(f"✅ Process completed successfully!")
        
        # Show result summary
        if result.get("status") == "saved_locally":
            print("\n📋 SUMMARY:")
            print("- Tweet was generated successfully")
            print("- Saved to pending_tweets.json (Twitter API limitations)")
            print("- Article URL added to history")
            print("- Ready for manual posting when API access is available")
        
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        print("🔍 This might be due to API rate limits or permissions")
        print("💡 Check your API keys and try again later")
        raise

if __name__ == "__main__":
    main()
