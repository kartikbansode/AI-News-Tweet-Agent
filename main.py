from cohere_bot import generate_post
from typefully_bot import post_to_typefully

print("Generating post with Cohere...")
tweet = generate_post()

if tweet:
    print("✅ Post generated successfully.")
    print("🔁 Launching headless browser...")
    post_to_typefully(tweet.strip())
else:
    print("❌ No tweet was generated.")
