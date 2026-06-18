-- ============================================================
-- Query 08: Contribution Margin by Product Line
-- ============================================================
-- BUSINESS QUESTION:
-- Which product lines are actually profitable?
-- This query reveals Product Line C as a hidden loss-maker —
-- positive revenue but negative contribution margin.
--
-- USED IN: Power BI Page 3 — Cost Centre Profitability
-- AUDIENCE: CFO, Product Managers
-- FREQUENCY: Monthly
-- ============================================================

WITH product_financials AS (
    SELECT
        p.product_line_id,
        p.product_name,
        p.product_category,
        p.margin_target_pct,
        f.fiscal_period,
        SUM(CASE
            WHEN f.scenario_id = 1 AND a.is_revenue = 1
            THEN f.amount ELSE 0
        END) AS actual_revenue,
        SUM(CASE
            WHEN f.scenario_id = 1 AND a.is_cost = 1
            THEN f.amount ELSE 0
        END) AS actual_cost,
        SUM(CASE
            WHEN f.scenario_id = 2 AND a.is_revenue = 1
            THEN f.amount ELSE 0
        END) AS budget_revenue
    FROM FACT_GL_ENTRIES f
    JOIN DIM_PRODUCT_LINE p ON f.product_line_id = p.product_line_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    GROUP BY
        p.product_line_id, p.product_name,
        p.product_category, p.margin_target_pct, f.fiscal_period
)
SELECT
    product_name,
    product_category,
    fiscal_period,
    ROUND(actual_revenue, 2)    AS actual_revenue_eur,
    ROUND(actual_cost, 2)       AS actual_cost_eur,
    -- Contribution margin = Revenue - Cost
    ROUND(actual_revenue - actual_cost, 2)
                                AS contribution_margin_eur,
    -- Contribution margin percentage
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100
    , 2)                        AS contribution_margin_pct,
    -- Target margin from dimension table
    margin_target_pct           AS target_margin_pct,
    -- Gap vs target
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100
        - margin_target_pct
    , 2)                        AS margin_gap_vs_target_pct,
    -- Flag hidden loss makers
    CASE
        WHEN (actual_revenue - actual_cost) < 0
             THEN 'LOSS MAKER — Immediate Review Required'
        WHEN (actual_revenue - actual_cost) /
             NULLIF(actual_revenue, 0) * 100
             < margin_target_pct * 0.8
             THEN 'BELOW TARGET — Monitor'
        ELSE 'ON TARGET'
    END                         AS margin_status
FROM product_financials
WHERE actual_revenue > 0
ORDER BY fiscal_period, contribution_margin_pct ASC;