"""
Make deliberately messy "raw exports" from the clean Brew Room data.

The clean data in ../data is the answer key. This script scrambles it the way real
exports get scrambled, so a cleaning workflow (in Alteryx or Python) has real work to do,
and so the cleaned result can be checked against the answer key exactly.

Mess added:
  pos_bills.csv         inconsistent item names, padded spaces, two date formats, currency
                        text in amounts, "3.0" quantities, duplicate bills, test bills,
                        blank lines, rows in random order
  instagram_export.csv  two junk lines above the header, padded titles, two date formats,
                        a "Total" row at the bottom
  loyalty_signups.csv   inconsistent tier spelling, Y/Yes/TRUE style flags, two date
                        formats, currency text in spend, duplicate rows
  product_lookup.csv    the mapping from every raw item name to the clean product name
  post_theme_lookup.csv the mapping from upper-cased post title to the clean post title

Run:  python3 generate_messy_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)

rng = np.random.default_rng(11)

# ------------------------------------------------------------------ helpers
ITEM_VARIANTS = {
    "Plum Cake": ["PLUM CAKE", "XMAS PLUM CAKE", "PLUMCAKE"],
    "Christmas Truffles": ["CHRISTMAS TRUFFLES", "XMAS TRUFFLES", "TRUFFLE BOX"],
    "Christmas Cupcake Tree": ["CHRISTMAS CUPCAKE TREE", "CUPCAKE TREE", "XMAS CUPCAKE TREE"],
    "Hot Chocolate Board": ["HOT CHOCOLATE BOARD", "HOT CHOC BOARD"],
    "Gifting Hampers": ["GIFTING HAMPERS", "GIFT HAMPER", "HAMPER"],
    "Regular Menu": ["REGULAR MENU", "REG MENU", "CAFE ITEMS"],
}


def messy_case(text):
    """Random casing and padding, like hand-typed or exported text."""
    style = rng.choice(["upper", "lower", "title", "as_is"])
    text = {"upper": text.upper(), "lower": text.lower(), "title": text.title(), "as_is": text}[style]
    pad_left, pad_right = " " * int(rng.choice([0, 0, 0, 1])), " " * int(rng.choice([0, 0, 1, 2]))
    return pad_left + text + pad_right


def messy_date(iso, share_iso=0.55):
    """Same date written as 2023-12-13 or 13/12/2023."""
    y, m, d = iso.split("-")
    return iso if rng.random() < share_iso else f"{d}/{m}/{y}"


def messy_amount(value):
    value = int(round(float(value)))
    kind = rng.choice(["plain", "rs", "inr", "decimal"], p=[0.4, 0.25, 0.2, 0.15])
    if kind == "plain":
        return str(value)
    if kind == "rs":
        return f"Rs {value:,}"
    if kind == "inr":
        return f"INR {value:,}.00"
    return f"{value}.00"


# ------------------------------------------------------------------ product lookup
lookup_rows = [(raw, clean) for clean, raws in ITEM_VARIANTS.items() for raw in raws]
pd.DataFrame(lookup_rows, columns=["raw_key", "product"]).to_csv(RAW / "product_lookup.csv", index=False)

# ------------------------------------------------------------------ POS bills
orders = pd.read_csv(DATA / "transactions.csv")
pos = pd.DataFrame(
    {
        "Bill No": orders["order_id"],
        "Bill Date": [messy_date(d) for d in orders["date"]],
        "Customer": [c if rng.random() > 0.1 else c.lower() + " " for c in orders["customer_id"]],
        "Item": [messy_case(str(rng.choice(ITEM_VARIANTS[p]))) for p in orders["product"]],
        "Qty": [str(q) if rng.random() > 0.08 else f"{q}.0" for q in orders["quantity"]],
        "Amount": [messy_amount(a) for a in orders["amount"]],
    }
)

duplicates = pos.sample(18, random_state=3)                      # keyed twice by mistake
tests = pd.DataFrame(                                            # staff test bills
    {
        "Bill No": [f"T{n:03d}" for n in range(1, 7)],
        "Bill Date": [messy_date(d) for d in rng.choice(orders["date"], 6)],
        "Customer": ["TEST"] * 6,
        "Item": ["TEST ORDER"] * 6,
        "Qty": ["1"] * 6,
        "Amount": ["1"] * 6,
    }
)
blanks = pd.DataFrame([[""] * 6] * 3, columns=pos.columns)       # empty lines
pos_messy = pd.concat([pos, duplicates, tests, blanks]).sample(frac=1, random_state=5).reset_index(drop=True)
pos_messy.to_csv(RAW / "pos_bills.csv", index=False)

# ------------------------------------------------------------------ Instagram export
ig = pd.read_csv(DATA / "instagram_engagement.csv")
pd.DataFrame({"raw_key": ig["post_theme"].str.upper().unique(), "post_theme": ig["post_theme"].unique()}).to_csv(
    RAW / "post_theme_lookup.csv", index=False
)
ig_out = pd.DataFrame(
    {
        "Post Date": [messy_date(d, share_iso=0.5) for d in ig["date"]],
        "Post Title ": [messy_case(t) for t in ig["post_theme"]],
        "Reach": ig["reach"].astype(str),
        "Likes": ig["likes"].astype(str),
        "Saves": ig["saves"].astype(str),
        "Comments": ig["comments"].astype(str),
        "Story Replies": ig["story_replies"].astype(str),
    }
)
total = pd.DataFrame(
    [["Total", "", ig["reach"].sum(), ig["likes"].sum(), ig["saves"].sum(), ig["comments"].sum(), ig["story_replies"].sum()]],
    columns=ig_out.columns,
)
with open(RAW / "instagram_export.csv", "w", newline="") as f:
    f.write("Brew Room - Instagram Insights Export\n")
    f.write("Exported by: manager account\n")
    pd.concat([ig_out, total]).to_csv(f, index=False)

# ------------------------------------------------------------------ loyalty sign-ups
loy = pd.read_csv(DATA / "loyalty_members.csv")
YES, NO = ["Y", "Yes", "TRUE", "yes"], ["N", "No", "FALSE", "no"]
loy_out = pd.DataFrame(
    {
        "Member ID": loy["member_id"],
        "Signup Date": [messy_date(d, share_iso=0.5) for d in loy["signup_date"]],
        "Tier": [messy_case(t) for t in loy["tier"]],
        "Visits": loy["visits_post_signup"].astype(str),
        "Total Spend": [messy_amount(v) for v in loy["total_spend_post_signup"]],
        "Redeemed?": [str(rng.choice(YES if v else NO)) for v in loy["redeemed_reward"]],
        "Referred A Friend": [str(rng.choice(YES if v else NO)) for v in loy["referred_a_friend"]],
    }
)
loy_out = pd.concat([loy_out, loy_out.sample(2, random_state=9)]).sample(frac=1, random_state=2).reset_index(drop=True)
loy_out.to_csv(RAW / "loyalty_signups.csv", index=False)

print("Wrote:", ", ".join(sorted(p.name for p in RAW.glob("*.csv"))))
print(f"pos_bills.csv: {len(pos_messy):,} lines (clean data has {len(orders):,} bills)")
