-- ============================================================
-- Query 02: P&L Waterfall
-- ============================================================
-- BUSINESS QUESTION:
-- What is the full Profit & Loss statement showing
-- Revenue → COGS → Gross Profit → OpEx → EBIT?
-- Both Budget and Actual side by side.
--
-- USED IN: Power BI Page 2 — P&L Variance View
-- AUDIENCE: CFO, Controller
-- FREQUENCY: Monthly
-- ============================================================

WITH pl_data AS (
    SELECT
        a.account_category,
        a.account_name,
        a.pl_order,
        a.is_revenue,
        a.is_cost,
        f.fiscal_period,
        SUM(CASE WHEN f.scenario_id = 2 THEN f.amount ELSE 0 END)
            AS budget_eur,
        SUM(CASE WHEN f.scenario_id = 1 THEN f.amount ELSE 0 END)
            AS actual_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    GROUP BY
        a.account_category,
        a.account_name,
        a.pl_order,
        a.is_revenue,
        a.is_cost,
        f.fiscal_period
)
SELECT
    pl_order,
    account_category,
    account_name,
    fiscal_period,
    ROUND(budget_eur, 2)    AS budget_eur,
    ROUND(actual_eur, 2)    AS actual_eur,
    ROUND(actual_eur - budget_eur, 2)
                            AS variance_eur,
    ROUND(
        (actual_eur - budget_eur) / NULLIF(budget_eur, 0) * 100
    , 2)                    AS variance_pct,
    -- Sign logic: Revenue is positive, Costs are negative for P&L
    CASE
        WHEN is_revenue = 1 THEN ROUND(actual_eur, 2)
        WHEN is_cost = 1    THEN ROUND(-actual_eur, 2)
        ELSE 0
    END                     AS pl_impact_eur
FROM pl_data
ORDER BY fiscal_period, pl_order;