from feeds import fetch_all
from output import print_digest


def main():
    print("Fetching news feeds...")
    results = fetch_all()
    print_digest(results)


if __name__ == "__main__":
    main()
