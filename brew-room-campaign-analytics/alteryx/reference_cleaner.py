"""
Reference solution: clean the three raw exports with pandas.

This is the same logic the Alteryx workflow should apply, written in Python, so the
answer key is proven reachable. It writes to ./output_reference/.

Run:  python3 reference_cleaner.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "raw"
OUT = HERE / "output_reference"
OUT.mkdir(exist_ok=True)


def parse_date(series):
    """Two formats appear: 2023-12-13 and 13/12/2023."""
    s = series.str.strip()
    iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    uk = pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(uk).dt.strftime("%Y-%m-%d")


def parse_amount(series):
    """'Rs 1,234' / 'INR 1,234.00' / '1234.00' / '1234'  ->  1234"""
    return pd.to_numeric(series.str.replace(r"[^0-9.]", "", regex=True)).round().astype(int)


def parse_flag(series):
    return series.str.strip().str.upper().isin(["Y", "YES", "TRUE"])


# ---------------------------------------------------------------- POS bills
pos = pd.read_csv(RAW / "pos_bills.csv", dtype=str, skip_blank_lines=False).dropna(how="all")
pos = pos.rename(columns={"Bill No": "order_id", "Bill Date": "date", "Customer": "customer_id",
                          "Item": "item", "Qty": "quantity", "Amount": "amount"})
pos = pos.apply(lambda col: col.str.strip())
pos = pos[pos["order_id"].notna()]
pos = pos[pos["item"].str.upper() != "TEST ORDER"]
pos = pos.drop_duplicates(subset="order_id")

lookup = pd.read_csv(RAW / "product_lookup.csv")
pos["raw_key"] = pos["item"].str.upper()
pos = pos.merge(lookup, on="raw_key", how="left")
assert pos["product"].notna().all(), "some item names are missing from product_lookup.csv"

pos["date"] = parse_date(pos["date"])
pos["customer_id"] = pos["customer_id"].str.upper()
pos["quantity"] = pd.to_numeric(pos["quantity"]).round().astype(int)
pos["amount"] = parse_amount(pos["amount"])
clean_pos = pos[["order_id", "date", "customer_id", "product", "quantity", "amount"]]
clean_pos = clean_pos.sort_values(["date", "customer_id", "product"]).reset_index(drop=True)
clean_pos.to_csv(OUT / "clean_transactions.csv", index=False)

# ---------------------------------------------------------------- Instagram
ig = pd.read_csv(RAW / "instagram_export.csv", skiprows=2, dtype=str)
ig.columns = ["date", "post_theme", "reach", "likes", "saves", "comments", "story_replies"]
ig = ig.apply(lambda col: col.str.strip())
ig = ig[ig["date"].str.upper() != "TOTAL"]
ig["date"] = parse_date(ig["date"])
themes = pd.read_csv(RAW / "post_theme_lookup.csv").rename(columns={"post_theme": "clean_theme"})
ig["raw_key"] = ig["post_theme"].str.upper()
ig = ig.merge(themes, on="raw_key", how="left")
assert ig["clean_theme"].notna().all(), "unmapped post title"
ig["post_theme"] = ig["clean_theme"]
ig = ig.drop(columns=["raw_key", "clean_theme"])
for col in ["reach", "likes", "saves", "comments", "story_replies"]:
    ig[col] = pd.to_numeric(ig[col]).astype(int)
ig = ig.sort_values("date").reset_index(drop=True)
ig.to_csv(OUT / "clean_instagram.csv", index=False)

# ---------------------------------------------------------------- Loyalty
loy = pd.read_csv(RAW / "loyalty_signups.csv", dtype=str)
loy.columns = ["member_id", "signup_date", "tier", "visits_post_signup", "total_spend_post_signup",
               "redeemed_reward", "referred_a_friend"]
loy = loy.apply(lambda col: col.str.strip()).drop_duplicates(subset="member_id")
loy["signup_date"] = parse_date(loy["signup_date"])
loy["tier"] = loy["tier"].str.title()
loy["visits_post_signup"] = pd.to_numeric(loy["visits_post_signup"]).astype(int)
loy["total_spend_post_signup"] = parse_amount(loy["total_spend_post_signup"])
loy["redeemed_reward"] = parse_flag(loy["redeemed_reward"])
loy["referred_a_friend"] = parse_flag(loy["referred_a_friend"])
loy = loy.sort_values("member_id").reset_index(drop=True)
loy.to_csv(OUT / "clean_loyalty.csv", index=False)

print(f"clean_transactions.csv: {len(clean_pos):,} rows | clean_instagram.csv: {len(ig)} rows | clean_loyalty.csv: {len(loy)} rows")
