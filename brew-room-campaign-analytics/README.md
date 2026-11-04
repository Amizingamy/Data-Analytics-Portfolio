# Brew Room Christmas Campaign: Analytics

I ran the Christmas campaign at The Brew Room, a café in Mylapore, Chennai. This project turns that campaign into an analytics case study: how much revenue it added, which products drove it, whether Instagram helped, and how loyalty-card members behaved.

## About the data (please read)

The real sales data belongs to the business and is confidential, so it is not here. The data in this project is **simulated**.

I built it around the few real figures I am free to share:

- About ₹5,00,000 in revenue from Christmas hampers during the campaign (Dec 13-25). The daily split is simulated, but the hamper total is scaled to match this number.
- About 6,000 organic Instagram reach across the campaign posts.
- About 20 real loyalty-card sign-ups. The data has 24 simulated members.
- What I know about the campaign itself: the cupcake tree was an impulse-buy product, the hot chocolate board was made for Instagram, plum cake and truffles were top sellers, and the Instagram riddles got people talking.

Everything else (daily revenue, product splits, member behaviour) is made up to fit those facts. Treat the findings as a demonstration of method, not as the real results of the business.

## What is in this folder

| Path | What it is |
|---|---|
| `data/daily_sales.csv` | Revenue and units per product per day, Dec 1-25 (Dec 1-12 is the baseline before the campaign) |
| `data/loyalty_members.csv` | 24 simulated loyalty members: tier, visits, spend, rewards redeemed, referrals |
| `data/instagram_engagement.csv` | Daily Instagram reach, likes, saves, comments and story replies for the campaign |
| `sql/queries.sql` | 12 SQL queries, each answering a business question |
| `sql/run_sql.py` | Loads the CSVs into SQLite and runs the queries |
| `generate_data.py` | The script that creates the data (fixed seed, so it gives the same files every time) |

## The SQL queries

The queries cover:

- Campaign lift, before vs during (CTEs, self-join)
- Product ranking and revenue share (RANK, window SUM)
- Daily revenue with a 3-day moving average and running total (window frames)
- Biggest day-to-day swings (LAG)
- Weekend vs weekday revenue (CASE WHEN)
- Each product's best day (ROW_NUMBER with PARTITION BY)
- Whether Instagram riddle posts did better, and whether high-reach days had higher sales (joins across tables)
- Loyalty tiers, spend bands and the effect of referrals (NTILE, conditional aggregation)

To run them:

```
pip install pandas
cd sql
python3 run_sql.py          # all queries
python3 run_sql.py 3        # just Q3
python3 run_sql.py --save-db   # also saves brew_room.db to open in DB Browser for SQLite
```

## What the simulated data shows

- Average daily revenue rose from about ₹20,900 before the campaign to about ₹79,200 during it, a lift of roughly 280%.
- Gifting Hampers were about half of campaign revenue. Plum Cake and Christmas Truffles came next.
- Weekends earned about 50% more per day than weekdays during the campaign.
- Riddle posts reached about 58% more people than other posts and got far more story replies.
- Loyalty members who referred a friend spent more and visited more often than those who did not.

## Coming next

A Tableau dashboard on this data, and an Alteryx workflow that cleans messy raw exports before the SQL step.
