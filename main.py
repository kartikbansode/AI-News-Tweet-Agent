import os
import requests

# Load API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_post():
    print("Generating post with Gemini...")

    endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Write a short, engaging Twitter post about a recent global innovation or idea."
                    }
                ]
            }
        ]
    }

    response = requests.post(endpoint, headers=headers, json=data)
    res_json = response.json()
    print("Gemini response:", res_json)

    if "candidates" in res_json:
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        print("❌ Gemini failed to return valid response.")
        return None

def main():
    tweet = generate_post()
    if tweet:
        print("✅ Generated Tweet:")
        print(tweet)
    else:
        print("❌ No tweet was generated.")

if __name__ == "__main__":
    main()
