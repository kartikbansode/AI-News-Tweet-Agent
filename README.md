# AI News Tweet Agent  

>**Version:** 1.1.0
>
>**Release Date:** December 28, 2025  

An **AI-powered social media bot** that fetches the latest global news, professional updates, and posts automatically on **Twitter (X)**. 


---
## What’s New in v1.1.0

1. Bug fix - Posts full headlines with source name once.
2. Clean tweet format with spaced sections.
3. Custom hashtag support (including #theverixanews, #news, #viral, #trending).
4. Unified [logs.json] file for: Overall stats (total, success, failed) and Line-by-line tweet history with timestamps.
5. Smarter error logging - stores causes like 403 API error or Cloudflare blocked.
6. Better duplicate prevention using logged URLs.
7. Stable scheduled runs (manual or every 4 hours).

---

##  Features  
-  Fetches **real-time news** from [NewsAPI](https://newsapi.org/)  
-  Summarizes headline for readability  
-  Adds the **original article link** for full context  
-  Auto-generates relevant hashtags
-  Posts directly to **Twitter (X)**  
-  Runs manually, or every **4-5 hours** after enabling the GitHub Actions cron
-  Supports an optional [source context review](docs/source-context-review.md) before posting sensitive or fast-moving stories

---

## 📂 Project Structure  
```

ai-social-agent/
│── .github/workflows/   # GitHub Actions automation (scheduled & manual runs)
│── logs.json            # Unified logs: stats + tweet history with timestamps
│── main.py              # Core bot logic (fetch news, format tweets, post, log stats)
│── requirements.txt     # Python dependencies
│── twitter_api.py       # Twitter/X API client


````

---

## ⚙️ Setup  

### 1. Clone the repo  
```bash
git clone https://github.com/kartikbansode/AI-News-Tweet-Agent.git
cd AI-News-Tweet-Agent
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Add your secrets in **GitHub → Repo Settings → Secrets → Actions**

| Variable                      | Description                                  |
| ----------------------------- | -------------------------------------------- |
| `NEWS_API_KEY`                | API key from [NewsAPI](https://newsapi.org/) |
| `TWITTER_API_KEY`             | Twitter/X API key                            |
| `TWITTER_API_SECRET`          | Twitter/X API secret                         |
| `TWITTER_ACCESS_TOKEN`        | Twitter/X access token                       |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter/X access token secret                |

---

##  Usage

### Run locally

```bash
python main.py
```

### Run on GitHub Actions

* The bot is pre-configured with a workflow file.
* It will post manually by default.
* Uncomment the cron schedule in `.github/workflows/post-news.yml` to post every few hours.
* Review [source context](docs/source-context-review.md) before enabling scheduled posts for sensitive topics.

* Check Workflow actions here [[AI News Tweet Agent Workflow]](https://github.com/kartikbansode/AI-News-Tweet-Agent/actions)  

---


## 📜 License

MIT License © 2025 [Kartik Bansode](https://github.com/kartikbansode)

---

## Contact
- Email: bansodekartik00@gmail.com
- Github: https://github.com/kartikbansode


