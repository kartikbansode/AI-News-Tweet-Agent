from cohere_bot import generate_post
from twitter_bot import post_to_twitter

tweet = generate_post()
post_to_twitter(tweet)
