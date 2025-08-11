# main.py
import os
import requests
import json
import random
import re
from datetime import datetime
from twitter_api import TwitterClient
import urllib.parse

# New imports
import textwrap
import base64
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
import time

# Environment variables (set in GitHub Secrets)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# Instagram credentials / session
INSTA_USERNAME = os.environ.get("INSTA_USERNAME")
INSTA_PASSWORD = os.environ.get("INSTA_PASSWORD")
# Optional: base64-encoded session JSON (set in Secrets) so CI doesn't need interactive login
INSTA_SESSION_BASE64 = os.environ.get("INSTA_SESSION_BASE64")
INSTA_SESSION_FILE = os.environ.get("INSTA_SESSION_FILE", "insta_session.json")

# Initialize Twitter client (unchanged)
twitter = TwitterClient(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)

# --- your existing constants / functions (unchanged) ---
COUNTRIES = ["us", "gb", "ca", "au", "in", "fr", "de", "jp", "cn", "br"]
SOURCES = ["bbc-news", "al-jazeera-english", "reuters", "cnn", "the-guardian-uk"]

def load_posted_urls():
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
    posted_urls = load_posted_urls()
    decoded_url = urllib.parse.unquote(url.encode().decode('unicode_escape'))
    posted_urls.append(decoded_url)
    with open("posted_articles.json", "w", encoding='utf-8') as f:
        json.dump(posted_urls[-100:], f)

def fetch_news():
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
    words = text.lower().split()
    stop_words = {'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should', 'news', 'more', 'than', 'when', 'where', 'what', 'which', 'their'}
    keywords = [word.strip(".,!?()[]{}\"\'") for word in words if len(word) > 4 and word.isalpha() and word not in stop_words]
    hashtags = [f"#{word.capitalize()}" for word in list(dict.fromkeys(keywords))[:1]]
    trending = random.sample([
        "#BreakingNews", "#GlobalNews", "#Headlines", "#TechUpdate", "#SpaceNews"
    ], 2)
    return hashtags + trending + ["#verixanews", "#verixa"]

def summarize_text(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:max_sentences])

def trim_to_twitter_limit(text, url, hashtags):
    hashtag_str = " ".join(hashtags)
    max_len = 280 - (len(url) + len(hashtag_str) + 18)
    sentences = re.split(r'(?<=[.!?]) +', text)
    trimmed = ""
    for s in sentences:
        if len(trimmed) + len(s) + 1 <= max_len:
            trimmed += (s + " ")
        else:
            break
    return trimmed.strip()

def create_tweet(article):
    title = article.get('title', 'Breaking News')
    description = article.get('description', '').strip()
    content = article.get('content', '').strip()
    url = urllib.parse.unquote(article.get('url', 'https://example.com').encode().decode('unicode_escape'))
    raw_text = f"{title}. {description} {content}".strip()
    summary = summarize_text(raw_text, max_sentences=6)
    hashtags = generate_hashtags(raw_text)[:4]
    clean_summary = trim_to_twitter_limit(summary, url, hashtags)
    tweet = f"{clean_summary}\nRead full article - {url}\n{' '.join(hashtags)}"
    print(f"📝 Generated tweet ({len(tweet)} chars):\n{'-' * 50}\n{tweet}\n{'-' * 50}")
    return tweet

# ---------------- New Instagram functions ----------------

def _maybe_write_session_file_from_base64():
    """If INSTA_SESSION_BASE64 is provided (GitHub Actions secret), decode it to session file."""
    if INSTA_SESSION_BASE64 and not os.path.exists(INSTA_SESSION_FILE):
        try:
            data = base64.b64decode(INSTA_SESSION_BASE64)
            with open(INSTA_SESSION_FILE, "wb") as f:
                f.write(data)
            print(f"🔐 Wrote Instagram session file to {INSTA_SESSION_FILE} from INSTA_SESSION_BASE64")
        except Exception as e:
            print("⚠️ Failed to decode INSTA_SESSION_BASE64:", e)

def get_instagram_client():
    """Return a logged-in instagrapi.Client or None on failure."""
    if not INSTA_USERNAME or not INSTA_PASSWORD:
        print("⚠️ INSTA_USERNAME or INSTA_PASSWORD not set; skipping Instagram.")
        return None

    _maybe_write_session_file_from_base64()

    client = Client()
    try:
        # If session file exists, try to load it first
        if os.path.exists(INSTA_SESSION_FILE):
            try:
                client.load_settings(INSTA_SESSION_FILE)
                # Attempt login (this will reuse session if valid)
                client.login(INSTA_USERNAME, INSTA_PASSWORD)
                client.dump_settings(INSTA_SESSION_FILE)
                print("🔁 Instagram: logged in using saved session/settings.")
                return client
            except Exception as e:
                print("⚠️ Saved IG session failed; will attempt fresh login:", e)

        # Fresh login and dump session
        client = Client()
        client.login(INSTA_USERNAME, INSTA_PASSWORD)
        client.dump_settings(INSTA_SESSION_FILE)
        print("🔐 Instagram: fresh login succeeded and session saved.")
        return client
    except Exception as e:
        print("❌ Instagram login/initialization failed:", e)
        return None

def create_news_image(headline, url):
    """Generate a professional news-style image."""
    W, H = 1080, 1080
    bg_color = (20, 20, 20)
    text_color = (255, 255, 255)
    accent_color = (255, 0, 0)

    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        url_font = ImageFont.truetype("arial.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        url_font = ImageFont.load_default()

    # Breaking News Banner
    draw.rectangle([(0, 0), (W, 120)], fill=accent_color)
    draw.text((40, 30), "BREAKING NEWS", font=title_font, fill=text_color)

    # Wrap headline
    wrapped_text = textwrap.fill(headline, width=25)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=title_font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(((W - w) / 2, (H - h) / 2), wrapped_text, font=title_font, fill=text_color, align="center")

    # URL at bottom
    draw.text((40, H - 50), url, font=url_font, fill=(180, 180, 180))

    image_path = "news_post.jpg"
    img.save(image_path)
    print(f"🖼 News image created at {image_path}")
    return image_path


def post_to_instagram(image_path, caption):
    """Upload image to Instagram and return True on success, False otherwise."""
    client = get_instagram_client()
    if client is None:
        print("⚠️ Instagram client not available; skipping upload.")
        return False
    try:
        # Use photo_upload (instagrapi handles resizing if needed)
        media = client.photo_upload(image_path, caption)
        print(f"✅ Posted to Instagram (pk={getattr(media, 'pk', 'unknown')})")
        return True
    except Exception as e:
        print("❌ Instagram upload failed:", e)
        return False

# ---------------- end Instagram functions ----------------

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

        # ---- New: create image + post to Instagram ----
        try:
            # headline: prefer article title, otherwise first line of tweet
            headline = article.get("title") or tweet.split("\n")[0]
            image_path = create_news_image(headline, article.get("url"))
            # Use tweet as IG caption (it already includes URL + hashtags)
            caption = tweet
            posted = post_to_instagram(image_path, caption)
            if posted:
                print("📸 Instagram post successful.")
            else:
                print("📸 Instagram post skipped/failed.")
        except Exception as e:
            print("❌ Error during Instagram flow:", e)

    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
