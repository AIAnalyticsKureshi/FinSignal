-- ============================================================
-- Query 12: CFO Executive Summary
-- ============================================================
-- BUSINESS QUESTION:
-- Single page view for the CFO.
-- Key financial metrics for the most recent period.
-- Revenue, costs, EBIT, variance, and risk flags.
--
-- USED IN: Power BI Page 1 — CFO Dashboard
-- AUDIENCE: CFO, Board
-- FREQUENCY: Monthly
-- ============================================================

WITH latest_period AS (
    SELECT MAX(fiscal_period) AS max_period
    FROM FACT_GL_ENTRIES
    WHERE scenario_id = 1
),
period_summary AS (
    SELECT
        f.fiscal_period,
        SUM(CASE
            WHEN a.is_revenue = 1 AND f.scenario_id = 1
            THEN f.amount ELSE 0
        END) AS actual_revenue,
        SUM(CASE
            WHEN a.is_revenue = 1 AND f.scenario_id = 2
            THEN f.amount ELSE 0
        END) AS budget_revenue,
        SUM(CASE
            WHEN a.is_cost = 1 AND f.scenario_id = 1
            THEN f.amount ELSE 0
        END) AS actual_cost,
        SUM(CASE
            WHEN a.is_cost = 1 AND f.scenario_id = 2
            THEN f.amount ELSE 0
        END) AS budget_cost
    FROM FACT_GL_ENTRIES f
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    WHERE f.fiscal_period = (SELECT max_period FROM latest_period)
    GROUP BY f.fiscal_period
)
SELECT
    fiscal_period                   AS reporting_period,
    ROUND(actual_revenue, 2)        AS actual_revenue_eur,
    ROUND(budget_revenue, 2)        AS budget_revenue_eur,
    ROUND(actual_revenue - budget_revenue, 2)
                                    AS revenue_variance_eur,
    ROUND(
        (actual_revenue - budget_revenue) /
        NULLIF(budget_revenue, 0) * 100
    , 2)                            AS revenue_variance_pct,
    ROUND(actual_cost, 2)           AS actual_cost_eur,
    ROUND(budget_cost, 2)           AS budget_cost_eur,
    ROUND(actual_cost - budget_cost, 2)
                                    AS cost_variance_eur,
    -- EBIT = Revenue - Cost
    ROUND(actual_revenue - actual_cost, 2)
                                    AS actual_ebit_eur,
    ROUND(budget_revenue - budget_cost, 2)
                                    AS budget_ebit_eur,
    -- EBIT Margin
    ROUND(
        (actual_revenue - actual_cost) /
        NULLIF(actual_revenue, 0) * 100
    , 2)                            AS actual_ebit_margin_pct,
    -- Active red signals
    (SELECT COUNT(*) FROM FACT_SIGNAL_LOG
     WHERE severity = 'RED')        AS active_red_signals,
    -- Active amber signals
    (SELECT COUNT(*) FROM FACT_SIGNAL_LOG
     WHERE severity = 'AMBER')      AS active_amber_signals,
    -- Average days saved
    (SELECT ROUND(AVG(days_saved), 1)
     FROM FACT_SIGNAL_LOG)          AS avg_early_warning_days
FROM period_summary;