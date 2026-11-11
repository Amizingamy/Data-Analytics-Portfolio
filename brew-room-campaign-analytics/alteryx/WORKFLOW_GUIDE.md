# Build guide: cleaning the Brew Room exports in Alteryx Designer

**Honest note:** this guide was written without Alteryx access and has not been run in it. Tool names are standard Designer tools; if a setting differs in your version, trust the tool's own help. The Python file `reference_cleaner.py` is the tested answer key.

Build **three small workflows** (or three lanes in one canvas). Run each, then compare with `../data/`.

## Lane 1: POS bills → clean transactions

1. **Input Data** → `raw/pos_bills.csv`. Set all fields to `V_String` so nothing is guessed wrongly.
2. **Select** → rename `Bill No`→`order_id`, `Bill Date`→`date`, `Customer`→`customer_id`, `Item`→`item`, `Qty`→`quantity`, `Amount`→`amount`.
3. **Data Cleansing** → tick all string fields; *Remove Null Rows*, *Trim leading and trailing whitespace*. (Blank lines drop out here.)
4. **Filter** → `[item] != "TEST ORDER"` (keep the True output). Check the False output holds 6 rows.
5. **Unique** → on `order_id`. Duplicates go to the D output (expect 18).
6. **Formula** → `item_key = Uppercase([item])`, `customer_id = Uppercase([customer_id])`.
7. **Join** → `item_key` to `raw_key` from a second **Input Data** (`raw/product_lookup.csv`). Use the J output. Attach a **Browse** to the L output: it must be empty. If not, a name is missing from the lookup.
8. **Formula for dates** → `date = IF REGEX_Match([date], "\d{4}-\d{2}-\d{2}") THEN [date] ELSE DateTimeFormat(DateTimeParse([date], "%d/%m/%Y"), "%Y-%m-%d") ENDIF`. (Or use **DateTime** tool twice and combine.)
9. **Formula for numbers** → `amount = ToNumber(REGEX_Replace([amount], "[^0-9.]", ""))`, `quantity = ToNumber([quantity])`. Then **Select** to set `amount` and `quantity` to Int32 (rounds `2.0` to `2`).
10. **Select** → keep `order_id, date, customer_id, product, quantity, amount`. **Sort** by date, customer_id, product. **Output Data** → `clean_transactions.csv`.

**Checkpoint:** 2,421 rows. A **Summarize** (Sum of `amount`, group by `product`) on 13 to 25 Dec shows Gifting Hampers = 499,998 and the total = 1,029,785.

## Lane 2: Instagram export → clean engagement

1. **Input Data** → `raw/instagram_export.csv`. In the options set *Start Data Import on Line* = **3** (skips the two junk lines), all `V_String`.
2. **Select** → rename to `date, post_theme, reach, likes, saves, comments, story_replies`.
3. **Data Cleansing** → trim whitespace.
4. **Filter** → `Uppercase([date]) != "TOTAL"`.
5. **Formula** → same date rule as Lane 1. `post_theme_key = Uppercase([post_theme])`.
6. **Join** → to `raw/post_theme_lookup.csv` on `post_theme_key = raw_key`; take `post_theme` from the lookup (deselect the raw one in the Join's Select).
7. **Select** → set the five metrics to Int32. **Sort** by date. **Output Data** → `clean_instagram.csv`.

**Checkpoint:** 13 rows.

## Lane 3: Loyalty sign-ups → clean members

1. **Input Data** → `raw/loyalty_signups.csv`, all `V_String`.
2. **Select** → rename to `member_id, signup_date, tier, visits_post_signup, total_spend_post_signup, redeemed_reward, referred_a_friend`.
3. **Data Cleansing** → trim; **Unique** on `member_id` (expect 2 duplicates).
4. **Formula** → `tier = TitleCase(Trim([tier]))`; date rule as before; `total_spend_post_signup = ToNumber(REGEX_Replace([total_spend_post_signup], "[^0-9.]", ""))`; flags: `redeemed_reward = Uppercase([redeemed_reward]) IN ("Y","YES","TRUE")` (same for `referred_a_friend`).
5. **Select** → types: spend and visits Int32, flags Bool. **Sort** by `member_id`. **Output Data** → `clean_loyalty.csv`.

**Checkpoint:** 24 rows, tiers only Bronze, Silver, Gold.

## Proving it matches

Add a **Join** between your output and the matching file in `../data/` on the key, or run a **Summarize** to compare totals. Then screenshot each lane for the portfolio.

## What to put in the repo once done

- `brew_room_cleaning.yxmd` (File → Save As)
- `screenshots/` of each lane (canvas zoomed so the tool labels are readable)
- Add the "Checks" table with your actual numbers.

Replace the 'Status' note in `README.md` with the date you ran it.
