-- ============================================================
-- Query 17: R&D Underspend Analysis
-- ============================================================
-- BUSINESS QUESTION:
-- R&D is consistently underspending its budget.
-- This signals project delays — a strategic risk.
-- How severe is the underspend and when did it start?
--
-- USED IN: Controlling Memo — Exhibit B
-- AUDIENCE: CTO, CFO
-- ============================================================

WITH rd_monthly AS (
    SELECT
        d.fiscal_year,
        d.month_number,
        d.month_name,
        f.fiscal_period,
        SUM(CASE WHEN f.scenario_id = 2
            THEN f.amount ELSE 0 END) AS budget_eur,
        SUM(CASE WHEN f.scenario_id = 1
            THEN f.amount ELSE 0 END) AS actual_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_DATE d ON f.date_id = d.date_id
    WHERE f.cost_centre_id = 4  -- R&D only
    GROUP BY d.fiscal_year, d.month_number,
             d.month_name, f.fiscal_period
)
SELECT
    fiscal_period,
    month_name,
    fiscal_year,
    ROUND(budget_eur, 2)            AS budget_eur,
    ROUND(actual_eur, 2)            AS actual_eur,
    ROUND(actual_eur - budget_eur, 2)
                                    AS variance_eur,
    ROUND(
        actual_eur / NULLIF(budget_eur, 0) * 100
    , 1)                            AS budget_utilisation_pct,
    ROUND(SUM(actual_eur - budget_eur) OVER (
        PARTITION BY fiscal_year
        ORDER BY month_number
        ROWS UNBOUNDED PRECEDING
    ), 2)                           AS ytd_cumulative_variance,
    CASE
        WHEN actual_eur / NULLIF(budget_eur, 0) < 0.70
             THEN 'CRITICAL UNDERSPEND — Project Delays Likely'
        WHEN actual_eur / NULLIF(budget_eur, 0) < 0.85
             THEN 'MODERATE UNDERSPEND — Monitor'
        ELSE 'ON TRACK'
    END                             AS underspend_status
FROM rd_monthly
ORDER BY fiscal_year, month_number;