-- ============================================================
-- Query 13: Prior Year Comparison
-- ============================================================
-- BUSINESS QUESTION:
-- How does this year's performance compare to last year?
-- Are costs growing faster than revenue?
-- Which cost centres show deterioration year over year?
--
-- USED IN: Power BI Page 2 — P&L Variance View
-- AUDIENCE: CFO, Controller
-- FREQUENCY: Monthly
-- ============================================================

WITH yearly_data AS (
    SELECT
        c.cost_centre_name,
        a.account_category,
        d.fiscal_year,
        d.month_number,
        f.fiscal_period,
        SUM(CASE WHEN f.scenario_id = 1
            THEN f.amount ELSE 0 END) AS actual_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_COST_CENTRE c ON f.cost_centre_id = c.cost_centre_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    JOIN DIM_DATE d ON f.date_id = d.date_id
    GROUP BY
        c.cost_centre_name, a.account_category,
        d.fiscal_year, d.month_number, f.fiscal_period
)
SELECT
    current_year.cost_centre_name,
    current_year.account_category,
    current_year.fiscal_period,
    ROUND(current_year.actual_eur, 2)   AS current_year_eur,
    ROUND(prior_year.actual_eur, 2)     AS prior_year_eur,
    ROUND(
        current_year.actual_eur - prior_year.actual_eur
    , 2)                                AS yoy_change_eur,
    ROUND(
        (current_year.actual_eur - prior_year.actual_eur) /
        NULLIF(prior_year.actual_eur, 0) * 100
    , 2)                                AS yoy_change_pct,
    CASE
        WHEN (current_year.actual_eur - prior_year.actual_eur) /
             NULLIF(prior_year.actual_eur, 0) > 0.15
             THEN 'DETERIORATING'
        WHEN (current_year.actual_eur - prior_year.actual_eur) /
             NULLIF(prior_year.actual_eur, 0) < -0.15
             THEN 'IMPROVING'
        ELSE 'STABLE'
    END                                 AS yoy_trend
FROM yearly_data current_year
LEFT JOIN yearly_data prior_year
    ON current_year.cost_centre_name = prior_year.cost_centre_name
    AND current_year.account_category = prior_year.account_category
    AND current_year.month_number = prior_year.month_number
    AND current_year.fiscal_year = prior_year.fiscal_year + 1
WHERE current_year.fiscal_year = 2025
AND prior_year.actual_eur IS NOT NULL
ORDER BY current_year.fiscal_period,
         yoy_change_pct DESC;