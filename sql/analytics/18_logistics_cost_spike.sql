-- ============================================================
-- Query 18: Logistics Cost Spike Analysis
-- ============================================================
-- BUSINESS QUESTION:
-- Logistics costs spiked significantly in Q4 2024.
-- Prove this with data and show the week it started.
-- This is anomaly 5 — working capital deterioration.
--
-- USED IN: Controlling Memo — Exhibit C
-- AUDIENCE: COO, Controller
-- ============================================================

WITH logistics_weekly AS (
    SELECT
        d.full_date,
        d.week_number,
        d.month_number,
        d.month_name,
        d.fiscal_year,
        o.purchase_orders_placed,
        o.purchase_orders_budget,
        o.material_consumed_kg,
        o.material_budget_kg,
        ROUND(
            o.purchase_orders_placed /
            NULLIF(o.purchase_orders_budget, 0) * 100
        , 1) AS po_volume_pct
    FROM FACT_OPERATIONAL o
    JOIN DIM_DATE d ON o.date_id = d.date_id
    WHERE o.cost_centre_id = 3  -- Logistics only
    ORDER BY d.full_date
)
SELECT
    full_date,
    week_number,
    month_name,
    fiscal_year,
    purchase_orders_placed,
    purchase_orders_budget,
    po_volume_pct,
    material_consumed_kg,
    material_budget_kg,
    ROUND(
        material_consumed_kg - material_budget_kg
    , 1) AS material_variance_kg,
    CASE
        WHEN po_volume_pct > 120
             THEN 'SPIKE — Cost Overrun Risk'
        WHEN po_volume_pct > 110
             THEN 'ELEVATED — Monitor'
        ELSE 'NORMAL'
    END AS po_status
FROM logistics_weekly
ORDER BY fiscal_year, full_date;