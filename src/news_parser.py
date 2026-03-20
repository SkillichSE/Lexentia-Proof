"""
News Parser for ModelLens
Fetches AI news from reliable RSS feeds.
"""

import json
import re
import time
import feedparser
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime

# RSS feeds that reliably cover AI model releases and updates
RSS_FEEDS = [
    {
        "url": "https://huggingface.co/blog/feed.xml",
        "source": "Hugging Face",
        "keywords": ["model", "release", "launch", "llm", "benchmark", "fine-tun", "open"]
    },
    {
        "url": "https://blog.google/technology/ai/rss/",
        "source": "Google AI Blog",
        "keywords": ["gemini", "model", "ai", "release", "update"]
    },
    {
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "source": "AWS ML Blog",
        "keywords": ["model", "llm", "inference", "release", "bedrock", "sagemaker"]
    },
    {
        "url": "https://developer.nvidia.com/blog/feed/",
        "source": "NVIDIA Developer",
        "keywords": ["model", "llm", "inference", "release", "nim", "gpu"]
    },
    {
        "url": "https://www.together.ai/blog/rss.xml",
        "source": "Together AI",
        "keywords": ["model", "release", "open", "inference", "fine-tun"]
    },
    {
        "url": "https://openai.com/news/rss.xml",
        "source": "OpenAI",
        "keywords": ["model", "release", "gpt", "update", "api"]
    },
    {
        "url": "https://www.anthropic.com/rss.xml",
        "source": "Anthropic",
        "keywords": ["claude", "model", "release", "update", "api"]
    },
    {
        "url": "https://mistral.ai/feed",
        "source": "Mistral AI",
        "keywords": ["model", "release", "mistral", "update"]
    },
]

KEYWORDS_ALWAYS_INCLUDE = [
    "llm", "language model", "gpt", "llama", "gemini", "claude", "mistral",
    "qwen", "deepseek", "release", "launched", "benchmark", "open source",
    "open-source", "api", "fine-tun", "instruct", "inference"
]

# feedparser timeout workaround — set socket timeout via urllib
import socket
_DEFAULT_TIMEOUT = 15


def parse_date(entry) -> str:
    """Try to extract a parseable ISO date from a feed entry."""
    for field in ("published", "updated", "created"):
        val = entry.get(field, "")
        if not val:
            continue
        try:
            dt = parsedate_to_datetime(val)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            pass
        # Already ISO-ish
        if "T" in val or val.count("-") >= 2:
            return val
    return datetime.now(timezone.utc).isoformat()


def is_relevant(title: str, summary: str, keywords: list) -> bool:
    text = (title + " " + summary).lower()
    feed_match   = any(kw.lower() in text for kw in keywords)
    global_match = any(kw in text for kw in KEYWORDS_ALWAYS_INCLUDE)
    return feed_match or global_match


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:280]


def fetch_feed_with_retry(url: str, retries: int = 2) -> feedparser.FeedParserDict:
    """Parse feed with timeout and retry support."""
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(_DEFAULT_TIMEOUT)
    try:
        for attempt in range(retries + 1):
            try:
                feed = feedparser.parse(url)
                # feedparser returns bozo=True on errors but still may have entries
                if feed.entries or attempt == retries:
                    return feed
                time.sleep(2)
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(2)
        return feedparser.parse(url)
    finally:
        socket.setdefaulttimeout(old_timeout)


def fetch_all_news() -> list:
    items = []
    seen_titles = set()

    for feed_cfg in RSS_FEEDS:
        print(f"  📡 {feed_cfg['source']}...", end=" ", flush=True)
        try:
            feed = fetch_feed_with_retry(feed_cfg["url"])
            count = 0
            for entry in feed.entries[:20]:
                title   = entry.get("title", "").strip()
                link    = entry.get("link", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))

                if not title or title in seen_titles:
                    continue
                # Relaxed filtering: include if title alone matches, even without summary
                if not is_relevant(title, summary, feed_cfg["keywords"]):
                    # Still include any entry from trusted AI-focused sources
                    if feed_cfg["source"] not in ("Hugging Face", "Together AI", "OpenAI",
                                                   "Anthropic", "Mistral AI"):
                        continue

                seen_titles.add(title)
                items.append({
                    "title":   title,
                    "link":    link,
                    "date":    parse_date(entry),
                    "source":  feed_cfg["source"],
                    "summary": summary,
                })
                count += 1

            print(f"{count} items")
        except Exception as e:
            print(f"⚠️  error: {e}")

    # Sort newest first
    items.sort(key=lambda x: x["date"], reverse=True)

    # Deduplicate by title again (cross-feed)
    seen = set()
    unique = []
    for item in items:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique.append(item)

    return unique[:30]


def save_news(items: list):
    Path("../docs/data/results").mkdir(parents=True, exist_ok=True)
    out = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count":   len(items),
        "items":   items,
    }
    path = "../docs/data/results/news.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"💾 {len(items)} news items saved")


if __name__ == "__main__":
    print("🔍 Fetching AI news...")
    items = fetch_all_news()
    save_news(items)
    print("✨ Done!")

