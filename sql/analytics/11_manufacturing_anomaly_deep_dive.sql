-- ============================================================
-- Query 11: Manufacturing Anomaly Deep Dive
-- ============================================================
-- BUSINESS QUESTION:
-- Deep dive into Manufacturing cost centre.
-- Prove the Q1 2025 raw material overrun with data.
-- Week by week progression of the anomaly.
--
-- USED IN: Controlling Memo — Exhibit A
-- AUDIENCE: COO, Controller
-- ============================================================

WITH mfg_weekly AS (
    SELECT
        d.full_date,
        d.week_number,
        d.month_number,
        d.month_name,
        d.fiscal_year,
        o.material_consumed_kg,
        o.material_budget_kg,
        ROUND(
            o.material_consumed_kg /
            NULLIF(o.material_budget_kg, 0) * 100
        , 2) AS consumption_pct,
        ROUND(
            o.material_consumed_kg - o.material_budget_kg
        , 2) AS material_variance_kg
    FROM FACT_OPERATIONAL o
    JOIN DIM_DATE d ON o.date_id = d.date_id
    WHERE o.cost_centre_id = 1  -- Manufacturing only
    ORDER BY d.full_date
)
SELECT
    full_date,
    week_number,
    month_name,
    fiscal_year,
    material_consumed_kg,
    material_budget_kg,
    consumption_pct,
    material_variance_kg,
    -- Cumulative variance to show build-up over time
    ROUND(SUM(material_variance_kg) OVER (
        PARTITION BY fiscal_year, month_number
        ORDER BY full_date
        ROWS UNBOUNDED PRECEDING
    ), 2) AS cumulative_variance_kg,
    CASE
        WHEN consumption_pct > 120 THEN 'RED — Critical'
        WHEN consumption_pct > 110 THEN 'AMBER — Warning'
        ELSE 'GREEN — Normal'
    END AS weekly_status
FROM mfg_weekly
ORDER BY fiscal_year, full_date;