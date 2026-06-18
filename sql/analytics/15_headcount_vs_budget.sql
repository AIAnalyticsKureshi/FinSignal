-- ============================================================
-- Query 15: Headcount vs Budget Analysis
-- ============================================================
-- BUSINESS QUESTION:
-- Is each department operating with the right number of people?
-- Are we over or under staffed vs plan?
-- How does headcount relate to cost performance?
--
-- USED IN: Power BI Page 3 — Cost Centre Profitability
-- AUDIENCE: COO, HR, Controller
-- FREQUENCY: Monthly
-- ============================================================

WITH weekly_headcount AS (
    SELECT
        c.cost_centre_name,
        c.manager_name,
        d.fiscal_year,
        d.month_number,
        d.month_name,
        AVG(o.headcount_active)     AS avg_actual_headcount,
        AVG(o.headcount_budget)     AS avg_budget_headcount,
        AVG(o.production_hours_actual)
                                    AS avg_weekly_hours_actual,
        AVG(o.production_hours_budget)
                                    AS avg_weekly_hours_budget
    FROM FACT_OPERATIONAL o
    JOIN DIM_COST_CENTRE c ON o.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d ON o.date_id = d.date_id
    GROUP BY
        c.cost_centre_name, c.manager_name,
        d.fiscal_year, d.month_number, d.month_name
)
SELECT
    cost_centre_name,
    manager_name,
    fiscal_year,
    month_name,
    ROUND(avg_actual_headcount, 0)  AS actual_headcount,
    ROUND(avg_budget_headcount, 0)  AS budget_headcount,
    ROUND(
        avg_actual_headcount - avg_budget_headcount
    , 0)                            AS headcount_variance,
    ROUND(
        avg_actual_headcount /
        NULLIF(avg_budget_headcount, 0) * 100
    , 1)                            AS headcount_utilisation_pct,
    ROUND(avg_weekly_hours_actual, 0)
                                    AS avg_weekly_hours,
    ROUND(
        avg_weekly_hours_actual /
        NULLIF(avg_actual_headcount, 0)
    , 1)                            AS hours_per_person,
    CASE
        WHEN avg_actual_headcount >
             avg_budget_headcount * 1.10
             THEN 'OVERSTAFFED'
        WHEN avg_actual_headcount 
             avg_budget_headcount * 0.90
             THEN 'UNDERSTAFFED'
        ELSE 'ON PLAN'
    END                             AS staffing_status
FROM weekly_headcount
ORDER BY fiscal_year, month_number, cost_centre_name;