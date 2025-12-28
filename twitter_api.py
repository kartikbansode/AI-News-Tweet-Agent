from requests_oauthlib import OAuth1Session

class TwitterClient:
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        self.oauth = OAuth1Session(
            client_key=api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )

    def post_tweet(self, text):
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        response = self.oauth.post(url, json=payload)

        if response.status_code != 201:
            raise Exception(f"{response.status_code} {response.text}")

        return response.json()
