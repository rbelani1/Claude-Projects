from feeds import fetch_all
from cli_output import print_headlines
from html_output import write_html


def main():
    print("Fetching news feeds...")
    results = fetch_all()
    print_headlines(results)
    path = write_html(results)
    print(f"HTML digest written to: {path}")


if __name__ == "__main__":
    main()
