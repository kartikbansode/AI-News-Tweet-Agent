# 🤖 Verixa News Agent  
[![News Bot Workflow](https://github.com/kartikbansode/ai-social-agent/actions/workflows/main.yml/badge.svg)](https://github.com/kartikbansode/ai-social-agent/actions)  

An **AI-powered social media bot** that fetches the latest global news, summarizes it into short, professional updates, and posts automatically on **Twitter (X)** and **Instagram**.  

---

## ✨ Features  
- 📰 Fetches **real-time news** from [NewsAPI](https://newsapi.org/)  
- ✍️ Summarizes articles into **5–6 lines** for readability  
- 🔗 Adds the **original article link** for full context  
- #️⃣ Auto-generates relevant hashtags (+ branded tags: `#verixanews`, `#verixa`)  
- 🐦 Posts directly to **Twitter (X)**  
- 📸 Converts tweets into styled **Instagram posts** using Meta Graph API (coming soon 🚀)  
- 🔄 Runs every **4–5 hours** automatically via GitHub Actions  

---

## 📂 Project Structure  
```

ai-social-agent/
│── main.py              # Core bot logic (fetch, summarize, post)
│── twitter\_api.py       # Twitter API client
│── posted\_articles.json # Stores posted news URLs (avoid duplicates)
│── requirements.txt     # Dependencies
│── .github/workflows/   # GitHub Actions automation

````

---

## ⚙️ Setup  

### 1. Clone the repo  
```bash
git clone https://github.com/kartikbansode/ai-social-agent.git
cd ai-social-agent
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

👉 Future update: Meta Instagram Graph API tokens for auto-posting.

---

## 🚀 Usage

### Run locally

```bash
python main.py
```

### Run on GitHub Actions

* The bot is pre-configured with a workflow file.
* It will automatically post news every few hours.

---

## 📌 Roadmap

* [x] Fetch and post news to Twitter
* [x] Summarize articles into short, professional updates
* [ ] Auto-generate **Instagram posts** with headlines in styled templates
* [ ] Add support for Threads & LinkedIn
* [ ] Improve hashtag generation with AI

---

## 🤝 Contributing

Pull requests are welcome! If you’d like to add new features, feel free to open an issue first.

---

## 📜 License

MIT License © 2025 [Kartik Bansode](https://github.com/kartikbansode)

```

