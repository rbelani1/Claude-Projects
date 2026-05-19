import argparse
from feeds import fetch_all


def main():
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Fetch RSS feeds and output a news digest.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html", action="store_true", help="Write digest to index.html")
    group.add_argument("--cli",  action="store_true", help="Print top headlines to terminal")
    args = parser.parse_args()

    if args.html:
        from html_output import write_html
        path = write_html()
        print(f"HTML digest written to: {path}")
    else:
        print("Fetching news feeds...")
        results = fetch_all()
        from cli_output import print_headlines
        print_headlines(results)


if __name__ == "__main__":
    main()
