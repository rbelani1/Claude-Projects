import html
import re
from datetime import datetime, timezone
from email.utils import parsedate


def _strip_tags(text):
    return re.sub(r"<[^>]+>", "", text or "")

OUTPUT_FILE = "index.html"
SUMMARY_MAX_CHARS = 280

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: #0f1117;
    color: #d1d5db;
    font-family: 'Georgia', serif;
    font-size: 16px;
    line-height: 1.7;
    padding: 2rem 1rem;
}

header {
    max-width: 860px;
    margin: 0 auto 2.5rem;
    border-bottom: 1px solid #2d2f3a;
    padding-bottom: 1rem;
}

header h1 {
    font-size: 1.75rem;
    font-weight: normal;
    color: #f3f4f6;
    letter-spacing: 0.02em;
}

header p.timestamp {
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.35rem;
}

main {
    max-width: 860px;
    margin: 0 auto;
}

section.publication {
    margin-bottom: 3rem;
}

section.publication h2 {
    font-size: 0.75rem;
    font-weight: normal;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #9ca3af;
    border-left: 3px solid #3b82f6;
    padding-left: 0.65rem;
    margin-bottom: 1.25rem;
}

.error-notice {
    font-style: italic;
    color: #ef4444;
    font-size: 0.875rem;
    padding-left: 0.65rem;
}

ul.articles {
    list-style: none;
}

ul.articles li {
    padding: 1rem 0;
    border-bottom: 1px solid #1e2130;
}

ul.articles li:last-child {
    border-bottom: none;
}

a.headline {
    display: block;
    font-size: 1.05rem;
    color: #e5e7eb;
    text-decoration: none;
    margin-bottom: 0.3rem;
    transition: color 0.15s;
}

a.headline:hover {
    color: #3b82f6;
}

p.summary {
    font-size: 0.875rem;
    color: #9ca3af;
    margin-bottom: 0.3rem;
}

span.published {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    color: #4b5563;
}

footer {
    max-width: 860px;
    margin: 3rem auto 0;
    padding-top: 1rem;
    border-top: 1px solid #2d2f3a;
    font-size: 0.75rem;
    color: #4b5563;
    text-align: center;
}
"""


def _esc(text):
    return html.escape(text or "")


def _format_date(published):
    try:
        t = parsedate(published)
        return datetime(*t[:6]).strftime("%-d %b")
    except Exception:
        return ""


def _snippet(text, max_chars=SUMMARY_MAX_CHARS):
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars].rsplit(" ", 1)[0] + "…"


def _render_article(article):
    title = _esc(article["title"])
    link = _esc(article["link"])
    summary = _esc(_snippet(_strip_tags(article["summary"]))) if article["summary"] else ""
    published = _format_date(article["published"]) if article["published"] else ""

    headline = (
        f'<a class="headline" href="{link}" target="_blank" rel="noopener">{title}</a>'
        if link else
        f'<span class="headline">{title}</span>'
    )
    summary_html = f'<p class="summary">{summary}</p>' if summary else ""
    published_html = f'<span class="published">{published}</span>' if published else ""

    return f"""
        <li>
            {headline}
            {summary_html}
            {published_html}
        </li>"""


def _render_section(feed):
    source = _esc(feed["source"])
    articles = feed["articles"]
    error = feed.get("error")

    if error and not articles:
        body = f'<p class="error-notice">Could not load feed: {_esc(str(error))}</p>'
    else:
        items = "".join(_render_article(a) for a in articles)
        body = f'<ul class="articles">{items}\n        </ul>'

    return f"""
    <section class="publication">
        <h2>{source}</h2>
        {body}
    </section>"""


def write_html(feed_results, output_path=OUTPUT_FILE):
    timestamp = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    sections = "".join(_render_section(f) for f in feed_results)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Digest</title>
    <style>{CSS}</style>
</head>
<body>
    <header>
        <h1>News Digest</h1>
        <p class="timestamp">{timestamp}</p>
    </header>
    <main>
        {sections}
    </main>
    <footer>Generated on {timestamp}</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(page)

    return output_path
