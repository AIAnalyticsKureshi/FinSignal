-- ============================================================
-- Query 19: Scenario Comparison — Actual vs Budget vs Forecast
-- ============================================================
-- BUSINESS QUESTION:
-- How do all three scenarios compare side by side?
-- Actual vs Budget vs Forecast for each period.
-- This powers the scenario toggle in Power BI Page 4.
--
-- USED IN: Power BI Page 4 — Scenario Projection
-- AUDIENCE: CFO, FP&A Team
-- FREQUENCY: Monthly
-- ============================================================

WITH scenario_data AS (
    SELECT
        f.fiscal_period,
        d.fiscal_year,
        d.month_number,
        s.scenario_name,
        s.scenario_type,
        SUM(CASE WHEN a.is_revenue = 1
            THEN f.amount ELSE 0 END) AS revenue_eur,
        SUM(CASE WHEN a.is_cost = 1
            THEN f.amount ELSE 0 END) AS cost_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_SCENARIO s ON f.scenario_id = s.scenario_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    JOIN DIM_DATE d ON f.date_id = d.date_id
    GROUP BY f.fiscal_period, d.fiscal_year,
             d.month_number, s.scenario_name, s.scenario_type
)
SELECT
    fiscal_period,
    fiscal_year,
    month_number,
    ROUND(MAX(CASE WHEN scenario_name = 'Actual'
        THEN revenue_eur END), 2)   AS actual_revenue,
    ROUND(MAX(CASE WHEN scenario_name = 'Budget'
        THEN revenue_eur END), 2)   AS budget_revenue,
    ROUND(MAX(CASE WHEN scenario_name = 'Actual'
        THEN cost_eur END), 2)      AS actual_cost,
    ROUND(MAX(CASE WHEN scenario_name = 'Budget'
        THEN cost_eur END), 2)      AS budget_cost,
    -- EBIT per scenario
    ROUND(MAX(CASE WHEN scenario_name = 'Actual'
        THEN revenue_eur - cost_eur END), 2)
                                    AS actual_ebit,
    ROUND(MAX(CASE WHEN scenario_name = 'Budget'
        THEN revenue_eur - cost_eur END), 2)
                                    AS budget_ebit,
    -- Variance actual vs budget
    ROUND(
        MAX(CASE WHEN scenario_name = 'Actual'
            THEN revenue_eur END) -
        MAX(CASE WHEN scenario_name = 'Budget'
            THEN revenue_eur END)
    , 2)                            AS revenue_variance_eur,
    ROUND(
        MAX(CASE WHEN scenario_name = 'Actual'
            THEN revenue_eur - cost_eur END) -
        MAX(CASE WHEN scenario_name = 'Budget'
            THEN revenue_eur - cost_eur END)
    , 2)                            AS ebit_variance_eur
FROM scenario_data
GROUP BY fiscal_period, fiscal_year, month_number
ORDER BY fiscal_year, month_number;