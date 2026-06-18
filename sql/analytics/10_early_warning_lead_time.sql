-- ============================================================
-- Query 10: Early Warning Lead Time Analysis
-- ============================================================
-- BUSINESS QUESTION:
-- This is the HEADLINE metric of FinSignal.
-- How many days earlier does FinSignal detect problems
-- compared to the traditional monthly Controlling report?
-- What is the financial value of this advance warning?
--
-- USED IN: Power BI Page 1 — Risk Register
-- README headline metric
-- CV bullet point
-- AUDIENCE: CFO, Recruiter reading your GitHub
-- ============================================================

WITH signal_summary AS (
    SELECT
        s.signal_id,
        c.cost_centre_name,
        s.signal_type,
        s.severity,
        d1.full_date        AS detected_date,
        d2.full_date        AS traditional_report_date,
        s.projected_overrun_eur,
        s.days_saved,
        s.days_before_monthend
    FROM FACT_SIGNAL_LOG s
    JOIN DIM_COST_CENTRE c ON s.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d1 ON s.detected_date_id = d1.date_id
    JOIN DIM_DATE d2 ON s.traditional_report_date_id = d2.date_id
)
SELECT
    -- Overall FinSignal performance metrics
    COUNT(*)                        AS total_signals_detected,
    COUNT(CASE WHEN severity = 'RED'
               THEN 1 END)          AS red_signals,
    COUNT(CASE WHEN severity = 'AMBER'
               THEN 1 END)          AS amber_signals,
    ROUND(AVG(days_saved), 1)       AS avg_days_saved,
    MAX(days_saved)                 AS max_days_saved,
    MIN(days_saved)                 AS min_days_saved,
    ROUND(SUM(projected_overrun_eur), 2)
                                    AS total_projected_overrun_eur,
    ROUND(AVG(projected_overrun_eur), 2)
                                    AS avg_projected_overrun_eur,
    -- Key headline: % of overrun that could be prevented
    -- with 3+ weeks advance warning
    ROUND(
        COUNT(CASE WHEN days_saved >= 21 THEN 1 END) * 100.0 /
        NULLIF(COUNT(*), 0)
    , 1)                            AS pct_signals_3weeks_early
FROM signal_summary;