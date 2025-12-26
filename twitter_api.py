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

    def post_tweet(self, text, retries=2, timeout=15):
        payload = {"text": text}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "VerixaNewsBot/1.0"
        }

        for attempt in range(1, retries + 1):
            try:
                r = self.oauth.post(self.url, json=payload, headers=headers, timeout=timeout)
            except Exception as e:
                if attempt == retries:
                    raise Exception(f"Twitter request failed: {e}")
                time.sleep(5)
                continue

            status = r.status_code
            body = r.text or ""

            # ✅ Success
            if status == 201:
                try:
                    return r.json()
                except Exception:
                    return {"status": "ok"}

            lower = body.lower()

            # 🚫 Cloudflare / HTML block
            if "<html" in lower:
                raise Exception(f"Twitter blocked request with HTML (status {status})")

            # ⏱ Rate limit
            if status == 429:
                raise Exception("Twitter API rate limit (429)")

            # ♻️ Retry some errors
            if status in (403, 500, 502, 503, 504) and attempt < retries:
                time.sleep(5)
                continue

            # Other errors
            try:
                err = r.json()
            except json.JSONDecodeError:
                err = body[:200]

            raise Exception(f"Twitter API error: {status} {err}")

        raise Exception("Twitter API failed after retries")
