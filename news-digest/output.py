import textwrap


def _wrap(text, width=100, indent="    "):
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)


def print_digest(feed_results):
    print("\n" + "=" * 60)
    print("  DAILY NEWS DIGEST")
    print("=" * 60)

    for feed in feed_results:
        source = feed["source"]
        articles = feed["articles"]

        print(f"\n--- {source} ---")

        if not articles:
            print("    No articles retrieved.")
            continue

        for i, article in enumerate(articles, start=1):
            print(f"\n  {i}. {article['title']}")
            if article["published"]:
                print(f"     {article['published']}")
            if article["link"]:
                print(f"     {article['link']}")
            if article["summary"]:
                clean = article["summary"].replace("\n", " ").strip()
                print(_wrap(clean[:300] + ("..." if len(clean) > 300 else "")))

    print("\n" + "=" * 60 + "\n")
