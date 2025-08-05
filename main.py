from cohere_bot import generate_post
from chirr_bot import post_to_chirr

tweet = generate_post()
post_to_chirr(tweet)
