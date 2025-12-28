from requests_oauthlib import OAuth1Session
import json

class TwitterClient:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        self.oauth = OAuth1Session(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        self.url = "https://api.twitter.com/2/tweets"

    def post_tweet(self, text):
        payload = {"text": text}
        response = self.oauth.post(self.url, json=payload, timeout=15)

        status = response.status_code
        body = response.text or ""

        # ✅ Success
        if status == 201:
            try:
                return response.json()
            except Exception:
                return {"status": "ok"}

        lower = body.lower()

        # 🛡 Cloudflare / HTML block
        if "<html" in lower:
            raise Exception("CLOUDFLARE_BLOCK")

        # ⏱ Rate limit
        if status == 429:
            raise Exception("RATE_LIMIT")

        # Other API errors
        try:
            err = response.json()
        except json.JSONDecodeError:
            err = body[:200]

        raise Exception(f"TWITTER_ERROR_{status}: {err}")
