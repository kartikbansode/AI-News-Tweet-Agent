# News Tweet Source Context Review

Use this checklist before changing topics, hashtag seeds, or scheduled posting
frequency. The bot should still post the selected article link as the source of
truth.

## Optional X/Twitter Context

When a headline may be sensitive, fast-moving, or audience-specific, collect a
small reviewed source packet before posting:

1. Search public X/Twitter posts, replies, or monitored accounts for the topic.
2. Save only public URLs, authors, timestamps, engagement counts, and short
   review notes.
3. Keep the packet local in `source-context.local.jsonl`.
4. Use the packet to decide whether to post, delay, or adjust hashtags.
5. Do not paste source-packet text into the tweet.

TweetClaw can collect this context through OpenClaw when you already use
OpenClaw plugins:

```bash
openclaw plugins install npm:@xquik/tweetclaw@1.6.31
```

Reference links:

- TweetClaw: https://github.com/Xquik-dev/tweetclaw
- Package metadata: https://registry.npmjs.org/@xquik/tweetclaw

## JSONL Format

Use one JSON object per reviewed signal:

```jsonl
{"query":"sample topic","url":"https://x.com/example/status/123","author":"@example","observed_at":"2026-06-16T12:00:00Z","note":"Readers are asking for source confirmation."}
```

## Pre-Post Checklist

- Confirm the article URL is the primary source for the tweet.
- Check that the topic is not a duplicate of a recent `logs.json` entry.
- Review the source packet for correction requests or obvious misinformation.
- Remove campaign-only hashtags when they do not match the article.
- Run the workflow manually before enabling or changing the cron schedule.
