-- ============================================================
-- FinSignal Database Schema
-- Project: Operational-Financial Early Warning System
-- Company: PräzisionWerk GmbH, Stuttgart
-- Author: Mohammad M. Kureshi
-- Version: 2.0
-- ============================================================


-- ============================================================
-- DIMENSION TABLES (the descriptive tables)
-- Think of these as your lookup/reference tables
-- They answer WHO, WHAT, WHEN, WHERE
-- ============================================================


-- DIM_DATE
-- Answers: WHEN did this happen?
-- Contains every single day from Jan 2024 to Jun 2025
-- Includes fiscal intelligence so we can filter by
-- week, month, quarter, fiscal year in Power BI
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_DATE (
    date_id          INTEGER PRIMARY KEY,
    full_date        DATE NOT NULL,
    day_of_week      INTEGER NOT NULL,
    week_number      INTEGER NOT NULL,
    month_number     INTEGER NOT NULL,
    month_name       TEXT NOT NULL,
    quarter          INTEGER NOT NULL,
    fiscal_year      INTEGER NOT NULL,
    is_month_end     INTEGER NOT NULL DEFAULT 0,
    is_quarter_end   INTEGER NOT NULL DEFAULT 0,
    ytd_flag         INTEGER NOT NULL DEFAULT 1
);


-- DIM_ACCOUNT
-- Answers: WHAT type of financial transaction is this?
-- Contains the chart of accounts (P&L hierarchy)
-- Revenue → COGS → Gross Profit → OpEx → EBITDA → EBIT
-- pl_order tells Power BI in which order to show P&L lines
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_ACCOUNT (
    account_id       INTEGER PRIMARY KEY,
    account_code     TEXT NOT NULL UNIQUE,
    account_name     TEXT NOT NULL,
    account_category TEXT NOT NULL,
    pl_order         INTEGER NOT NULL,
    is_revenue       INTEGER NOT NULL DEFAULT 0,
    is_cost          INTEGER NOT NULL DEFAULT 0
);


-- DIM_COST_CENTRE
-- Answers: WHERE (which department) did this happen?
-- 6 departments of PräzisionWerk GmbH
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_COST_CENTRE (
    cost_centre_id   INTEGER PRIMARY KEY,
    cost_centre_code TEXT NOT NULL UNIQUE,
    cost_centre_name TEXT NOT NULL,
    manager_name     TEXT NOT NULL,
    department_type  TEXT NOT NULL,
    budget_owner     TEXT NOT NULL,
    headcount_budget INTEGER NOT NULL
);


-- DIM_SCENARIO
-- Answers: Is this Actual data, Budget data, or Forecast?
-- This is what enables 3-way comparison in Power BI
-- Without this table, you cannot compare Budget vs Actual
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_SCENARIO (
    scenario_id    INTEGER PRIMARY KEY,
    scenario_code  TEXT NOT NULL UNIQUE,
    scenario_name  TEXT NOT NULL,
    scenario_type  TEXT NOT NULL,
    is_actuals     INTEGER NOT NULL DEFAULT 0,
    is_budget      INTEGER NOT NULL DEFAULT 0,
    is_forecast    INTEGER NOT NULL DEFAULT 0
);


-- DIM_PRODUCT_LINE
-- Answers: WHICH product line does this belong to?
-- 4 product lines of PräzisionWerk GmbH
-- Product Line C is our hidden loss-maker anomaly
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_PRODUCT_LINE (
    product_line_id   INTEGER PRIMARY KEY,
    product_code      TEXT NOT NULL UNIQUE,
    product_name      TEXT NOT NULL,
    product_category  TEXT NOT NULL,
    margin_target_pct REAL NOT NULL,
    is_active         INTEGER NOT NULL DEFAULT 1
);


-- ============================================================
-- FACT TABLES (the number tables)
-- These store the actual measurements and amounts
-- They answer HOW MUCH
-- Each row links to dimension tables through foreign keys
-- ============================================================


-- FACT_GL_ENTRIES
-- The heart of financial data
-- Every financial transaction lives here
-- Each row = one financial posting
-- Links to ALL dimension tables
-- ============================================================
CREATE TABLE IF NOT EXISTS FACT_GL_ENTRIES (
    entry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id         INTEGER NOT NULL,
    account_id      INTEGER NOT NULL,
    cost_centre_id  INTEGER NOT NULL,
    scenario_id     INTEGER NOT NULL,
    product_line_id INTEGER NOT NULL,
    amount          REAL NOT NULL,
    entry_type      TEXT NOT NULL,
    fiscal_period   TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (date_id)
        REFERENCES DIM_DATE(date_id),
    FOREIGN KEY (account_id)
        REFERENCES DIM_ACCOUNT(account_id),
    FOREIGN KEY (cost_centre_id)
        REFERENCES DIM_COST_CENTRE(cost_centre_id),
    FOREIGN KEY (scenario_id)
        REFERENCES DIM_SCENARIO(scenario_id),
    FOREIGN KEY (product_line_id)
        REFERENCES DIM_PRODUCT_LINE(product_line_id)
);


-- FACT_OPERATIONAL
-- THIS IS WHAT MAKES FINSIGNAL UNIQUE
-- Stores weekly operational data from department Excel files
-- Each row = one week of activity per cost centre
-- By comparing actual vs budget operational pace,
-- we can PREDICT the financial outcome before month end
-- No other BI portfolio project has this table
-- ============================================================
CREATE TABLE IF NOT EXISTS FACT_OPERATIONAL (
    op_id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id                   INTEGER NOT NULL,
    cost_centre_id            INTEGER NOT NULL,
    product_line_id           INTEGER NOT NULL,
    production_hours_actual   REAL NOT NULL DEFAULT 0,
    production_hours_budget   REAL NOT NULL DEFAULT 0,
    material_consumed_kg      REAL NOT NULL DEFAULT 0,
    material_budget_kg        REAL NOT NULL DEFAULT 0,
    purchase_orders_placed    INTEGER NOT NULL DEFAULT 0,
    purchase_orders_budget    INTEGER NOT NULL DEFAULT 0,
    headcount_active          INTEGER NOT NULL DEFAULT 0,
    headcount_budget          INTEGER NOT NULL DEFAULT 0,
    operational_week          INTEGER NOT NULL,
    operational_month         INTEGER NOT NULL,
    operational_year          INTEGER NOT NULL,

    FOREIGN KEY (date_id)
        REFERENCES DIM_DATE(date_id),
    FOREIGN KEY (cost_centre_id)
        REFERENCES DIM_COST_CENTRE(cost_centre_id),
    FOREIGN KEY (product_line_id)
        REFERENCES DIM_PRODUCT_LINE(product_line_id)
);


-- FACT_SIGNAL_LOG
-- THIS IS THE MOST SENIOR LEVEL TABLE IN THIS PROJECT
-- Every time the signal engine detects an early warning,
-- it logs it here with full details
-- This table answers the most powerful question:
-- "How many days earlier did FinSignal detect this
--  problem vs the traditional monthly report?"
-- That number is your headline metric on your CV
-- ============================================================
CREATE TABLE IF NOT EXISTS FACT_SIGNAL_LOG (
    signal_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_date_id           INTEGER NOT NULL,
    cost_centre_id             INTEGER NOT NULL,
    signal_type                TEXT NOT NULL,
    projected_overrun_eur      REAL NOT NULL,
    days_before_monthend       INTEGER NOT NULL,
    threshold_breached         TEXT NOT NULL,
    severity                   TEXT NOT NULL,
    traditional_report_date_id INTEGER NOT NULL,
    days_saved                 INTEGER NOT NULL,
    signal_status              TEXT NOT NULL DEFAULT 'OPEN',
    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (detected_date_id)
        REFERENCES DIM_DATE(date_id),
    FOREIGN KEY (cost_centre_id)
        REFERENCES DIM_COST_CENTRE(cost_centre_id),
    FOREIGN KEY (traditional_report_date_id)
        REFERENCES DIM_DATE(date_id)
);


-- ============================================================
-- INDEXES
-- Make queries faster by indexing the most used columns
-- These are the columns we filter and join on most often
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_gl_date
    ON FACT_GL_ENTRIES(date_id);
CREATE INDEX IF NOT EXISTS idx_gl_cost_centre
    ON FACT_GL_ENTRIES(cost_centre_id);
CREATE INDEX IF NOT EXISTS idx_gl_scenario
    ON FACT_GL_ENTRIES(scenario_id);
CREATE INDEX IF NOT EXISTS idx_gl_account
    ON FACT_GL_ENTRIES(account_id);
CREATE INDEX IF NOT EXISTS idx_op_date
    ON FACT_OPERATIONAL(date_id);
CREATE INDEX IF NOT EXISTS idx_op_cost_centre
    ON FACT_OPERATIONAL(cost_centre_id);
CREATE INDEX IF NOT EXISTS idx_op_week
    ON FACT_OPERATIONAL(operational_week);
CREATE INDEX IF NOT EXISTS idx_signal_date
    ON FACT_SIGNAL_LOG(detected_date_id);
CREATE INDEX IF NOT EXISTS idx_signal_cost_centre
    ON FACT_SIGNAL_LOG(cost_centre_id);