"""
Simulated dataset generator — Brew Room Christmas Campaign
----------------------------------------------------------------------
Anchors simulated daily/product data to the ONE real, disclosed figure
from Amisha's resume: ~5,00,000 in Christmas hamper revenue over the
Dec 13-25 campaign window. Everything else (daily split, other
product lines, loyalty members, Instagram engagement) is simulated to
be internally consistent with that figure and with the campaign
narrative (cupcake tree = impulse hero, hot choc board = IG-led,
plum cake/truffles = top sellers).

This is a PORTFOLIO / case-study dataset, not real business data.
Methodology is disclosed in the README that ships with it.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from datetime import date, timedelta

YEAR = 2023  # campaign year: change here if needed
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)  # fixed seed = reproducible

# ---------------------------------------------------------------
# 1. DAILY SALES BY PRODUCT CATEGORY
# ---------------------------------------------------------------
# Campaign window (real, from resume): Dec 13-25
# We also simulate a short "before" window (Dec 1-12) as a baseline
# to show campaign lift — a classic before/after comparison recruiters
# and analysts expect to see.

start = date(YEAR, 12, 1)
end = date(YEAR, 12, 25)
all_days = [start + timedelta(days=i) for i in range((end - start).days + 1)]

CAMPAIGN_START = date(YEAR, 12, 13)

products = [
    "Christmas Cupcake Tree",
    "Hot Chocolate Board",
    "Plum Cake",
    "Christmas Truffles",
    "Gifting Hampers",
    "Regular Menu",  # everyday café items, still sold throughout
]

# Baseline daily revenue (pre-campaign, "Regular Menu" only really active)
baseline_regular = 18000  # INR/day, ordinary café trading
weekend_bump = 1.35  # Fri/Sat/Sun lift, same pre and post

# Relative weight of each product once the campaign is live
# (cupcake tree = impulse hero; hampers = big ticket, used to hit 5L total)
campaign_weights = {
    "Christmas Cupcake Tree": 0.13,
    "Hot Chocolate Board": 0.09,
    "Plum Cake": 0.20,
    "Christmas Truffles": 0.17,
    "Gifting Hampers": 0.32,
    "Regular Menu": 0.09,
}

# Target: Gifting Hampers must sum to ~5,00,000 over the 13 campaign days (real figure)
TARGET_HAMPER_REVENUE = 500000
N_CAMPAIGN_DAYS = (end - CAMPAIGN_START).days + 1

rows = []
for d in all_days:
    is_campaign = d >= CAMPAIGN_START
    dow = d.strftime("%A")
    is_weekend = dow in ("Friday", "Saturday", "Sunday")
    weekend_mult = weekend_bump if is_weekend else 1.0

    # Christmas Eve/25th extra surge (real-world pattern for gifting)
    surge = 1.0
    if d == date(YEAR, 12, 24):
        surge = 1.6
    elif d == date(YEAR, 12, 25):
        surge = 1.3
    elif d == date(YEAR, 12, 23):
        surge = 1.25

    if not is_campaign:
        # Only "Regular Menu" trading pre-campaign, with small day-to-day noise
        rev = baseline_regular * weekend_mult * rng.normal(1.0, 0.08)
        rows.append({
            "date": d, "day_of_week": dow, "campaign_period": "Pre-Campaign",
            "product": "Regular Menu", "revenue": round(max(rev, 0)),
            "units_sold": int(max(rev, 0) // 220),  # rough avg ticket size
        })
        continue

    # Campaign days: total day revenue scaled by weekend + surge, then
    # split across products by weight, with daily noise per product.
    day_base_total = baseline_regular * 2.6  # campaign lifts total daily revenue
    day_total = day_base_total * weekend_mult * surge * rng.normal(1.0, 0.10)

    for prod, weight in campaign_weights.items():
        noise = rng.normal(1.0, 0.18)
        rev = max(day_total * weight * noise, 0)
        avg_ticket = {
            "Christmas Cupcake Tree": 180,
            "Hot Chocolate Board": 260,
            "Plum Cake": 450,
            "Christmas Truffles": 320,
            "Gifting Hampers": 1450,
            "Regular Menu": 230,
        }[prod]
        rows.append({
            "date": d, "day_of_week": dow, "campaign_period": "Campaign (Dec 13-25)",
            "product": prod, "revenue": round(rev),
            "units_sold": int(round(rev / avg_ticket)),
        })

daily_sales = pd.DataFrame(rows)

# --- Rescale Gifting Hampers so the campaign-period total hits exactly 5,00,000 ---
mask = (daily_sales["product"] == "Gifting Hampers") & (daily_sales["campaign_period"] == "Campaign (Dec 13-25)")
current_hamper_total = daily_sales.loc[mask, "revenue"].sum()
scale = TARGET_HAMPER_REVENUE / current_hamper_total
daily_sales.loc[mask, "revenue"] = (daily_sales.loc[mask, "revenue"] * scale).round()
daily_sales.loc[mask, "units_sold"] = (daily_sales.loc[mask, "revenue"] / 1450).round().astype(int)

daily_sales = daily_sales.sort_values(["date", "product"]).reset_index(drop=True)
daily_sales.to_csv(OUT / "daily_sales.csv", index=False)

# ---------------------------------------------------------------
# 2. LOYALTY PROGRAM MEMBERS (simulating ~20 real card signups)
# ---------------------------------------------------------------
n_members = 24
signup_dates = [CAMPAIGN_START + timedelta(days=int(x)) for x in rng.integers(0, 13, n_members)]
tiers = rng.choice(["Bronze", "Silver", "Gold"], n_members, p=[0.5, 0.35, 0.15])  # draw kept so other columns stay unchanged; tier is reassigned from spend below

loyalty = pd.DataFrame({
    "member_id": [f"BR-{1000+i}" for i in range(n_members)],
    "signup_date": signup_dates,
    "tier": tiers,
})

# Visits and spend after signup through end of Feb 2024 (loyalty is a retention play)
loyalty["visits_post_signup"] = rng.poisson(lam=5, size=n_members) + 1
loyalty["total_spend_post_signup"] = (loyalty["visits_post_signup"] * rng.normal(420, 90, n_members)).round().clip(lower=150)
# Tier follows spend: bottom half Bronze, next 35% Silver, top 15% Gold
loyalty["tier"] = pd.cut(
    loyalty["total_spend_post_signup"].rank(pct=True),
    bins=[0, 0.5, 0.85, 1.0], labels=["Bronze", "Silver", "Gold"],
).astype(str)
loyalty["redeemed_reward"] = rng.choice([True, False], n_members, p=[0.58, 0.42])
loyalty["referred_a_friend"] = rng.choice([True, False], n_members, p=[0.29, 0.71])

loyalty.to_csv(OUT / "loyalty_members.csv", index=False)

# ---------------------------------------------------------------
# 3. INSTAGRAM ENGAGEMENT (daily, campaign window)
# ---------------------------------------------------------------
ig_rows = []
post_themes = [
    "Cupcake Tree reveal", "Hot Chocolate Board", "Riddle Day 1", "Riddle Day 2",
    "Behind the scenes styling", "Plum Cake gifting", "Christmas Brunch invite",
    "Staff spotlight", "Hamper unboxing", "Riddle Day 3", "Christmas Eve countdown",
    "Christmas Day thank you", "Campaign recap",
]
for i, d in enumerate([CAMPAIGN_START + timedelta(days=x) for x in range(13)]):
    theme = post_themes[i]
    base_reach = 420
    surge = 1.0
    if "Riddle" in theme:
        surge = 1.6  # interactive content outperformed
    if d in (date(YEAR, 12, 24), date(YEAR, 12, 25)):
        surge *= 1.3
    reach = int(base_reach * surge * rng.normal(1.0, 0.15))
    likes = int(reach * rng.uniform(0.07, 0.13))
    saves = int(reach * rng.uniform(0.015, 0.04))
    comments = int(reach * rng.uniform(0.005, 0.02))
    story_replies = int(rng.uniform(5, 40)) if "Riddle" in theme else int(rng.uniform(0, 12))
    ig_rows.append({
        "date": d, "post_theme": theme, "reach": reach, "likes": likes,
        "saves": saves, "comments": comments, "story_replies": story_replies,
    })

instagram = pd.DataFrame(ig_rows)
instagram.to_csv(OUT / "instagram_engagement.csv", index=False)

# ---------------------------------------------------------------
# Summary printout for sanity-checking against the real headline figures
# ---------------------------------------------------------------
print("=== Sanity check against real disclosed figures ===")
hamper_mask = (daily_sales["product"] == "Gifting Hampers") & (daily_sales["campaign_period"] == "Campaign (Dec 13-25)")
campaign_mask = daily_sales["campaign_period"] == "Campaign (Dec 13-25)"
print(f"Hamper revenue, Dec 13-25: Rs {daily_sales.loc[hamper_mask, 'revenue'].sum():,.0f}  (target: Rs 5,00,000)")
print(f"Total campaign revenue, Dec 13-25: Rs {daily_sales.loc[campaign_mask, 'revenue'].sum():,.0f}")
print(f"Total IG reach across campaign: {instagram['reach'].sum():,} (resume says ~6,000 on static posts)")
print(f"Loyalty members simulated: {len(loyalty)} (resume mentions ~20 real cards)")
print()
print("Files written: daily_sales.csv, loyalty_members.csv, instagram_engagement.csv")
