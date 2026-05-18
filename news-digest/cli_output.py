from email.utils import parsedate
from datetime import datetime

TOP_N = 10

_DIVIDER = "─" * 52
_HEAVY   = "═" * 52


def _format_date(published):
    try:
        t = parsedate(published)
        return datetime(*t[:6]).strftime("%-d %b")
    except Exception:
        return ""


def print_headlines(feed_results):
    print(f"\n{_HEAVY}")
    print("  NEWS DIGEST — TOP HEADLINES")
    print(_HEAVY)

    for feed in feed_results:
        source   = feed["source"]
        articles = feed["articles"][:TOP_N]
        error    = feed.get("error")

        print(f"\n  {source.upper()}")
        print(f"  {_DIVIDER}")

        if error and not articles:
            print(f"  [feed unavailable: {error}]")
            continue

        if not articles:
            print("  [no articles retrieved]")
            continue

        for i, article in enumerate(articles, start=1):
            title = article["title"] or "Untitled"
            date = _format_date(article["published"]) if article["published"] else ""
            suffix = f" — {date}" if date else ""
            print(f"  {i}. {title}{suffix}")

    print(f"\n{_HEAVY}\n")
