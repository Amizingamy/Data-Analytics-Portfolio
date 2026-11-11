# SQL results

Output of every query in `queries.sql`, run on the simulated Brew Room data (SQLite). Regenerate with `python3 make_results.py`.

## Q1: How did average daily revenue compare before and during the campaign?

```sql
SELECT
    campaign_period,
    COUNT(DISTINCT date)                                   AS days,
    SUM(revenue)                                           AS total_revenue,
    ROUND(SUM(revenue) * 1.0 / COUNT(DISTINCT date))       AS avg_daily_revenue
FROM daily_sales
GROUP BY campaign_period;
```

```
     campaign_period  days  total_revenue  avg_daily_revenue
Campaign (Dec 13-25)    13        1029785            79214.0
        Pre-Campaign    12         250763            20897.0
```

## Q2: What was the campaign lift, as a percentage of average daily revenue?

```sql
WITH period_avg AS (
    SELECT
        campaign_period,
        SUM(revenue) * 1.0 / COUNT(DISTINCT date) AS avg_daily
    FROM daily_sales
    GROUP BY campaign_period
)
SELECT
    ROUND(b.avg_daily)                                         AS before_avg_daily,
    ROUND(c.avg_daily)                                         AS during_avg_daily,
    ROUND((c.avg_daily - b.avg_daily) / b.avg_daily * 100, 1)  AS lift_pct
FROM period_avg AS b
JOIN period_avg AS c
  ON b.campaign_period = 'Pre-Campaign'
 AND c.campaign_period LIKE 'Campaign%';
```

```
 before_avg_daily  during_avg_daily  lift_pct
          20897.0           79214.0     279.1
```

## Q3: Which products earned the most during the campaign, and what share of revenue is each?

```sql
SELECT
    RANK() OVER (ORDER BY SUM(revenue) DESC)                      AS revenue_rank,
    product,
    SUM(revenue)                                                  AS revenue,
    SUM(units_sold)                                               AS units,
    ROUND(SUM(revenue) * 100.0 / SUM(SUM(revenue)) OVER (), 1)    AS pct_of_campaign_revenue
FROM daily_sales
WHERE campaign_period LIKE 'Campaign%'
GROUP BY product
ORDER BY revenue_rank;
```

```
 revenue_rank                product  revenue  units  pct_of_campaign_revenue
            1        Gifting Hampers   499998    345                     48.6
            2              Plum Cake   158798    352                     15.4
            3     Christmas Truffles   132266    413                     12.8
            4 Christmas Cupcake Tree   103373    575                     10.0
            5    Hot Chocolate Board    68624    266                      6.7
            6           Regular Menu    66726    289                      6.5
```

## Q4: Show total daily revenue with a 3-day moving average and a running total.

```sql
WITH daily AS (
    SELECT date, SUM(revenue) AS revenue
    FROM daily_sales
    GROUP BY date
)
SELECT
    date,
    revenue,
    ROUND(AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS moving_avg_3d,
    SUM(revenue) OVER (ORDER BY date)                                                 AS running_total
FROM daily
ORDER BY date;
```

```
      date  revenue  moving_avg_3d  running_total
2023-12-01    24892        24892.0          24892
2023-12-02    22278        23585.0          47170
2023-12-03    25759        24310.0          72929
2023-12-04    19354        22464.0          92283
2023-12-05    15191        20101.0         107474
2023-12-06    16125        16890.0         123599
2023-12-07    18184        16500.0         141783
2023-12-08    23685        19331.0         165468
2023-12-09    24267        22045.0         189735
2023-12-10    22642        23531.0         212377
2023-12-11    19266        22058.0         231643
2023-12-12    19120        20343.0         250763
2023-12-13    59820        32735.0         310583
2023-12-14    61666        46869.0         372249
2023-12-15    92943        71476.0         465192
2023-12-16    73774        76128.0         538966
2023-12-17    95911        87543.0         634877
2023-12-18    58466        76050.0         693343
2023-12-19    64991        73123.0         758334
2023-12-20    62037        61831.0         820371
2023-12-21    67448        64825.0         887819
2023-12-22    95171        74885.0         982990
2023-12-23   102176        88265.0        1085166
2023-12-24   118822       105390.0        1203988
2023-12-25    76560        99186.0        1280548
```

## Q5: Which days grew or fell the most compared with the day before?

```sql
WITH daily AS (
    SELECT date, SUM(revenue) AS revenue
    FROM daily_sales
    GROUP BY date
),
changes AS (
    SELECT
        date,
        revenue,
        LAG(revenue) OVER (ORDER BY date) AS prev_revenue
    FROM daily
)
SELECT
    date,
    revenue,
    prev_revenue,
    revenue - prev_revenue                                        AS change_rs,
    ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)     AS change_pct
FROM changes
WHERE prev_revenue IS NOT NULL
ORDER BY ABS(revenue - prev_revenue) DESC
LIMIT 5;
```

```
      date  revenue  prev_revenue  change_rs  change_pct
2023-12-25    76560        118822     -42262       -35.6
2023-12-13    59820         19120      40700       212.9
2023-12-18    58466         95911     -37445       -39.0
2023-12-15    92943         61666      31277        50.7
2023-12-22    95171         67448      27723        41.1
```

## Q6: Do weekends earn more than weekdays during the campaign?

```sql
SELECT
    day_type,
    COUNT(*)                         AS days,
    ROUND(AVG(day_revenue))          AS avg_daily_revenue
FROM (
    SELECT
        date,
        CASE WHEN day_of_week IN ('Friday', 'Saturday', 'Sunday')
             THEN 'Weekend' ELSE 'Weekday' END AS day_type,
        SUM(revenue)                           AS day_revenue
    FROM daily_sales
    WHERE campaign_period LIKE 'Campaign%'
    GROUP BY date, day_of_week
)
GROUP BY day_type;
```

```
day_type  days  avg_daily_revenue
 Weekday     7            64427.0
 Weekend     6            96466.0
```

## Q7: What was each product's best day during the campaign?

```sql
WITH ranked AS (
    SELECT
        product,
        date,
        revenue,
        ROW_NUMBER() OVER (PARTITION BY product ORDER BY revenue DESC) AS rn
    FROM daily_sales
    WHERE campaign_period LIKE 'Campaign%'
)
SELECT product, date AS best_day, revenue
FROM ranked
WHERE rn = 1
ORDER BY revenue DESC;
```

```
               product   best_day  revenue
       Gifting Hampers 2023-12-23    51744
             Plum Cake 2023-12-24    19511
    Christmas Truffles 2023-12-24    17695
Christmas Cupcake Tree 2023-12-24    15372
   Hot Chocolate Board 2023-12-24     9336
          Regular Menu 2023-12-23     7442
```

## Q8: Did Instagram riddle posts reach and engage more people than other posts?

```sql
SELECT
    CASE WHEN post_theme LIKE '%Riddle%' THEN 'Riddle post' ELSE 'Other post' END AS post_type,
    COUNT(*)                          AS posts,
    ROUND(AVG(reach))                 AS avg_reach,
    ROUND(AVG(saves), 1)              AS avg_saves,
    ROUND(AVG(story_replies), 1)      AS avg_story_replies
FROM instagram_engagement
GROUP BY post_type;
```

```
  post_type  posts  avg_reach  avg_saves  avg_story_replies
 Other post     10      429.0        9.9                6.4
Riddle post      3      679.0       13.7               25.3
```

## Q9: Did sales run higher on days when Instagram reach was above average?

```sql
WITH daily_rev AS (
    SELECT date, SUM(revenue) AS revenue
    FROM daily_sales
    GROUP BY date
),
joined AS (
    SELECT
        i.date,
        i.reach,
        d.revenue,
        CASE WHEN i.reach > (SELECT AVG(reach) FROM instagram_engagement)
             THEN 'Above-average reach' ELSE 'Below-average reach' END AS reach_group
    FROM instagram_engagement AS i
    JOIN daily_rev AS d ON d.date = i.date
)
SELECT
    reach_group,
    COUNT(*)                  AS days,
    ROUND(AVG(revenue))       AS avg_daily_revenue
FROM joined
GROUP BY reach_group;
```

```
        reach_group  days  avg_daily_revenue
Above-average reach     5            91454.0
Below-average reach     8            71564.0
```

## Q10: How do loyalty tiers compare on visits, spend and rewards redeemed?

```sql
SELECT
    tier,
    COUNT(*)                                                      AS members,
    ROUND(AVG(visits_post_signup), 1)                             AS avg_visits,
    ROUND(AVG(total_spend_post_signup))                           AS avg_spend,
    ROUND(SUM(redeemed_reward) * 100.0 / COUNT(*), 0)
                                                                  AS pct_redeemed
FROM loyalty_members
GROUP BY tier
ORDER BY avg_spend DESC;
```

```
  tier  members  avg_visits  avg_spend  pct_redeemed
  Gold        4         9.3     4299.0          50.0
Silver        8         6.4     2864.0          88.0
Bronze       12         4.3     1691.0          58.0
```

## Q11: Split loyalty members into three spend bands and describe each.

```sql
WITH banded AS (
    SELECT
        member_id,
        total_spend_post_signup AS spend,
        visits_post_signup      AS visits,
        NTILE(3) OVER (ORDER BY total_spend_post_signup DESC) AS band
    FROM loyalty_members
)
SELECT
    CASE band WHEN 1 THEN 'Top third' WHEN 2 THEN 'Middle third' ELSE 'Bottom third' END AS spend_band,
    COUNT(*)                 AS members,
    ROUND(AVG(spend))        AS avg_spend,
    ROUND(AVG(visits), 1)    AS avg_visits
FROM banded
GROUP BY band
ORDER BY band;
```

```
  spend_band  members  avg_spend  avg_visits
   Top third        8     3736.0         7.9
Middle third        8     2355.0         5.4
Bottom third        8     1460.0         4.3
```

## Q12: Do members who referred a friend spend more than those who did not?

```sql
SELECT
    referred_a_friend,
    COUNT(*)                              AS members,
    ROUND(AVG(total_spend_post_signup))   AS avg_spend,
    ROUND(AVG(visits_post_signup), 1)     AS avg_visits
FROM loyalty_members
GROUP BY referred_a_friend;
```

```
 referred_a_friend  members  avg_spend  avg_visits
                 0       17     2109.0         5.1
                 1        7     3507.0         7.7
```
