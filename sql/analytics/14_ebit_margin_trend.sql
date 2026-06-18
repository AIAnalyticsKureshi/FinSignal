-- ============================================================
-- Query 14: EBIT Margin Trend
-- ============================================================
-- BUSINESS QUESTION:
-- How is our profitability trending month over month?
-- Is the EBIT margin improving or declining?
-- Where is margin compression happening?
--
-- USED IN: Power BI Page 1 — CFO Executive Dashboard
-- AUDIENCE: CFO, Board
-- FREQUENCY: Monthly
-- ============================================================

WITH monthly_pnl AS (
    SELECT
        f.fiscal_period,
        d.fiscal_year,
        d.month_number,
        d.month_name,
        SUM(CASE
            WHEN a.is_revenue = 1 AND f.scenario_id = 1
            THEN f.amount ELSE 0
        END) AS actual_revenue,
        SUM(CASE
            WHEN a.is_cost = 1 AND f.scenario_id = 1
            THEN f.amount ELSE 0
        END) AS actual_cost,
        SUM(CASE
            WHEN a.is_revenue = 1 AND f.scenario_id = 2
            THEN f.amount ELSE 0
        END) AS budget_revenue,
        SUM(CASE
            WHEN a.is_cost = 1 AND f.scenario_id = 2
            THEN f.amount ELSE 0
        END) AS budget_cost
    FROM FACT_GL_ENTRIES f
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    JOIN DIM_DATE d ON f.date_id = d.date_id
    GROUP BY f.fiscal_period, d.fiscal_year,
             d.month_number, d.month_name
)
SELECT
    fiscal_period,
    fiscal_year,
    month_name,
    ROUND(actual_revenue, 2)        AS actual_revenue_eur,
    ROUND(actual_cost, 2)           AS actual_cost_eur,
    ROUND(actual_revenue - actual_cost, 2)
                                    AS actual_ebit_eur,
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100
    , 2)                            AS actual_ebit_margin_pct,
    ROUND(budget_revenue - budget_cost, 2)
                                    AS budget_ebit_eur,
    ROUND(
        (budget_revenue - budget_cost) /
        NULLIF(budget_revenue, 0) * 100
    , 2)                            AS budget_ebit_margin_pct,
    -- Margin variance vs budget
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100 -
        (budget_revenue - budget_cost) /
        NULLIF(budget_revenue, 0) * 100
    , 2)                            AS margin_variance_pp,
    -- Prior month comparison using LAG
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100 -
        LAG(
            (actual_revenue - actual_cost) /
            NULLIF(actual_revenue, 0) * 100
        ) OVER (ORDER BY fiscal_year, month_number)
    , 2)                            AS mom_margin_change_pp,
    CASE
        WHEN (actual_revenue - actual_cost) /
             NULLIF(actual_revenue, 0) * 100 
             (budget_revenue - budget_cost) /
             NULLIF(budget_revenue, 0) * 100 - 2
             THEN 'MARGIN COMPRESSION — Investigate'
        WHEN (actual_revenue - actual_cost) /
             NULLIF(actual_revenue, 0) * 100 >
             (budget_revenue - budget_cost) /
             NULLIF(budget_revenue, 0) * 100 + 2
             THEN 'MARGIN EXPANSION — Positive'
        ELSE 'ON TARGET'
    END                             AS margin_status
FROM monthly_pnl
ORDER BY fiscal_year, month_number;