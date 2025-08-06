import requests

def get_latest_news():
    url = "https://www.reddit.com/r/worldnews/top.json?limit=5&t=day"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    titles = [post["data"]["title"] for post in data["data"]["children"]]
    return titles[0] if titles else "No news found"
