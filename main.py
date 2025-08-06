from news_bot.news_scraper import get_latest_news
from news_bot.cohere_bot import generate_tweet
from news_bot.tweet_bot import post_tweet

news = get_latest_news()
tweet = generate_tweet(news)
post_tweet(tweet)
print("✅ Tweet posted successfully.")
