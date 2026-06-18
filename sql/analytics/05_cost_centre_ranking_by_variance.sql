-- ============================================================
-- Query 06: YTD Revenue vs Budget
-- ============================================================
-- BUSINESS QUESTION:
-- How is total revenue tracking against budget
-- on a year-to-date basis?
-- Are we ahead or behind for the full year?
--
-- USED IN: Power BI Page 2 — CFO Executive View
-- AUDIENCE: CFO
-- FREQUENCY: Monthly
-- ============================================================

WITH monthly_revenue AS (
    SELECT
        d.fiscal_year,
        d.month_number,
        d.month_name,
        f.fiscal_period,
        SUM(CASE
            WHEN f.scenario_id = 2 AND a.is_revenue = 1
            THEN f.amount ELSE 0
        END) AS budget_revenue,
        SUM(CASE
            WHEN f.scenario_id = 1 AND a.is_revenue = 1
            THEN f.amount ELSE 0
        END) AS actual_revenue
    FROM FACT_GL_ENTRIES f
    JOIN DIM_DATE d ON f.date_id = d.date_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    GROUP BY d.fiscal_year, d.month_number, d.month_name, f.fiscal_period
)
SELECT
    fiscal_year,
    month_number,
    month_name,
    fiscal_period,
    ROUND(budget_revenue, 2)    AS monthly_budget_revenue,
    ROUND(actual_revenue, 2)    AS monthly_actual_revenue,
    -- YTD cumulative using window function
    ROUND(SUM(budget_revenue) OVER (
        PARTITION BY fiscal_year
        ORDER BY month_number
        ROWS UNBOUNDED PRECEDING
    ), 2)                       AS ytd_budget_revenue,
    ROUND(SUM(actual_revenue) OVER (
        PARTITION BY fiscal_year
        ORDER BY month_number
        ROWS UNBOUNDED PRECEDING
    ), 2)                       AS ytd_actual_revenue,
    -- YTD variance
    ROUND(
        SUM(actual_revenue) OVER (
            PARTITION BY fiscal_year
            ORDER BY month_number
            ROWS UNBOUNDED PRECEDING
        ) -
        SUM(budget_revenue) OVER (
            PARTITION BY fiscal_year
            ORDER BY month_number
            ROWS UNBOUNDED PRECEDING
        )
    , 2)                        AS ytd_variance_eur,
    -- Monthly variance percentage
    ROUND(
        (actual_revenue - budget_revenue) /
        NULLIF(budget_revenue, 0) * 100
    , 2)                        AS monthly_variance_pct
FROM monthly_revenue
ORDER BY fiscal_year, month_number;