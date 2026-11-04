-- Brew Room Christmas campaign: SQL analysis (SQLite syntax)
--
-- Tables (loaded from ../data by run_sql.py):
--   daily_sales(date, day_of_week, campaign_period, product, revenue, units_sold)
--   loyalty_members(member_id, signup_date, tier, visits_post_signup,
--                   total_spend_post_signup, redeemed_reward, referred_a_friend)
--   instagram_engagement(date, post_theme, reach, likes, saves, comments, story_replies)
--
-- Each query starts with "-- Q<number>:" and a business question.
-- All numbers come from a simulated dataset (see the README).


-- Q1: How did average daily revenue compare before and during the campaign?
-- Skills: GROUP BY, COUNT(DISTINCT), aggregate maths
SELECT
    campaign_period,
    COUNT(DISTINCT date)                                   AS days,
    SUM(revenue)                                           AS total_revenue,
    ROUND(SUM(revenue) * 1.0 / COUNT(DISTINCT date))       AS avg_daily_revenue
FROM daily_sales
GROUP BY campaign_period;


-- Q2: What was the campaign lift, as a percentage of average daily revenue?
-- Skills: CTE, self-join
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


-- Q3: Which products earned the most during the campaign, and what share of revenue is each?
-- Skills: window functions (RANK, SUM OVER)
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


-- Q4: Show total daily revenue with a 3-day moving average and a running total.
-- Skills: CTE, window frames (ROWS BETWEEN)
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


-- Q5: Which days grew or fell the most compared with the day before?
-- Skills: LAG, CTE
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


-- Q6: Do weekends earn more than weekdays during the campaign?
-- Skills: CASE WHEN, subquery
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


-- Q7: What was each product's best day during the campaign?
-- Skills: ROW_NUMBER with PARTITION BY
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


-- Q8: Did Instagram riddle posts reach and engage more people than other posts?
-- Skills: CASE WHEN, aggregation
SELECT
    CASE WHEN post_theme LIKE '%Riddle%' THEN 'Riddle post' ELSE 'Other post' END AS post_type,
    COUNT(*)                          AS posts,
    ROUND(AVG(reach))                 AS avg_reach,
    ROUND(AVG(saves), 1)              AS avg_saves,
    ROUND(AVG(story_replies), 1)      AS avg_story_replies
FROM instagram_engagement
GROUP BY post_type;


-- Q9: Did sales run higher on days when Instagram reach was above average?
-- Skills: JOIN across tables, CTE, scalar subquery
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


-- Q10: How do loyalty tiers compare on visits, spend and rewards redeemed?
-- Skills: GROUP BY, conditional aggregation
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


-- Q11: Split loyalty members into three spend bands and describe each.
-- Skills: NTILE, CTE
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


-- Q12: Do members who referred a friend spend more than those who did not?
-- Skills: GROUP BY on a flag
SELECT
    referred_a_friend,
    COUNT(*)                              AS members,
    ROUND(AVG(total_spend_post_signup))   AS avg_spend,
    ROUND(AVG(visits_post_signup), 1)     AS avg_visits
FROM loyalty_members
GROUP BY referred_a_friend;
