import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


URL_FILE = "config/urls.txt"
OUTPUT_FILE = "knowledge/articles.json"


def read_urls():
    with open(URL_FILE, "r", encoding="utf-8") as file:
        urls = []

        for line in file:
            line = line.strip()

            if line and not line.startswith("#"):
                urls.append(line)

        return urls


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_article(url):
    print(f"Fetching: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/153.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header"
    ]):
        element.decompose()

    main = (
        soup.find("article")
        or soup.find("main")
        or soup.find("body")
    )

    if not main:
        raise ValueError("Could not find article content")

    title = ""

    if soup.title:
        title = clean_text(soup.title.get_text(" "))

    heading = main.find(["h1", "h2"])

    if heading:
        title = clean_text(heading.get_text(" "))

    content = clean_text(main.get_text(" "))

    return {
        "url": url,
        "title": title,
        "content": content,
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    os.makedirs("knowledge", exist_ok=True)

    urls = read_urls()

    print(f"Found {len(urls)} URLs.")

    articles = []

    for url in urls:
        try:
            article = extract_article(url)

            articles.append(article)

            print(f"SUCCESS: {article['title']}")

        except Exception as error:
            print(f"FAILED: {url}")
            print(f"ERROR: {error}")

        time.sleep(1)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            articles,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(f"Saved {len(articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
