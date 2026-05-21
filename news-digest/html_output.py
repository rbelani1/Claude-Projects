import os
import html
from datetime import datetime, timezone, timedelta

OUTPUT_FILE = "index.html"
PASSWORD = "Belani123!"

FEEDS = [
    {"name": "BBC News",               "urls": [{"url": "https://feeds.bbci.co.uk/news/rss.xml", "quota": 10}]},
    {"name": "New York Times",         "urls": [
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",   "quota": 7},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Opinion.xml", "quota": 3},
    ]},
    {"name": "Bloomberg",              "urls": [{"url": "https://feeds.bloomberg.com/markets/news.rss", "quota": 10}]},
    {"name": "Straits Times Singapore","urls": [{"url": "https://www.straitstimes.com/news/singapore/rss.xml", "quota": 10}]},
    {"name": "WSJ",                    "urls": [
        {"url": "https://feeds.content.dowjones.io/public/rss/RSSWorldNews",   "quota": 4},
        {"url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain", "quota": 4},
        {"url": "https://feeds.content.dowjones.io/public/rss/RSSOpinion",     "quota": 2},
    ], "todayOnly": True},
    {"name": "Business Times Singapore","urls": [
        {"url": "https://www.businesstimes.com.sg/rss/singapore",    "quota": 5},
        {"url": "https://www.businesstimes.com.sg/rss/international", "quota": 5},
    ]},
    {"name": "The Economist",          "urls": [{"url": "https://www.economist.com/latest/rss.xml", "quota": 10}]},
    {"name": "The Mint",               "urls": [
        {"url": "https://www.livemint.com/rss/news",       "quota": 4},
        {"url": "https://www.livemint.com/rss/technology", "quota": 3},
        {"url": "https://www.livemint.com/rss/opinion",    "quota": 3},
    ]},
]

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
    align-items: flex-end;
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

header div.header-left p.articles-read {
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.2rem;
}

header div.header-left p.articles-read span {
    color: #22c55e;
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

/* ── Loading spinner ── */
.loading {
    color: #4b5563;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    padding: 1rem 0;
}

/* ── Main content ── */
main { max-width: 860px; margin: 0 auto; }

section.publication { margin-bottom: 3rem; }

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
    list-style: none;
}

ul.articles { list-style: none; }

ul.articles li {
    padding: 1rem 2rem 1rem 0;
    border-bottom: 1px solid #1e2130;
    position: relative;
}

ul.articles li:last-child { border-bottom: none; }

button.dismiss {
    position: absolute;
    top: 1rem;
    right: 0;
    background: transparent;
    border: none;
    color: #4b5563;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0 0.25rem;
    line-height: 1;
}

button.dismiss:hover { color: #ef4444; }

a.headline {
    display: block;
    font-size: 1.05rem;
    color: #e5e7eb;
    text-decoration: none;
    margin-bottom: 0.3rem;
    transition: color 0.15s;
    word-wrap: break-word;
}

a.headline:hover { color: #3b82f6; }

span.read-tick {
    color: #22c55e;
    font-size: 0.85rem;
    flex-shrink: 0;
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

/* ── Section nav buttons ── */
#prev-btn, #next-btn {
    position: fixed;
    right: max(1rem, calc(50vw - 430px));
    width: 2.25rem;
    height: 2.25rem;
    background: transparent;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    opacity: 0.75;
    padding: 0;
    transition: opacity 0.15s;
}

#prev-btn { bottom: 4.25rem; }
#next-btn { bottom: 1.75rem; }

#prev-btn:hover, #next-btn:hover { opacity: 1; }

#prev-btn::before, #next-btn::before {
    content: '';
    display: block;
    width: 0.65rem;
    height: 0.65rem;
    border-right: 2.5px solid #3b82f6;
    border-bottom: 2.5px solid #3b82f6;
}

#prev-btn::before { transform: rotate(225deg); margin-top: 0.35rem; }
#next-btn::before { transform: rotate(45deg);  margin-top: -0.35rem; }

/* ── Filter bar ── */
.filter-bar {
    max-width: 860px;
    margin: -1.5rem auto 2rem;
    display: flex;
    justify-content: flex-end;
}

.filter-toggle {
    display: inline-flex;
    border: 1px solid #2d2f3a;
    border-radius: 6px;
    overflow: hidden;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
}

.filter-toggle button {
    background: transparent;
    border: none;
    color: #6b7280;
    padding: 0.35rem 0.85rem;
    cursor: pointer;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    transition: background 0.15s, color 0.15s;
}

.filter-toggle button:first-child {
    border-right: 1px solid #2d2f3a;
}

.filter-toggle button.active {
    background: #3b82f6;
    color: #fff;
}

.filter-toggle button:not(.active):hover {
    background: #1e2130;
    color: #d1d5db;
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

    .filter-bar { margin: -0.75rem auto 1.5rem; }
    #prev-btn, #next-btn { right: 0.85rem; }
}
"""


def _render_skeleton(feeds):
    sections = ""
    for feed in feeds:
        name = html.escape(feed["name"])
        fid = name.replace(" ", "-")
        sections += f"""
    <section class="publication" id="feed-{fid}">
        <h2>{name}</h2>
        <ul class="articles"><li class="loading">Loading...</li></ul>
    </section>"""
    return sections


def write_html(feed_results=None, output_path=OUTPUT_FILE):
    import json
    feeds_json = json.dumps(FEEDS)
    password_json = json.dumps(PASSWORD)
    sections = _render_skeleton(FEEDS)

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
            <p class="timestamp" id="timestamp">Loading...</p>
            <p class="articles-read">Articles Read Today: <span id="read-count">—</span></p>
        </div>
        <div class="header-right">
            <p class="refreshed" id="refreshed"></p>
        </div>
    </header>
    <div class="filter-bar">
        <div class="filter-toggle">
            <button id="btn-all" onclick="setFilter('all')">All</button>
            <button id="btn-business" onclick="setFilter('business')">Business</button>
        </div>
    </div>
    <main>{sections}
    </main>
    <footer>The Belani Foundry</footer>
    <button id="prev-btn" title="Previous section"></button>
    <button id="next-btn" title="Next section"></button>

    <script>
    const PASSWORD      = {password_json};
    const FEEDS         = {feeds_json};
    const PROXY         = "https://corsproxy.io/?url=";
    const SUMMARY_MAX   = 280;
    const BUSINESS_FEEDS = new Set(["Bloomberg", "WSJ", "Business Times Singapore", "The Economist", "The Mint"]);

    // ── Password gate ──
    (function() {{
        if (localStorage.getItem("bf_auth") === PASSWORD) {{
            document.getElementById("lock").style.display = "none";
            loadFeeds();
        }}
    }})();

    function unlock() {{
        const val = document.getElementById("pw").value;
        if (val === PASSWORD) {{
            localStorage.setItem("bf_auth", val);
            document.getElementById("lock").style.display = "none";
            loadFeeds();
        }} else {{
            document.getElementById("pw-error").textContent = "Incorrect password.";
            document.getElementById("pw").value = "";
            document.getElementById("pw").focus();
        }}
    }}

    document.getElementById("pw").addEventListener("keydown", e => {{
        if (e.key === "Enter") unlock();
    }});

    // ── Read & dismiss tracking ──
    const feedPool = {{}};

    function getRead() {{
        try {{ return new Set(JSON.parse(localStorage.getItem("bf_read") || "[]")); }}
        catch(e) {{ return new Set(); }}
    }}

    function getDismissed() {{
        try {{ return new Set(JSON.parse(localStorage.getItem("bf_dismissed") || "[]")); }}
        catch(e) {{ return new Set(); }}
    }}

    function markDismissed(url) {{
        const dismissed = getDismissed();
        dismissed.add(url);
        localStorage.setItem("bf_dismissed", JSON.stringify([...dismissed]));
    }}

    function todaySGT() {{
        return new Date().toLocaleDateString("en-GB", {{ timeZone: "Asia/Singapore", day: "numeric", month: "short", year: "numeric" }});
    }}

    function getTodayCount() {{
        try {{
            const data = JSON.parse(localStorage.getItem("bf_read_today") || "{{}}");
            return data.date === todaySGT() ? data.count : 0;
        }} catch(e) {{ return 0; }}
    }}

    function incrementTodayCount() {{
        const today = todaySGT();
        let data;
        try {{ data = JSON.parse(localStorage.getItem("bf_read_today") || "{{}}"); }}
        catch(e) {{ data = {{}}; }}
        const count = (data.date === today ? data.count : 0) + 1;
        localStorage.setItem("bf_read_today", JSON.stringify({{ date: today, count }}));
        document.getElementById("read-count").textContent = count;
    }}

    function markRead(url) {{
        const read = getRead();
        if (!read.has(url)) {{
            incrementTodayCount();
        }}
        read.add(url);
        localStorage.setItem("bf_read", JSON.stringify([...read]));
    }}

    // ── Helpers ──
    function stripTags(str) {{
        const d = document.createElement("div");
        d.innerHTML = str || "";
        return d.textContent || d.innerText || "";
    }}

    function snippet(str) {{
        const clean = stripTags(str).replace(/\\s+/g, " ").trim();
        if (clean.length <= SUMMARY_MAX) return clean;
        return clean.slice(0, SUMMARY_MAX).replace(/\\s+\\S*$/, "") + "\\u2026";
    }}

    function isTodaySGT(dateStr) {{
        if (!dateStr) return false;
        try {{
            const opts = {{ timeZone: "Asia/Singapore", day: "numeric", month: "numeric", year: "numeric" }};
            return new Date(dateStr).toLocaleDateString("en-GB", opts) === new Date().toLocaleDateString("en-GB", opts);
        }} catch(e) {{ return false; }}
    }}

    function formatDate(str) {{
        if (!str) return "";
        try {{
            const d = new Date(str);
            if (isNaN(d.getTime())) return "";
            return d.getDate() + " " + d.toLocaleString("en", {{ month: "short" }});
        }} catch(e) {{ return ""; }}
    }}

    function escHtml(str) {{
        return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
    }}

    // ── Feed fetching ──
    async function fetchUrl(url) {{
        try {{
            const res = await fetch(PROXY + encodeURIComponent(url));
            const text = await res.text();
            const xml = new DOMParser().parseFromString(text, "text/xml");
            return Array.from(xml.querySelectorAll("item")).map(item => ({{
                title:     stripTags(item.querySelector("title")?.textContent || "Untitled"),
                link:      item.querySelector("link")?.textContent?.trim() || "",
                published: item.querySelector("pubDate")?.textContent || "",
                summary:   item.querySelector("description")?.textContent || ""
            }}));
        }} catch(e) {{
            console.warn("Failed:", url, e);
            return [];
        }}
    }}

    function renderArticle(a) {{
        const headline = a.link
            ? `<a class="headline" href="${{escHtml(a.link)}}" target="_blank" rel="noopener" data-url="${{escHtml(a.link)}}">${{escHtml(a.title)}}</a>`
            : `<span class="headline">${{escHtml(a.title)}}</span>`;
        const dismiss = a.link
            ? `<button class="dismiss" data-url="${{escHtml(a.link)}}" title="Dismiss">&#10005;</button>`
            : "";
        return `<li>
            ${{dismiss}}
            ${{headline}}
            ${{a.summary ? `<p class="summary">${{escHtml(snippet(a.summary))}}</p>` : ""}}
            ${{a.published ? `<span class="published">${{formatDate(a.published)}}</span>` : ""}}
        </li>`;
    }}

    async function loadFeed(feed) {{
        const fid     = feed.name.replace(/\\s+/g, "-");
        const section = document.querySelector("#feed-" + fid);
        const ul      = section?.querySelector("ul");
        const read      = getRead();
        const dismissed = getDismissed();

        // Fetch all URLs in parallel
        const rawFetched = await Promise.all(feed.urls.map(u => fetchUrl(u.url)));

        // Apply todayOnly before redistribution so empty-today feeds give up their quota
        const fetched = rawFetched.map(items =>
            feed.todayOnly ? items.filter(it => isTodaySGT(it.published)) : items
        );

        // Redistribute quota from URLs that returned nothing to those that did
        const quotas    = feed.urls.map(u => u.quota);
        const activeIdx = quotas.map((_, i) => i).filter(i => fetched[i].length > 0);
        const emptyIdx  = quotas.map((_, i) => i).filter(i => fetched[i].length === 0);
        const leftover  = emptyIdx.reduce((s, i) => s + quotas[i], 0);
        const effective = [...quotas];
        if (leftover > 0 && activeIdx.length > 0) {{
            const base = Math.floor(leftover / activeIdx.length);
            const rem  = leftover % activeIdx.length;
            activeIdx.forEach((i, n) => {{ effective[i] += base + (n < rem ? 1 : 0); }});
        }}

        // Collect articles and overflow pool
        const seen     = new Set();
        const articles = [];
        const pool     = [];
        fetched.forEach((items, i) => {{
            const available = items.filter(it => !it.link || (!read.has(it.link) && !dismissed.has(it.link)));
            let count = 0;
            for (const item of available) {{
                if (item.link && seen.has(item.link)) continue;
                seen.add(item.link);
                if (count < effective[i]) {{ articles.push(item); count++; }}
                else {{ pool.push(item); }}
            }}
        }});

        feedPool[feed.name] = pool;

        if (!articles.length) {{
            section?.remove();
            return;
        }}

        ul.innerHTML = articles.map(renderArticle).join("");
    }}

    function updateHeader() {{
        const sgt  = new Date(new Date().toLocaleString("en-US", {{ timeZone: "Asia/Singapore" }}));
        const date = sgt.toLocaleDateString("en-GB", {{ weekday:"long", day:"numeric", month:"long", year:"numeric" }});
        const hh   = String(sgt.getHours()).padStart(2, "0");
        const mm   = String(sgt.getMinutes()).padStart(2, "0");
        document.getElementById("timestamp").textContent  = date;
        document.getElementById("refreshed").textContent  = "Last refreshed " + hh + ":" + mm + " SGT";
        const count = getTodayCount();
        document.getElementById("read-count").textContent = count > 0 ? count : "—";
    }}

    document.addEventListener("click", e => {{
        // Read tick
        const a = e.target.closest("a.headline[data-url]");
        if (a) {{
            markRead(a.dataset.url);
            if (!a.querySelector(".read-tick")) {{
                const tick = document.createElement("span");
                tick.className = "read-tick";
                tick.innerHTML = "&#10003;";
                a.append(tick);
            }}
        }}

        // Dismiss
        const btn = e.target.closest("button.dismiss[data-url]");
        if (btn) {{
            e.preventDefault();
            const url = btn.dataset.url;
            markDismissed(url);
            const li = btn.closest("li");
            const ul = li?.closest("ul");
            const feedSection = ul?.closest("section.publication");
            const feedName = feedSection?.querySelector("h2")?.textContent;
            li?.remove();
            if (feedName && feedPool[feedName]?.length) {{
                const next = feedPool[feedName].shift();
                ul.insertAdjacentHTML("beforeend", renderArticle(next));
            }}
        }}
    }});

    async function loadFeeds() {{
        updateHeader();
        applyFilter(getFilter());
        await Promise.all(FEEDS.map(loadFeed));
    }}

    // ── All / Business filter ──
    function getFilter() {{
        return localStorage.getItem("bf_filter") || "all";
    }}

    function applyFilter(filter) {{
        document.querySelectorAll("section.publication").forEach(sec => {{
            const name = sec.querySelector("h2")?.textContent || "";
            sec.style.display = (filter === "all" || BUSINESS_FEEDS.has(name)) ? "" : "none";
        }});
        document.getElementById("btn-all").classList.toggle("active", filter === "all");
        document.getElementById("btn-business").classList.toggle("active", filter === "business");
    }}

    function setFilter(filter) {{
        localStorage.setItem("bf_filter", filter);
        applyFilter(filter);
    }}

    // Restore saved filter on load
    applyFilter(getFilter());

    // ── Section nav buttons ──
    (function() {{
        const prevBtn = document.getElementById("prev-btn");
        const nextBtn = document.getElementById("next-btn");

        function visibleSections() {{
            return Array.from(document.querySelectorAll("section.publication"))
                .filter(s => s.style.display !== "none");
        }}

        function currentIndex(sections) {{
            let idx = 0;
            for (let i = 0; i < sections.length; i++) {{
                if (sections[i].getBoundingClientRect().top + window.scrollY <= window.scrollY + 80) idx = i;
            }}
            return idx;
        }}

        function updateVisibility() {{
            const atTop    = window.scrollY < 50;
            const atBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 50;
            prevBtn.style.display = atTop    ? "none" : "flex";
            nextBtn.style.display = atBottom ? "none" : "flex";
        }}

        nextBtn.addEventListener("click", function() {{
            const sections = visibleSections();
            if (!sections.length) return;
            const next = sections[currentIndex(sections) + 1];
            if (next) next.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }});

        prevBtn.addEventListener("click", function() {{
            const sections = visibleSections();
            if (!sections.length) return;
            const prev = sections[currentIndex(sections) - 1];
            if (prev) prev.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }});

        window.addEventListener("scroll", updateVisibility, {{ passive: true }});
        updateVisibility();
    }})();
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(page)

    return output_path
