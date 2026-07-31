-- ============================================================
-- Query 06: Product Line Contribution Margin Analysis
-- Purpose: Calculate contribution margin and profitability
--          by product line to identify hidden loss-makers
-- FinSignal | PräzisionWerk GmbH
-- ============================================================

WITH product_revenue AS (
    SELECT
        p.product_name,
        p.product_category,
        p.margin_target_pct,
        SUM(CASE WHEN a.is_revenue = 1
            AND s.scenario_code = 'ACT'
            THEN f.amount ELSE 0 END) AS actual_revenue,
        SUM(CASE WHEN a.is_cost = 1
            AND s.scenario_code = 'ACT'
            THEN f.amount ELSE 0 END) AS actual_cost
    FROM FACT_GL_ENTRIES f
    JOIN DIM_PRODUCT_LINE p ON f.product_line_id = p.product_line_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    JOIN DIM_SCENARIO s ON f.scenario_id = s.scenario_id
    GROUP BY
        p.product_name,
        p.product_category,
        p.margin_target_pct
)
SELECT
    product_name,
    product_category,
    ROUND(actual_revenue, 2)                          AS revenue_eur,
    ROUND(actual_cost, 2)                             AS cost_eur,
    ROUND(actual_revenue - actual_cost, 2)            AS contribution_margin_eur,
    ROUND((actual_revenue - actual_cost)
        / NULLIF(actual_revenue, 0) * 100, 2)         AS margin_pct,
    ROUND(margin_target_pct, 2)                       AS target_margin_pct,
    ROUND((actual_revenue - actual_cost)
        / NULLIF(actual_revenue, 0) * 100
        - margin_target_pct, 2)                       AS margin_gap_pct,
    CASE
        WHEN (actual_revenue - actual_cost) < 0
            THEN 'LOSS MAKER'
        WHEN (actual_revenue - actual_cost)
            / NULLIF(actual_revenue, 0) * 100
            < margin_target_pct
            THEN 'BELOW TARGET'
        ELSE 'ON TARGET'
    END                                               AS margin_status
FROM product_revenue
ORDER BY contribution_margin_eur ASC;