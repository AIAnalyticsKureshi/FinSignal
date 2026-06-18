-- ============================================================
-- Query 01: Budget vs Actual by Cost Centre
-- ============================================================
-- BUSINESS QUESTION:
-- For each department, how much did we budget vs actually spend?
-- What is the variance in EUR and percentage?
--
-- USED IN: Power BI Page 2 — P&L Variance & Controlling View
-- AUDIENCE: Controller, CFO
-- FREQUENCY: Monthly
-- ============================================================

WITH budget_actuals AS (
    SELECT
        c.cost_centre_name,
        c.manager_name,
        f.fiscal_period,
        SUM(CASE WHEN f.scenario_id = 2 THEN f.amount ELSE 0 END)
            AS budget_eur,
        SUM(CASE WHEN f.scenario_id = 1 THEN f.amount ELSE 0 END)
            AS actual_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_COST_CENTRE c ON f.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d ON f.date_id = d.date_id
    GROUP BY
        c.cost_centre_name,
        c.manager_name,
        f.fiscal_period
)
SELECT
    cost_centre_name,
    manager_name,
    fiscal_period,
    ROUND(budget_eur, 2)        AS budget_eur,
    ROUND(actual_eur, 2)        AS actual_eur,
    ROUND(actual_eur - budget_eur, 2)
                                AS variance_eur,
    ROUND(
        (actual_eur - budget_eur) / NULLIF(budget_eur, 0) * 100
    , 2)                        AS variance_pct,
    CASE
        WHEN (actual_eur - budget_eur) / NULLIF(budget_eur, 0)
             > 0.20 THEN 'RED — Critical Overrun'
        WHEN (actual_eur - budget_eur) / NULLIF(budget_eur, 0)
             > 0.10 THEN 'AMBER — Monitor Closely'
        WHEN (actual_eur - budget_eur) / NULLIF(budget_eur, 0)
             < -0.10 THEN 'BLUE — Significant Underspend'
        ELSE 'GREEN — On Track'
    END                         AS rag_status
FROM budget_actuals
WHERE budget_eur > 0
ORDER BY fiscal_period, variance_pct DESC;