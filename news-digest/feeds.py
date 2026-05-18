import logging
import re
import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FEEDS = {
    "BBC News": ["http://feeds.bbci.co.uk/news/rss.xml"],
    "The Economist": ["https://www.economist.com/latest/rss.xml"],
    "WSJ": ["https://feeds.a.dj.com/rss/RSSWorldNews.xml"],
    "Bloomberg": ["https://feeds.bloomberg.com/markets/news.rss"],
    "Business Times Singapore": [
        "https://www.businesstimes.com.sg/rss/singapore",
        "https://www.businesstimes.com.sg/rss/international",
    ],
    "Straits Times Singapore": ["https://www.straitstimes.com/news/singapore/rss.xml"],
}

MAX_ARTICLES_PER_FEED = 10


def _strip_tags(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _parse_entry(entry):
    return {
        "title": _strip_tags(entry.get("title", "No title")),
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
        "summary": _strip_tags(entry.get("summary", "")),
    }


def fetch_feed(name, urls):
    logger.info("Fetching: %s", name)
    seen = set()
    articles = []

    for url in urls:
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:
            logger.warning("Failed to fetch '%s' (%s): %s", name, url, exc)
            continue

        if parsed.bozo and not parsed.entries:
            exc = parsed.get("bozo_exception", "unknown error")
            logger.warning("Feed '%s' (%s) returned no entries (bozo: %s)", name, url, exc)
            continue

        for entry in parsed.entries:
            link = entry.get("link", "")
            if link and link in seen:
                continue
            seen.add(link)
            articles.append(_parse_entry(entry))

    articles = articles[:MAX_ARTICLES_PER_FEED]
    logger.info("  Got %d article(s) from %s", len(articles), name)
    error = None if articles else "No articles retrieved"
    return {"source": name, "articles": articles, "error": error}


def fetch_all():
    results = []
    for name, urls in FEEDS.items():
        results.append(fetch_feed(name, urls))

    failed = [r["source"] for r in results if r["error"]]
    if failed:
        logger.warning("The following feeds could not be loaded: %s", ", ".join(failed))

    return results
