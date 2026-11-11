"""
Simulated order-level data for the Brew Room Christmas campaign.

daily_sales.csv only has totals per product per day. This script splits those totals
into individual purchases by customer, so that customer-level analysis (like RFM
segmentation) is possible.

The split is built to reconcile exactly: for every date and product, the purchases add
up to the same revenue and units as daily_sales.csv. Customers are simulated (a pool of
300, with some customers buying far more often than others). Customer IDs are NOT linked
to the loyalty member IDs in loyalty_members.csv.

It uses its own random seed, so it never changes the other three data files.

Run after generate_data.py:
    python3 generate_transactions.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"
rng = np.random.default_rng(7)  # separate seed: leaves the other files untouched

sales = pd.read_csv(DATA / "daily_sales.csv")

# --- Customer pool: a few frequent buyers, many occasional ones ---
N_CUSTOMERS = 300
customer_ids = [f"C{n:03d}" for n in range(1, N_CUSTOMERS + 1)]
weights = rng.lognormal(mean=0.0, sigma=1.0, size=N_CUSTOMERS)
weights = weights / weights.sum()

rows = []
for r in sales.itertuples(index=False):
    units, revenue = int(r.units_sold), int(r.revenue)
    if revenue <= 0:
        continue
    units = max(units, 1)  # a day with revenue but no whole unit still has one purchase

    # Split the units into purchases of 1-3 units each
    quantities = []
    left = units
    while left > 0:
        q = int(min(left, rng.choice([1, 2, 3], p=[0.7, 0.2, 0.1])))
        quantities.append(q)
        left -= q

    # Share revenue by quantity; the last purchase takes the rounding remainder
    amounts = [int(round(revenue * q / units)) for q in quantities]
    amounts[-1] += revenue - sum(amounts)

    buyers = rng.choice(customer_ids, size=len(quantities), p=weights)
    for q, amount, buyer in zip(quantities, amounts, buyers):
        rows.append(
            {
                "date": r.date,
                "customer_id": buyer,
                "product": r.product,
                "quantity": q,
                "amount": amount,
            }
        )

orders = pd.DataFrame(rows).sort_values(["date", "customer_id", "product"]).reset_index(drop=True)
orders.insert(0, "order_id", [f"O{n:05d}" for n in range(1, len(orders) + 1)])
orders.to_csv(DATA / "transactions.csv", index=False)

# --- Reconciliation: purchases must add back to daily_sales exactly ---
check = (
    orders.groupby(["date", "product"])[["amount", "quantity"]].sum().reset_index()
    .merge(sales[["date", "product", "revenue", "units_sold"]], on=["date", "product"], how="outer")
)
revenue_ok = (check["amount"].fillna(0) == check["revenue"].fillna(0)).all()
unit_diff = int((check["quantity"].fillna(0) - check["units_sold"].fillna(0)).abs().sum())
print(f"Purchases written: {len(orders):,} from {orders['customer_id'].nunique()} customers")
print(f"Revenue reconciles to daily_sales for every date and product: {revenue_ok}")
print(f"Total unit difference vs daily_sales: {unit_diff}")
