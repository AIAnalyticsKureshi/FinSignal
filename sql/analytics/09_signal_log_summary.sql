-- ============================================================
-- Query 09: Signal Log Summary
-- ============================================================
-- BUSINESS QUESTION:
-- How many early warning signals were detected?
-- Which cost centres triggered the most alerts?
-- What is the average advance warning time?
--
-- USED IN: Power BI Page 1 — Risk Register
-- AUDIENCE: Controller, CFO
-- FREQUENCY: Weekly
-- ============================================================

SELECT
    c.cost_centre_name,
    c.manager_name,
    s.signal_type,
    s.severity,
    COUNT(*)                        AS total_signals,
    ROUND(AVG(s.projected_overrun_eur), 2)
                                    AS avg_projected_overrun_eur,
    ROUND(SUM(s.projected_overrun_eur), 2)
                                    AS total_projected_overrun_eur,
    ROUND(AVG(s.days_saved), 1)     AS avg_days_saved,
    MAX(s.days_saved)               AS max_days_saved,
    MIN(s.days_saved)               AS min_days_saved,
    ROUND(AVG(s.days_before_monthend), 1)
                                    AS avg_days_before_monthend
FROM FACT_SIGNAL_LOG s
JOIN DIM_COST_CENTRE c ON s.cost_centre_id = c.cost_centre_id
GROUP BY
    c.cost_centre_name,
    c.manager_name,
    s.signal_type,
    s.severity
ORDER BY total_projected_overrun_eur DESC;