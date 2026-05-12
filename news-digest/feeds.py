import feedparser

FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "The Economist": "https://www.economist.com/latest/rss.xml",
    "WSJ": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "Business Times Singapore": "https://www.businesstimes.com.sg/rss/all-news",
    "Straits Times Singapore": "https://www.straitstimes.com/news/singapore/rss.xml",
}

MAX_ARTICLES_PER_FEED = 5


def fetch_feed(name, url):
    parsed = feedparser.parse(url)
    articles = []
    for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
        articles.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
        })
    return {"source": name, "articles": articles, "status": parsed.bozo}


def fetch_all():
    results = []
    for name, url in FEEDS.items():
        results.append(fetch_feed(name, url))
    return results
