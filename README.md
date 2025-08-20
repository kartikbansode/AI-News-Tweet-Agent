# AI News Tweet Agent  

>**Version:** 1.0
>
>**Release Date:** August 20, 2025  

An **AI-powered social media bot** that fetches the latest global news, summarizes it into short, professional updates, and posts automatically on **Twitter (X)**. 

---

##  Features  
-  Fetches **real-time news** from [NewsAPI](https://newsapi.org/)  
-  Summarizes articles into **5–6 lines** for readability  
-  Adds the **original article link** for full context  
-  Auto-generates relevant hashtags
-  Posts directly to **Twitter (X)**  
-  Runs every **4–5 hours** automatically via GitHub Actions  

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

---

##  Usage

### Run locally

```bash
python main.py
```

### Run on GitHub Actions

* The bot is pre-configured with a workflow file.
* It will automatically post news every few hours.

* Check Workflow actions here [[AI News Tweet Agent Workflow]](https://github.com/kartikbansode/ai-social-agent/actions)  

---


## 📜 License

MIT License © 2025 [Kartik Bansode](https://github.com/kartikbansode)

---

## Contact
- Email: bansodekartik00@gmail.com
- Github: https://github.com/kartikbansode



