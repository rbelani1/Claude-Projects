import logging
import math
import re
import feedparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Each source maps to a list of (url, quota) tuples.
# quota=None means use MAX_ARTICLES_PER_FEED for that URL.
FEEDS = {
    "BBC News": [
        ("http://feeds.bbci.co.uk/news/rss.xml", None),
    ],
    "Bloomberg": [
        ("https://feeds.bloomberg.com/markets/news.rss", None),
    ],
    "Straits Times Singapore": [
        ("https://www.straitstimes.com/news/singapore/rss.xml", None),
    ],
    "WSJ": [
        ("https://feeds.a.dj.com/rss/RSSWorldNews.xml", None),
    ],
    "Business Times Singapore": [
        ("https://www.businesstimes.com.sg/rss/singapore", None),
        ("https://www.businesstimes.com.sg/rss/international", None),
    ],
    "The Economist": [
        ("https://www.economist.com/latest/rss.xml", None),
    ],
    "The Mint": [
        ("https://www.livemint.com/rss/news", 4),
        ("https://www.livemint.com/rss/technology", 3),
        ("https://www.livemint.com/rss/opinion", 3),
    ],
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


def _fetch_url(url):
    try:
        parsed = feedparser.parse(url)
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return []
    if parsed.bozo and not parsed.entries:
        logger.warning("No entries from %s (bozo: %s)", url, parsed.get("bozo_exception", "?"))
        return []
    return [_parse_entry(e) for e in parsed.entries]


def _resolve_quotas(url_quotas, fetched):
    """Redistribute quota from empty feeds evenly across feeds that have articles."""
    active = [(uq, entries) for uq, entries in zip(url_quotas, fetched) if entries]
    empty  = [(uq, entries) for uq, entries in zip(url_quotas, fetched) if not entries]

    if not active:
        return []

    leftover = sum(uq[1] for uq, _ in empty)
    if leftover == 0:
        return [(uq[1], entries) for uq, entries in active]

    n = len(active)
    base, remainder = divmod(leftover, n)
    result = []
    for i, (uq, entries) in enumerate(active):
        extra = base + (1 if i < remainder else 0)
        result.append((uq[1] + extra, entries))
    return result


def fetch_feed(name, url_quotas):
    logger.info("Fetching: %s", name)

    # Resolve None quotas
    total = MAX_ARTICLES_PER_FEED
    none_count = sum(1 for _, q in url_quotas if q is None)
    fixed_sum  = sum(q for _, q in url_quotas if q is not None)
    default_q  = math.floor((total - fixed_sum) / none_count) if none_count else 0
    resolved   = [(url, default_q if q is None else q) for url, q in url_quotas]

    fetched = [_fetch_url(url) for url, _ in resolved]
    quota_entries = _resolve_quotas(resolved, fetched)

    seen = set()
    articles = []
    for quota, entries in quota_entries:
        count = 0
        for entry in entries:
            if count >= quota:
                break
            link = entry["link"]
            if link and link in seen:
                continue
            seen.add(link)
            articles.append(entry)
            count += 1

    logger.info("  Got %d article(s) from %s", len(articles), name)
    error = None if articles else "No articles retrieved"
    return {"source": name, "articles": articles, "error": error}


def fetch_all():
    results = []
    for name, url_quotas in FEEDS.items():
        results.append(fetch_feed(name, url_quotas))

    failed = [r["source"] for r in results if r["error"]]
    if failed:
        logger.warning("The following feeds could not be loaded: %s", ", ".join(failed))

    return results
