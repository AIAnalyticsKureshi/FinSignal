-- ============================================================
-- Query 03: Signal Detection — Operational Pace Calculation
-- ============================================================
-- BUSINESS QUESTION:
-- This is the CORE of FinSignal.
-- For each cost centre, in each week:
-- How fast are we consuming resources vs budget?
-- What will month-end look like if this pace continues?
--
-- USED IN: Power BI Page 1 — Risk Register
-- AUDIENCE: Controller, Operations Manager
-- FREQUENCY: Weekly (every Monday)
-- ============================================================

WITH weekly_pace AS (
    SELECT
        c.cost_centre_name,
        d.fiscal_year,
        d.month_number,
        d.month_name,
        d.week_number,
        d.full_date         AS week_start_date,
        o.material_consumed_kg,
        o.material_budget_kg,
        o.production_hours_actual,
        o.production_hours_budget,
        -- Material consumption pace
        ROUND(
            o.material_consumed_kg /
            NULLIF(o.material_budget_kg, 0) * 100
        , 2)                AS material_pace_pct,
        -- Hours utilisation pace
        ROUND(
            o.production_hours_actual /
            NULLIF(o.production_hours_budget, 0) * 100
        , 2)                AS hours_pace_pct,
        -- Projected month-end material consumption
        ROUND(
            o.material_consumed_kg *
            (o.material_budget_kg /
             NULLIF(o.material_consumed_kg, 0))
        , 2)                AS projected_monthly_kg
    FROM FACT_OPERATIONAL o
    JOIN DIM_DATE d ON o.date_id = d.date_id
    JOIN DIM_COST_CENTRE c ON o.cost_centre_id = c.cost_centre_id
)
SELECT
    cost_centre_name,
    fiscal_year,
    month_name,
    week_number,
    week_start_date,
    material_pace_pct,
    hours_pace_pct,
    projected_monthly_kg,
    -- Traffic light based on material pace
    CASE
        WHEN material_pace_pct > 120 THEN 'RED'
        WHEN material_pace_pct > 110 THEN 'AMBER'
        WHEN material_pace_pct < 80  THEN 'BLUE'
        ELSE 'GREEN'
    END                     AS material_signal,
    -- Traffic light based on hours pace
    CASE
        WHEN hours_pace_pct > 120   THEN 'RED'
        WHEN hours_pace_pct > 110   THEN 'AMBER'
        WHEN hours_pace_pct < 80    THEN 'BLUE'
        ELSE 'GREEN'
    END                     AS hours_signal
FROM weekly_pace
WHERE material_budget_kg > 0
   OR production_hours_budget > 0
ORDER BY fiscal_year, month_number, week_number, cost_centre_name;