"""Normalise messy company/price records, de-duplicate and validate.

Usage: python clean_companies.py messy_companies.csv [--out clean.csv]
"""
import argparse
import re

import pandas as pd

SUFFIXES = {"ltd": "Ltd", "inc": "Inc", "co": "Co", "llc": "LLC"}
COUNTRIES = {"us": "US", "usa": "US", "u.s.": "US", "uk": "GB", "united kingdom": "GB"}


def clean_name(s: str) -> str:
    words = re.sub(r"[.,]", "", str(s)).strip().split()
    return " ".join(SUFFIXES.get(w.lower(), w.capitalize()) for w in words)


def clean_price(v) -> float | None:
    if pd.isna(v):
        return None
    digits = re.sub(r"[^0-9.]", "", str(v))
    return round(float(digits), 2) if digits else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="clean_companies.csv")
    a = ap.parse_args()
    df = pd.read_csv(a.src)
    df["company"] = df["company"].map(clean_name)
    df["price"] = df["price"].map(clean_price)
    df["country"] = df["country"].str.strip().str.lower().map(COUNTRIES).fillna("UNKNOWN")
    before = len(df)
    df = (df.sort_values("price", na_position="last")
            .drop_duplicates(subset=["company"], keep="first")
            .sort_values("company"))
    issues = df[df["price"].isna() | (df["country"] == "UNKNOWN")]
    df.to_csv(a.out, index=False)
    print(df.to_string(index=False))
    print(f"\n{before} rows in, {len(df)} out, {before - len(df)} duplicates removed, "
          f"{len(issues)} rows flagged for review.")


if __name__ == "__main__":
    main()
