# Catalogue scraper

Polite scraper for [books.toscrape.com](https://books.toscrape.com), a public scraping sandbox. It checks robots.txt, sends an identifying User-Agent, waits between requests, retries with backoff, follows pagination and writes CSV + JSON.

```bash
python scraper/catalog_scraper.py --pages 3 --delay 1 --out sample_output/books
```

Fields: title, price_gbp, in_stock, rating, url, scraped_at.
