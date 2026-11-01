"""Polite catalogue scraper for books.toscrape.com (a public scraping sandbox).

Shows the basics Crawlexa applies on every project: robots.txt check, a
identifying User-Agent, rate limiting, retries with backoff, pagination,
field extraction and CSV/JSON output.
"""
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/"
UA = "CrawlexaExampleBot/1.0 (+https://crawlexa.com)"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def allowed(url: str) -> bool:
    rp = robotparser.RobotFileParser(urljoin(BASE, "robots.txt"))
    try:
        rp.read()
    except Exception:
        return True  # no robots.txt reachable: proceed politely
    return rp.can_fetch(UA, url)


def fetch(session: requests.Session, url: str, retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)  # exponential backoff
    return ""


def parse_page(html: str, page_url: str) -> tuple[list[dict], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        a = card.select_one("h3 a")
        price = card.select_one(".price_color").get_text(strip=True)
        rows.append({
            "title": a["title"],
            "price_gbp": float(price.replace("£", "").replace("Â", "")),
            "in_stock": "In stock" in card.select_one(".availability").get_text(),
            "rating": RATING.get(card.select_one(".star-rating")["class"][1]),
            "url": urljoin(page_url, a["href"]),
            "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
    nxt = soup.select_one("li.next a")
    return rows, (urljoin(page_url, nxt["href"]) if nxt else None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=2, help="max pages to crawl")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--out", default="sample_output/books")
    args = ap.parse_args()

    if not allowed(BASE):
        raise SystemExit("robots.txt disallows crawling; stopping.")

    session = requests.Session()
    session.headers["User-Agent"] = UA
    url, records = BASE, []
    for _ in range(args.pages):
        rows, url = parse_page(fetch(session, url), url or BASE)
        records.extend(rows)
        if not url:
            break
        time.sleep(args.delay)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=records[0].keys())
        w.writeheader()
        w.writerows(records)
    out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} records to {out}.csv and {out}.json")


if __name__ == "__main__":
    main()
