from cohere_bot import generate_post
from chirr_bot import post_to_twitter_via_chirr


print("Generating post with Cohere...")
tweet = generate_post()

if tweet:
    print("✅ Post generated successfully.")
    print("🔁 Launching headless browser...")
    post_to_twitter_via_chirr(tweet.strip())

else:
    print("❌ No tweet was generated.")
