# Price-change monitor

Compares two daily snapshots (columns: sku, product, price, in_stock) and reports price drops, price rises, back-in-stock, out-of-stock, new and removed products.

```bash
python price_monitor/compare_snapshots.py sample_output/snapshot_day1.csv sample_output/snapshot_day2.csv --threshold 5
```

In production Crawlexa runs this daily and sends the changes as alerts, a Google Sheet or an API feed.
