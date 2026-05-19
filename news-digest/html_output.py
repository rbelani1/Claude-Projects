import html
import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate


def _strip_tags(text):
    return re.sub(r"<[^>]+>", "", text or "")

OUTPUT_FILE = "index.html"
SUMMARY_MAX_CHARS = 280

GH_TOKEN = "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"
GH_REPO  = "rbelani1/Claude-Projects"
GH_WORKFLOW = "refresh.yml"
GH_BRANCH   = "claude/create-news-digest-3CqJL"
PASSWORD    = "Belani123!"

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

/* ── Password overlay ── */
#lock {
    position: fixed;
    inset: 0;
    background: #0f1117;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    z-index: 999;
}

#lock h2 {
    color: #f3f4f6;
    font-size: 1.4rem;
    font-weight: normal;
    letter-spacing: 0.04em;
}

#lock input {
    background: #1e2130;
    border: 1px solid #2d2f3a;
    color: #f3f4f6;
    font-size: 1rem;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    width: 240px;
    text-align: center;
    outline: none;
}

#lock input:focus { border-color: #3b82f6; }

#lock button {
    background: #3b82f6;
    border: none;
    color: #fff;
    font-size: 0.9rem;
    padding: 0.6rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    width: 240px;
}

#lock button:hover { background: #2563eb; }

#lock p.error {
    color: #ef4444;
    font-size: 0.8rem;
    font-family: 'Courier New', monospace;
    min-height: 1em;
}

/* ── Header ── */
header {
    max-width: 860px;
    margin: 0 auto 2.5rem;
    border-bottom: 1px solid #2d2f3a;
    padding-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem;
}

header div.header-left h1 {
    font-size: 1.75rem;
    font-weight: normal;
    color: #f3f4f6;
    letter-spacing: 0.02em;
}

header div.header-left p.timestamp {
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.35rem;
}

div.header-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.35rem;
}

p.refreshed {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    color: #6b7280;
}

button.refresh {
    background: transparent;
    border: 1px solid #3b82f6;
    color: #3b82f6;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    padding: 0.4rem 0.9rem;
    border-radius: 4px;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, color 0.15s;
}

button.refresh:hover:not(:disabled) {
    background: #3b82f6;
    color: #0f1117;
}

button.refresh:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* ── Main content ── */
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

ul.articles { list-style: none; }

ul.articles li {
    padding: 1rem 0;
    border-bottom: 1px solid #1e2130;
}

ul.articles li:last-child { border-bottom: none; }

a.headline {
    display: block;
    font-size: 1.05rem;
    color: #e5e7eb;
    text-decoration: none;
    margin-bottom: 0.3rem;
    transition: color 0.15s;
}

a.headline:hover { color: #3b82f6; }

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

/* ── Mobile ── */
@media (max-width: 600px) {
    body { padding: 1.25rem 0.85rem; }

    header {
        flex-direction: column;
        align-items: flex-start;
    }

    div.header-right {
        flex-direction: row;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        justify-content: space-between;
    }

    p.refreshed { font-size: 0.7rem; }

    header div.header-left h1 { font-size: 1.4rem; }

    a.headline { font-size: 0.975rem; }

    p.summary { font-size: 0.825rem; }
}
"""

JS = """
const PASSWORD  = '{password}';
const GH_TOKEN  = '{token}';
const GH_REPO   = '{repo}';
const GH_WORKFLOW = '{workflow}';
const GH_BRANCH   = '{branch}';

// ── Password gate ──
(function() {{
    if (localStorage.getItem('bf_auth') === PASSWORD) {{
        document.getElementById('lock').style.display = 'none';
        return;
    }}
    document.getElementById('lock').style.display = 'flex';
}})();

function unlock() {{
    const val = document.getElementById('pw').value;
    if (val === PASSWORD) {{
        localStorage.setItem('bf_auth', val);
        document.getElementById('lock').style.display = 'none';
    }} else {{
        document.getElementById('pw-error').textContent = 'Incorrect password.';
        document.getElementById('pw').value = '';
        document.getElementById('pw').focus();
    }}
}}

document.getElementById('pw').addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') unlock();
}});

// ── Refresh button ──
async function triggerRefresh() {{
    const btn = document.querySelector('button.refresh');
    btn.disabled = true;

    try {{
        const res = await fetch(
            `https://api.github.com/repos/${{GH_REPO}}/actions/workflows/${{GH_WORKFLOW}}/dispatches`,
            {{
                method: 'POST',
                headers: {{
                    'Authorization': `token ${{GH_TOKEN}}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ ref: GH_BRANCH }})
            }}
        );

        if (!res.ok) {{
            btn.textContent = '↻ Failed — try again';
            btn.disabled = false;
            return;
        }}
    }} catch(e) {{
        btn.textContent = '↻ Network error';
        btn.disabled = false;
        return;
    }}

    let secs = 45;
    btn.textContent = `↻ Refreshing ${{secs}}s`;
    const timer = setInterval(() => {{
        secs--;
        btn.textContent = `↻ Refreshing ${{secs}}s`;
        if (secs <= 0) {{
            clearInterval(timer);
            window.location.reload();
        }}
    }}, 1000);
}}

document.querySelector('button.refresh').addEventListener('click', triggerRefresh);
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
    sgt = timezone(timedelta(hours=8))
    now_sgt = datetime.now(sgt)
    timestamp = now_sgt.strftime("%A, %d %B %Y")
    refreshed = now_sgt.strftime("%H:%M SGT")
    sections = "".join(_render_section(f) for f in feed_results)

    js = JS.format(
        password=PASSWORD,
        token=GH_TOKEN,
        repo=GH_REPO,
        workflow=GH_WORKFLOW,
        branch=GH_BRANCH,
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Belani Foundry</title>
    <style>{CSS}</style>
</head>
<body>
    <div id="lock">
        <h2>The Belani Foundry</h2>
        <input id="pw" type="password" placeholder="Enter password" autocomplete="current-password">
        <button onclick="unlock()">Enter</button>
        <p class="error" id="pw-error"></p>
    </div>

    <header>
        <div class="header-left">
            <h1>The Belani Foundry</h1>
            <p class="timestamp">{timestamp}</p>
        </div>
        <div class="header-right">
            <button class="refresh">↻ Refresh</button>
            <p class="refreshed">Last refreshed {refreshed}</p>
        </div>
    </header>
    <main>
        {sections}
    </main>
    <footer>Generated on {timestamp}</footer>
    <script>{js}</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(page)

    return output_path
