import logging
import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "The Economist": "https://www.economist.com/latest/rss.xml",
    "WSJ": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "Business Times Singapore": "https://www.businesstimes.com.sg/rss/all-news",
    "Straits Times Singapore": "https://www.straitstimes.com/news/singapore/rss.xml",
}

MAX_ARTICLES_PER_FEED = 5


def _parse_entry(entry):
    return {
        "title": entry.get("title", "No title").strip(),
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
        "summary": entry.get("summary", "").strip(),
    }


def fetch_feed(name, url):
    logger.info("Fetching: %s", name)
    try:
        parsed = feedparser.parse(url)
    except Exception as exc:
        logger.warning("Failed to fetch '%s' (%s): %s", name, url, exc)
        return {"source": name, "articles": [], "error": str(exc)}

    # feedparser doesn't raise on network errors — it sets bozo and bozo_exception
    if parsed.bozo:
        exc = parsed.get("bozo_exception", "unknown error")
        # An HTTPError with a 2xx code can still return valid entries; only
        # warn when there are genuinely no entries to show.
        if not parsed.entries:
            logger.warning("Feed '%s' returned no entries (bozo: %s)", name, exc)
            return {"source": name, "articles": [], "error": str(exc)}
        logger.warning("Feed '%s' parsed with bozo flag (%s) but returned %d entries",
                       name, exc, len(parsed.entries))

    articles = [_parse_entry(e) for e in parsed.entries[:MAX_ARTICLES_PER_FEED]]
    logger.info("  Got %d article(s) from %s", len(articles), name)
    return {"source": name, "articles": articles, "error": None}


def fetch_all():
    results = []
    for name, url in FEEDS.items():
        results.append(fetch_feed(name, url))

    failed = [r["source"] for r in results if r["error"]]
    if failed:
        logger.warning("The following feeds could not be loaded: %s", ", ".join(failed))

    return results
