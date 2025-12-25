import time
import json
from requests_oauthlib import OAuth1Session


class TwitterClient:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        self.oauth = OAuth1Session(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        self.url = "https://api.twitter.com/2/tweets"

    def post_tweet(self, text, retries=3, timeout=15):
        """Post a tweet to Twitter/X with retries and safe error handling."""
        payload = {"text": text}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "VerixaNewsBot/1.2"
        }

        for attempt in range(1, retries + 1):
            try:
                response = self.oauth.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
            except Exception as e:
                if attempt == retries:
                    raise Exception(f"Twitter request failed: {e}")
                time.sleep(2 * attempt)
                continue

            status = response.status_code
            text_resp = response.text or ""

            # Success
            if status == 201:
                try:
                    return response.json()
                except Exception:
                    return {"status": "ok"}

            lower = text_resp.lower()

            # Duplicate tweet
            if status == 403 and "duplicate" in lower:
                raise Exception("Twitter API error: duplicate content")

            # Rate limit or temporary block (Cloudflare / spam protection)
            if status in (403, 429, 500, 502, 503, 504):
                if attempt < retries:
                    time.sleep(2 * attempt)
                    continue

            # Try to parse JSON error if possible
            try:
                err = response.json()
            except json.JSONDecodeError:
                err = text_resp[:300]

            raise Exception(f"Twitter API error: {status} {err}")

        raise Exception("Twitter API error: failed after retries")
