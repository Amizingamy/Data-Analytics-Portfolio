# Alteryx cleaning workflow (practice kit)

Three messy exports from the Brew Room's systems go in. Three clean tables come out, and they must match the answer key exactly.

> **Status:** the kit and Python answer key are built and verified. The Alteryx workflow itself (`.yxmd` and screenshots) is built by the repo owner in Alteryx Designer and added here. The step-by-step guide below has **not** been run in Alteryx by its author.

## What is in the folder

| File | What it is |
|---|---|
| `raw/pos_bills.csv` | Till export: 2,448 lines for 2,421 real bills |
| `raw/instagram_export.csv` | Instagram Insights export with junk lines above the header and a Total row |
| `raw/loyalty_signups.csv` | Loyalty sign-ups with mixed spellings and flags |
| `raw/product_lookup.csv`, `raw/post_theme_lookup.csv` | Mapping tables to join against |
| `generate_messy_data.py` | Rebuilds the raw files from the clean data (seeded) |
| `reference_cleaner.py` | The same cleaning in pandas. Proves the answer key is reachable |
| `output_reference/` | Its output, identical to `../data/` |
| `WORKFLOW_GUIDE.md` | Tool-by-tool build guide for Alteryx |

## The mess, on purpose

- **POS bills:** 6 spellings of product names (`XMAS PLUM CAKE`, `PLUMCAKE`...), padded spaces, dates as `2023-12-13` or `13/12/2023`, amounts like `Rs 1,200` and `INR 1,200.00`, quantities like `2.0`, 18 duplicate bills, 6 staff test bills, 3 blank lines.
- **Instagram:** 2 junk lines above the headers, padded and upper/lower-cased titles, two date formats, a Total row.
- **Loyalty:** `gold`/`GOLD ` tiers, `Y`/`Yes`/`TRUE` flags, currency text in spend, 2 duplicate members, two date formats.

## Checks the cleaned output must pass

| Check | Expected |
|---|---|
| Rows in clean transactions | 2,421 |
| Revenue, 13 to 25 Dec | ₹10,29,785 |
| Gifting Hampers revenue in that window | ₹4,99,998 |
| Instagram rows | 13 |
| Loyalty members | 24 |
| `Tier` values | Bronze, Silver, Gold only |

Run `python3 reference_cleaner.py` to see the Python version hit all of these.
