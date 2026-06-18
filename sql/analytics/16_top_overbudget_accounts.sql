-- ============================================================
-- Query 16: Top Overbudget Accounts
-- ============================================================
-- BUSINESS QUESTION:
-- Which specific accounts are driving the biggest overruns?
-- Not just which department — which exact cost category?
-- This tells the Controller exactly where to investigate.
--
-- USED IN: Power BI Page 2 — P&L Variance Drillthrough
-- AUDIENCE: Controller
-- FREQUENCY: Monthly
-- ============================================================

WITH account_variance AS (
    SELECT
        a.account_code,
        a.account_name,
        a.account_category,
        c.cost_centre_name,
        f.fiscal_period,
        SUM(CASE WHEN f.scenario_id = 2
            THEN f.amount ELSE 0 END) AS budget_eur,
        SUM(CASE WHEN f.scenario_id = 1
            THEN f.amount ELSE 0 END) AS actual_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    JOIN DIM_COST_CENTRE c ON f.cost_centre_id = c.cost_centre_id
    GROUP BY
        a.account_code, a.account_name, a.account_category,
        c.cost_centre_name, f.fiscal_period
)
SELECT
    fiscal_period,
    account_code,
    account_name,
    account_category,
    cost_centre_name,
    ROUND(budget_eur, 2)            AS budget_eur,
    ROUND(actual_eur, 2)            AS actual_eur,
    ROUND(actual_eur - budget_eur, 2)
                                    AS variance_eur,
    ROUND(
        (actual_eur - budget_eur) /
        NULLIF(budget_eur, 0) * 100
    , 2)                            AS variance_pct,
    RANK() OVER (
        PARTITION BY fiscal_period
        ORDER BY (actual_eur - budget_eur) DESC
    )                               AS overrun_rank
FROM account_variance
WHERE budget_eur > 0
AND actual_eur > budget_eur
ORDER BY fiscal_period, variance_eur DESC
LIMIT 50;