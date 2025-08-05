import cohere
import os
from typefully_bot import post_to_typefully

def generate_post():
    print("Generating post with Cohere...")

    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        print("❌ Error: COHERE_API_KEY not found in environment variables.")
        return None

    co = cohere.Client(api_key)

    try:
        response = co.chat(
            message="Write a fresh, concise, and insightful social media post about today's global news or trending topic.",
        )
        if hasattr(response, 'text'):
            print("✅ Post generated successfully.")
            return response.text.strip()
        else:
            print(f"❌ Unexpected Cohere response: {response}")
            return None
    except Exception as e:
        print(f"❌ Error from Cohere: {e}")
        return None

if __name__ == "__main__":
    tweet = generate_post()
    if tweet:
        post_to_typefully(tweet)
    else:
        print("❌ No tweet generated.")
