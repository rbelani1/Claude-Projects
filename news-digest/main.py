from feeds import fetch_all
from output import print_digest
from html_output import write_html


def main():
    print("Fetching news feeds...")
    results = fetch_all()
    print_digest(results)
    path = write_html(results)
    print(f"HTML digest written to: {path}")


if __name__ == "__main__":
    main()
