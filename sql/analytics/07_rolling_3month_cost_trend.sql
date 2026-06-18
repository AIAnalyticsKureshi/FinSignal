-- ============================================================
-- Query 07: Rolling 3-Month Cost Trend
-- ============================================================
-- BUSINESS QUESTION:
-- What is the 3-month rolling average cost per cost centre?
-- Is the trend improving or deteriorating?
-- This smooths out one-off spikes to show the real trend.
--
-- USED IN: Power BI Page 3 — Cost Centre Profitability
-- AUDIENCE: Controller, Cost Centre Managers
-- FREQUENCY: Monthly
-- ============================================================

WITH monthly_costs AS (
    SELECT
        c.cost_centre_name,
        f.fiscal_period,
        d.fiscal_year,
        d.month_number,
        SUM(CASE
            WHEN f.scenario_id = 1 AND a.is_cost = 1
            THEN f.amount ELSE 0
        END) AS actual_cost_eur,
        SUM(CASE
            WHEN f.scenario_id = 2 AND a.is_cost = 1
            THEN f.amount ELSE 0
        END) AS budget_cost_eur
    FROM FACT_GL_ENTRIES f
    JOIN DIM_COST_CENTRE c ON f.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d ON f.date_id = d.date_id
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    GROUP BY
        c.cost_centre_name, f.fiscal_period,
        d.fiscal_year, d.month_number
)
SELECT
    cost_centre_name,
    fiscal_period,
    fiscal_year,
    month_number,
    ROUND(actual_cost_eur, 2)   AS actual_cost_eur,
    ROUND(budget_cost_eur, 2)   AS budget_cost_eur,
    -- 3-month rolling average actual cost
    ROUND(AVG(actual_cost_eur) OVER (
        PARTITION BY cost_centre_name
        ORDER BY fiscal_year, month_number
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                       AS rolling_3m_avg_cost,
    -- 3-month rolling average budget
    ROUND(AVG(budget_cost_eur) OVER (
        PARTITION BY cost_centre_name
        ORDER BY fiscal_year, month_number
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                       AS rolling_3m_avg_budget,
    -- Month over month change
    ROUND(actual_cost_eur - LAG(actual_cost_eur) OVER (
        PARTITION BY cost_centre_name
        ORDER BY fiscal_year, month_number
    ), 2)                       AS mom_change_eur,
    -- Trend direction
    CASE
        WHEN actual_cost_eur > LAG(actual_cost_eur) OVER (
            PARTITION BY cost_centre_name
            ORDER BY fiscal_year, month_number
        ) THEN 'INCREASING'
        WHEN actual_cost_eur < LAG(actual_cost_eur) OVER (
            PARTITION BY cost_centre_name
            ORDER BY fiscal_year, month_number
        ) THEN 'DECREASING'
        ELSE 'STABLE'
    END                         AS cost_trend
FROM monthly_costs
ORDER BY cost_centre_name, fiscal_year, month_number;