import os
import requests

def generate_post():
    print("Generating post with Gemini...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Write a short tweet (max 280 characters) summarizing today's biggest global idea news. Be engaging."
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    print("Gemini response:", response.json())

    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except KeyError:
        print("❌ Gemini failed to return valid response.")
        return None


def send_to_typefully(tweet_text):
    print("Sending tweet to Typefully...")

    # Replace with your actual Typefully Draft URL or webhook if available
    # This is a placeholder — you may need a paid Typefully account or use a browser automation workaround.
    print("Generated tweet:\n", tweet_text)
    print("✅ Manually copy and paste this into Typefully.com (or automate via Puppeteer or Selenium later).")


if __name__ == "__main__":
    tweet = generate_post()
    if tweet:
        send_to_typefully(tweet)
    else:
        print("❌ No tweet was generated.")
