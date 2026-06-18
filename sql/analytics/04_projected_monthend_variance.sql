-- ============================================================
-- Query 04: Projected Month-End Variance
-- ============================================================
-- BUSINESS QUESTION:
-- Based on current week operational pace, what will the
-- financial variance be at month-end if nothing changes?
-- This is the PREDICTION engine of FinSignal.
--
-- USED IN: Power BI Page 1 — Risk Register
-- AUDIENCE: Controller, CFO
-- FREQUENCY: Weekly
-- ============================================================

WITH weekly_pace AS (
    SELECT
        o.cost_centre_id,
        c.cost_centre_name,
        d.fiscal_year,
        d.month_number,
        d.month_name,
        d.week_number,
        -- Material pace ratio
        ROUND(
            o.material_consumed_kg /
            NULLIF(o.material_budget_kg, 0)
        , 4) AS material_pace_ratio,
        -- Hours pace ratio
        ROUND(
            o.production_hours_actual /
            NULLIF(o.production_hours_budget, 0)
        , 4) AS hours_pace_ratio
    FROM FACT_OPERATIONAL o
    JOIN DIM_DATE d ON o.date_id = d.date_id
    JOIN DIM_COST_CENTRE c ON o.cost_centre_id = c.cost_centre_id
),
monthly_budget AS (
    SELECT
        cost_centre_id,
        fiscal_period,
        SUM(amount) AS total_budget_eur
    FROM FACT_GL_ENTRIES
    WHERE scenario_id = 2
    GROUP BY cost_centre_id, fiscal_period
)
SELECT
    p.cost_centre_name,
    p.fiscal_year,
    p.month_name,
    p.week_number,
    p.material_pace_ratio,
    b.total_budget_eur,
    -- Projected actual = budget * pace ratio
    ROUND(b.total_budget_eur * p.material_pace_ratio, 2)
        AS projected_actual_eur,
    -- Projected variance = projected - budget
    ROUND(
        (b.total_budget_eur * p.material_pace_ratio)
        - b.total_budget_eur
    , 2) AS projected_variance_eur,
    -- Projected variance percentage
    ROUND(
        (p.material_pace_ratio - 1) * 100
    , 2) AS projected_variance_pct,
    -- RAG status based on projection
    CASE
        WHEN p.material_pace_ratio > 1.20 THEN 'RED'
        WHEN p.material_pace_ratio > 1.10 THEN 'AMBER'
        WHEN p.material_pace_ratio < 0.80 THEN 'BLUE'
        ELSE 'GREEN'
    END AS projected_rag_status
FROM weekly_pace p
JOIN monthly_budget b
    ON p.cost_centre_id = b.cost_centre_id
    AND b.fiscal_period = p.fiscal_year || '-'
        || printf('%02d', p.month_number)
WHERE p.material_pace_ratio > 0
ORDER BY p.fiscal_year, p.month_number, p.week_number,
         p.material_pace_ratio DESC;