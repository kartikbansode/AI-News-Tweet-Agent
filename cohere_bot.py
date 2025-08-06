import cohere
import os

def generate_post():
    print("Generating post with Cohere...")
    co = cohere.Client(os.environ['COHERE_API_KEY'])
    response = co.generate(
        model='command',
        prompt="Write a fresh, concise, insightful tweet about today's global news.",
        max_tokens=300,
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE'
    )

    tweet = response.generations[0].text.strip()
    print("✅ Post generated successfully.")
    return tweet
