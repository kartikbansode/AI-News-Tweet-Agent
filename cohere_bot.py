import cohere
import os

def generate_post():
    print("Generating post with Cohere...")
    co = cohere.Client(os.environ["COHERE_API_KEY"])

    response = co.generate(
        model="command",
        prompt="Write a fresh, concise, and insightful social media post about today's global news or trending topic.",
        max_tokens=300,
        temperature=0.7,
    )
    
    generation = response.generations[0].text
    print("✅ Post generated successfully.")
    return generation.strip()
