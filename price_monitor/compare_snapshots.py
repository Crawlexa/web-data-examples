"""Compare two price snapshots and report what changed.

Usage: python compare_snapshots.py day1.csv day2.csv [--threshold 5]
Both files need columns: sku, product, price, in_stock
"""
import argparse

import pandas as pd


def compare(old: pd.DataFrame, new: pd.DataFrame, threshold: float) -> dict:
    m = old.merge(new, on="sku", how="outer", suffixes=("_old", "_new"), indicator=True)
    m["product"] = m["product_new"].fillna(m["product_old"])
    both = m[m["_merge"] == "both"].copy()
    both["change_pct"] = (both["price_new"] - both["price_old"]) / both["price_old"] * 100
    return {
        "price_drops": both[both["change_pct"] <= -threshold],
        "price_rises": both[both["change_pct"] >= threshold],
        "back_in_stock": both[(~both["in_stock_old"]) & (both["in_stock_new"])],
        "out_of_stock": both[(both["in_stock_old"]) & (~both["in_stock_new"])],
        "new_products": m[m["_merge"] == "right_only"],
        "removed_products": m[m["_merge"] == "left_only"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--threshold", type=float, default=5.0, help="min % change to report")
    a = ap.parse_args()
    report = compare(pd.read_csv(a.old), pd.read_csv(a.new), a.threshold)
    for name, df in report.items():
        print(f"\n== {name.replace('_', ' ').title()} ({len(df)}) ==")
        if len(df):
            cols = [c for c in ["sku", "product", "price_old", "price_new", "change_pct"] if c in df]
            print(df[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
