# ============================================================
# FinSignal — Data Generation Script
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
# 
# What this script does:
# Generates realistic synthetic data for all database tables
# Simulates 18 months of financial and operational activity
# Includes built-in anomalies for signal detection
# ============================================================

import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

# ============================================================
# CONFIGURATION
# These are the settings for the entire script
# If you want to change anything, change it here
# ============================================================

from config import (DB_PATH, START_DATE, END_DATE, 
                   RANDOM_SEED, CC_MANUFACTURING, 
                   CC_SALES, CC_LOGISTICS, CC_RD)

# Set random seed so data is the same every time you run it
# This is important for reproducibility
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ============================================================
# DATABASE CONNECTION
# This opens the connection to your finsignal.db file
# ============================================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Connected to database successfully")
print(f"Generating data from {START_DATE} to {END_DATE}")
print("=" * 50)


# ============================================================
# STEP 1 — FILL DIM_DATE
# Creates one row for every single day in our date range
# Calculates week number, month, quarter, fiscal year
# ============================================================

def generate_dim_date():
    print("Generating DIM_DATE...")
    
    dates = []
    current = START_DATE
    
    while current <= END_DATE:
        # Calculate the last day of this month
        if current.month == 12:
            last_day = date(current.year, 12, 31)
        else:
            last_day = date(current.year, current.month + 1, 1) - timedelta(days=1)
        
        # Calculate last day of quarter
        quarter = (current.month - 1) // 3 + 1
        quarter_end_month = quarter * 3
        if quarter_end_month == 12:
            last_quarter_day = date(current.year, 12, 31)
        else:
            last_quarter_day = date(current.year, 
                                   quarter_end_month + 1, 1) - timedelta(days=1)
        
        dates.append({
            "date_id": int(current.strftime("%Y%m%d")),
            "full_date": current.strftime("%Y-%m-%d"),
            "day_of_week": current.weekday() + 1,
            "week_number": current.isocalendar()[1],
            "month_number": current.month,
            "month_name": current.strftime("%B"),
            "quarter": quarter,
            "fiscal_year": current.year,
            "is_month_end": 1 if current == last_day else 0,
            "is_quarter_end": 1 if current == last_quarter_day else 0,
            "ytd_flag": 1
        })
        
        current += timedelta(days=1)
    
    df = pd.DataFrame(dates)
    df.to_sql("DIM_DATE", conn, if_exists="replace", index=False)
    print(f"  DIM_DATE: {len(df)} rows created")
    return df


# ============================================================
# STEP 2 — FILL DIM_COST_CENTRE
# The 6 departments of PräzisionWerk GmbH
# ============================================================

def generate_dim_cost_centre():
    print("Generating DIM_COST_CENTRE...")
    
    cost_centres = [
        {
            "cost_centre_id": 1,
            "cost_centre_code": "CC001",
            "cost_centre_name": "Manufacturing",
            "manager_name": "Klaus Weber",
            "department_type": "Production",
            "budget_owner": "COO",
            "headcount_budget": 85
        },
        {
            "cost_centre_id": 2,
            "cost_centre_code": "CC002",
            "cost_centre_name": "Sales",
            "manager_name": "Petra Müller",
            "department_type": "Revenue",
            "budget_owner": "CSO",
            "headcount_budget": 32
        },
        {
            "cost_centre_id": 3,
            "cost_centre_code": "CC003",
            "cost_centre_name": "Logistics",
            "manager_name": "Thomas Bauer",
            "department_type": "Operations",
            "budget_owner": "COO",
            "headcount_budget": 28
        },
        {
            "cost_centre_id": 4,
            "cost_centre_code": "CC004",
            "cost_centre_name": "Research & Development",
            "manager_name": "Dr. Anna Schmidt",
            "department_type": "Innovation",
            "budget_owner": "CTO",
            "headcount_budget": 24
        },
        {
            "cost_centre_id": 5,
            "cost_centre_code": "CC005",
            "cost_centre_name": "Administration",
            "manager_name": "Michael Hoffmann",
            "department_type": "Support",
            "budget_owner": "CFO",
            "headcount_budget": 18
        },
        {
            "cost_centre_id": 6,
            "cost_centre_code": "CC006",
            "cost_centre_name": "Finance & Controlling",
            "manager_name": "Sandra Koch",
            "department_type": "Finance",
            "budget_owner": "CFO",
            "headcount_budget": 12
        }
    ]
    
    df = pd.DataFrame(cost_centres)
    df.to_sql("DIM_COST_CENTRE", conn, if_exists="replace", index=False)
    print(f"  DIM_COST_CENTRE: {len(df)} rows created")
    return df


# ============================================================
# STEP 3 — FILL DIM_ACCOUNT
# Chart of accounts — the P&L structure
# pl_order determines the order in Power BI P&L report
# ============================================================

def generate_dim_account():
    print("Generating DIM_ACCOUNT...")
    
    accounts = [
        # Revenue accounts
        {
            "account_id": 1,
            "account_code": "4000",
            "account_name": "Product Revenue",
            "account_category": "Revenue",
            "pl_order": 1,
            "is_revenue": 1,
            "is_cost": 0
        },
        {
            "account_id": 2,
            "account_code": "4100",
            "account_name": "Service Revenue",
            "account_category": "Revenue",
            "pl_order": 2,
            "is_revenue": 1,
            "is_cost": 0
        },
        # Cost of Goods Sold
        {
            "account_id": 3,
            "account_code": "5000",
            "account_name": "Raw Material Costs",
            "account_category": "COGS",
            "pl_order": 3,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 4,
            "account_code": "5100",
            "account_name": "Production Labour Costs",
            "account_category": "COGS",
            "pl_order": 4,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 5,
            "account_code": "5200",
            "account_name": "Manufacturing Overhead",
            "account_category": "COGS",
            "pl_order": 5,
            "is_revenue": 0,
            "is_cost": 1
        },
        # Operating Expenses
        {
            "account_id": 6,
            "account_code": "6000",
            "account_name": "Sales & Marketing Expenses",
            "account_category": "OpEx",
            "pl_order": 6,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 7,
            "account_code": "6100",
            "account_name": "R&D Expenses",
            "account_category": "OpEx",
            "pl_order": 7,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 8,
            "account_code": "6200",
            "account_name": "Administrative Expenses",
            "account_category": "OpEx",
            "pl_order": 8,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 9,
            "account_code": "6300",
            "account_name": "Logistics & Distribution",
            "account_category": "OpEx",
            "pl_order": 9,
            "is_revenue": 0,
            "is_cost": 1
        },
        {
            "account_id": 10,
            "account_code": "6400",
            "account_name": "Depreciation",
            "account_category": "OpEx",
            "pl_order": 10,
            "is_revenue": 0,
            "is_cost": 1
        }
    ]
    
    df = pd.DataFrame(accounts)
    df.to_sql("DIM_ACCOUNT", conn, if_exists="replace", index=False)
    print(f"  DIM_ACCOUNT: {len(df)} rows created")
    return df


# ============================================================
# STEP 4 — FILL DIM_SCENARIO
# Actual = what really happened
# Budget = what was planned
# Forecast = updated prediction
# ============================================================

def generate_dim_scenario():
    print("Generating DIM_SCENARIO...")
    
    scenarios = [
        {
            "scenario_id": 1,
            "scenario_code": "ACT",
            "scenario_name": "Actual",
            "scenario_type": "Historical",
            "is_actuals": 1,
            "is_budget": 0,
            "is_forecast": 0
        },
        {
            "scenario_id": 2,
            "scenario_code": "BUD",
            "scenario_name": "Budget",
            "scenario_type": "Plan",
            "is_actuals": 0,
            "is_budget": 1,
            "is_forecast": 0
        },
        {
            "scenario_id": 3,
            "scenario_code": "FOR",
            "scenario_name": "Forecast",
            "scenario_type": "Projection",
            "is_actuals": 0,
            "is_budget": 0,
            "is_forecast": 1
        }
    ]
    
    df = pd.DataFrame(scenarios)
    df.to_sql("DIM_SCENARIO", conn, if_exists="replace", index=False)
    print(f"  DIM_SCENARIO: {len(df)} rows created")
    return df


# ============================================================
# STEP 5 — FILL DIM_PRODUCT_LINE
# 4 product lines
# Product Line C (PL003) is our hidden loss-maker
# ============================================================

def generate_dim_product_line():
    print("Generating DIM_PRODUCT_LINE...")
    
    product_lines = [
        {
            "product_line_id": 1,
            "product_code": "PL001",
            "product_name": "Precision Gears",
            "product_category": "Mechanical Components",
            "margin_target_pct": 28.5,
            "is_active": 1
        },
        {
            "product_line_id": 2,
            "product_code": "PL002",
            "product_name": "Hydraulic Systems",
            "product_category": "Fluid Systems",
            "margin_target_pct": 32.0,
            "is_active": 1
        },
        {
            "product_line_id": 3,
            "product_code": "PL003",
            "product_name": "Electronic Control Units",
            "product_category": "Electronics",
            "margin_target_pct": 35.0,
            "is_active": 1
        },
        {
            "product_line_id": 4,
            "product_code": "PL004",
            "product_name": "Assembly Services",
            "product_category": "Services",
            "margin_target_pct": 22.0,
            "is_active": 1
        }
    ]
    
    df = pd.DataFrame(product_lines)
    df.to_sql("DIM_PRODUCT_LINE", conn, if_exists="replace", index=False)
    print(f"  DIM_PRODUCT_LINE: {len(df)} rows created")
    return df


# ============================================================
# RUN ALL DIMENSION GENERATORS
# ============================================================

if __name__ == "__main__":
    print("\nSTARTING DATA GENERATION — DIMENSION TABLES")
    print("=" * 50)
    
    generate_dim_date()
    generate_dim_cost_centre()
    generate_dim_account()
    generate_dim_scenario()
    generate_dim_product_line()
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print("All dimension tables generated successfully")
  # ============================================================
# STEP 6 — FILL FACT_GL_ENTRIES
# Generates all financial transactions
# Includes built-in anomalies for signal detection
#
# ANOMALIES BUILT IN:
# 1. Manufacturing: 22% over budget in Q1 2025
# 2. Sales: revenue growing but margin declining
# 3. R&D: 3 months underspend (project delays)
# 4. Product Line C: positive revenue, negative EBIT
# 5. Working capital: Q4 2024 deterioration
# ============================================================

def generate_fact_gl_entries():
    conn2 = sqlite3.connect(DB_PATH)
    print("\nGenerating FACT_GL_ENTRIES...")

    # Monthly budget amounts per cost centre per account (EUR)
    # These are realistic numbers for a €45M revenue company
    monthly_budgets = {
        # (cost_centre_id, account_id): monthly_budget_amount
        # Manufacturing budgets
        (1, 3): 280000,   # Raw Materials - Manufacturing
        (1, 4): 195000,   # Labour - Manufacturing
        (1, 5): 85000,    # Overhead - Manufacturing
        # Sales budgets
        (2, 1): 2800000,  # Product Revenue - Sales
        (2, 2): 450000,   # Service Revenue - Sales
        (2, 6): 120000,   # Sales & Marketing Expenses
        # Logistics budgets
        (3, 9): 95000,    # Logistics & Distribution
        (3, 4): 65000,    # Labour - Logistics
        # R&D budgets
        (4, 7): 180000,   # R&D Expenses
        (4, 4): 95000,    # Labour - R&D
        # Administration budgets
        (5, 8): 75000,    # Administrative Expenses
        (5, 4): 55000,    # Labour - Administration
        # Finance & Controlling budgets
        (6, 8): 45000,    # Administrative Expenses - Finance
        (6, 4): 48000,    # Labour - Finance
        (6, 10): 25000,   # Depreciation
    }

    # Seasonality factors per month
    # Q4 is always stronger for revenue, Q1 weaker
    seasonality = {
        1: 0.85,   # January - slow start
        2: 0.88,   # February
        3: 0.92,   # March
        4: 0.95,   # April
        5: 0.98,   # May
        6: 1.00,   # June
        7: 0.90,   # July - summer slowdown
        8: 0.88,   # August - summer slowdown
        9: 1.02,   # September - pickup
        10: 1.08,  # October
        11: 1.12,  # November
        12: 1.18,  # December - year end push
    }

    entries = []
    entry_id = 1

    # Get all date_ids for month-end dates only
    # Budget entries are posted once per month
    cursor2 = conn2.cursor()
    cursor2.execute("""
        SELECT date_id, month_number, fiscal_year
        FROM DIM_DATE
        WHERE day_of_week = 5
        ORDER BY full_date
    """)
    month_end_dates = cursor2.fetchall()

    for date_id, month, year in month_end_dates:
        season = seasonality[month]
        fiscal_period = f"{year}-{month:02d}"

        for (cc_id, acc_id), budget_amount in monthly_budgets.items():

            # ------------------------------------------------
            # BUDGET ENTRY
            # Budget is always the planned amount
            # No seasonality on budget - it is fixed at start
            # ------------------------------------------------
            entries.append({
                "entry_id": entry_id,
                "date_id": date_id,
                "account_id": acc_id,
                "cost_centre_id": cc_id,
                "scenario_id": 2,  # Budget
                "product_line_id": assign_product_line(cc_id, acc_id),
                "amount": round(budget_amount, 2),
                "entry_type": "BUDGET",
                "fiscal_period": fiscal_period
            })
            entry_id += 1

            # ------------------------------------------------
            # ACTUAL ENTRY
            # Actuals vary around budget using seasonality
            # Plus random variation of +/- 8%
            # Plus specific anomalies for certain combinations
            # ------------------------------------------------
            actual_amount = budget_amount * season
            variation = np.random.uniform(-0.08, 0.08)
            actual_amount = actual_amount * (1 + variation)

            # ANOMALY 1: Manufacturing Raw Materials Q1 2025
            # 22% over budget due to raw material price shock
            if cc_id == 1 and acc_id == 3 and year == 2025 and month in [1, 2, 3]:
                actual_amount = budget_amount * 1.22

            # ANOMALY 2: Sales revenue growing but costs growing faster
            # Revenue grows 8% but marketing costs grow 18%
            if cc_id == 2 and acc_id == 1:
                actual_amount = budget_amount * season * 1.08
            if cc_id == 2 and acc_id == 6 and year >= 2024 and month >= 6:
                actual_amount = budget_amount * 1.18

            # ANOMALY 3: R&D underspend 3 consecutive months
            # Project delays in Q2 2024
            if cc_id == 4 and acc_id == 7 and year == 2024 and month in [4, 5, 6]:
                actual_amount = budget_amount * 0.65

            # ANOMALY 4: Product Line C hidden loss-maker
            # Handled in product line assignment below

            # ANOMALY 5: Q4 2024 working capital deterioration
            # Logistics costs spike in Q4 2024
            if cc_id == 3 and acc_id == 9 and year == 2024 and month in [10, 11, 12]:
                actual_amount = budget_amount * 1.28

            entries.append({
                "entry_id": entry_id,
                "date_id": date_id,
                "account_id": acc_id,
                "cost_centre_id": cc_id,
                "scenario_id": 1,  # Actual
                "product_line_id": assign_product_line(cc_id, acc_id),
                "amount": round(actual_amount, 2),
                "entry_type": "ACTUAL",
                "fiscal_period": fiscal_period
            })
            entry_id += 1

    df = pd.DataFrame(entries)
    df.to_sql("FACT_GL_ENTRIES", conn2, if_exists="replace", index=False)
    print(f"  FACT_GL_ENTRIES: {len(df)} rows created")
    conn2.commit()
    conn2.close()
    return df


def assign_product_line(cc_id, acc_id):
    # Assign product lines based on cost centre and account
    # Product Line C (id=3) gets assigned to Manufacturing
    # electronics accounts to create the hidden loss-maker
    if cc_id == 1 and acc_id in [3, 4, 5]:
        return random.choice([1, 2, 3, 3, 4])  # PL003 weighted higher
    elif cc_id == 2:
        return random.choice([1, 2, 3, 4])
    elif cc_id == 4:
        return 3  # R&D always linked to Electronic Control Units
    else:
        return random.choice([1, 2, 4])


# ============================================================
# STEP 7 — FILL FACT_OPERATIONAL
# Weekly operational data per cost centre
# This is the early warning data source
# ============================================================

def generate_fact_operational():
    conn3 = sqlite3.connect(DB_PATH)
    print("Generating FACT_OPERATIONAL...")

    cursor3 = conn3.cursor()
    cursor3.execute("""
        SELECT DISTINCT date_id, week_number, month_number, fiscal_year
        FROM DIM_DATE
        WHERE day_of_week = 1
        ORDER BY full_date
    """)
    weekly_dates = cursor3.fetchall()

    # Weekly budgets per cost centre
    weekly_op_budgets = {
        1: {"hours": 1800, "material_kg": 4200, "po": 12, "headcount": 85},
        2: {"hours": 640,  "material_kg": 0,    "po": 8,  "headcount": 32},
        3: {"hours": 560,  "material_kg": 800,  "po": 15, "headcount": 28},
        4: {"hours": 480,  "material_kg": 120,  "po": 4,  "headcount": 24},
        5: {"hours": 360,  "material_kg": 0,    "po": 3,  "headcount": 18},
        6: {"hours": 240,  "material_kg": 0,    "po": 2,  "headcount": 12},
    }

    op_entries = []
    op_id = 1

    for date_id, week, month, year in weekly_dates:
        for cc_id in range(1, 7):
            budget = weekly_op_budgets[cc_id]
            variation = np.random.uniform(-0.05, 0.05)

            hours_actual = budget["hours"] * (1 + variation)
            material_actual = budget["material_kg"] * (1 + variation)
            po_actual = budget["po"]
            headcount_actual = budget["headcount"]

            # ANOMALY 1: Manufacturing material consumption spike Q1 2025
            if cc_id == 1 and year == 2025 and month in [1, 2, 3]:
                material_actual = budget["material_kg"] * 1.22
                po_actual = int(budget["po"] * 1.15)

            # ANOMALY 3: R&D hours drop Q2 2024
            if cc_id == 4 and year == 2024 and month in [4, 5, 6]:
                hours_actual = budget["hours"] * 0.65

            # ANOMALY 5: Logistics spike Q4 2024
            if cc_id == 3 and year == 2024 and month in [10, 11, 12]:
                material_actual = budget["material_kg"] * 1.28
                po_actual = int(budget["po"] * 1.20)

            op_entries.append({
                "op_id": op_id,
                "date_id": date_id,
                "cost_centre_id": cc_id,
                "product_line_id": random.choice([1, 2, 3, 4]),
                "production_hours_actual": round(hours_actual, 1),
                "production_hours_budget": float(budget["hours"]),
                "material_consumed_kg": round(material_actual, 1),
                "material_budget_kg": float(budget["material_kg"]),
                "purchase_orders_placed": po_actual,
                "purchase_orders_budget": budget["po"],
                "headcount_active": headcount_actual,
                "headcount_budget": budget["headcount"],
                "operational_week": week,
                "operational_month": month,
                "operational_year": year
            })
            op_id += 1

    df = pd.DataFrame(op_entries)
    df.to_sql("FACT_OPERATIONAL", conn3, if_exists="replace", index=False)
    print(f"  FACT_OPERATIONAL: {len(df)} rows created")
    conn3.commit()
    conn3.close()
    return df


# ============================================================
# STEP 8 — FILL FACT_SIGNAL_LOG
# Records every early warning signal detected
# This is the proof that FinSignal works
# ============================================================

def generate_fact_signal_log():
    conn4 = sqlite3.connect(DB_PATH)
    print("Generating FACT_SIGNAL_LOG...")

    signals = [
        {
            "signal_id": 1,
            "detected_date_id": 20250114,
            "cost_centre_id": 1,
            "signal_type": "MATERIAL_COST_OVERRUN",
            "projected_overrun_eur": 320000,
            "days_before_monthend": 17,
            "threshold_breached": "MATERIAL_BUDGET_PCT > 110%",
            "severity": "RED",
            "traditional_report_date_id": 20250208,
            "days_saved": 25,
            "signal_status": "CONFIRMED"
        },
        {
            "signal_id": 2,
            "detected_date_id": 20250121,
            "cost_centre_id": 1,
            "signal_type": "MATERIAL_COST_OVERRUN",
            "projected_overrun_eur": 298000,
            "days_before_monthend": 10,
            "threshold_breached": "MATERIAL_BUDGET_PCT > 115%",
            "severity": "RED",
            "traditional_report_date_id": 20250208,
            "days_saved": 18,
            "signal_status": "CONFIRMED"
        },
        {
            "signal_id": 3,
            "detected_date_id": 20240415,
            "cost_centre_id": 4,
            "signal_type": "RD_UNDERSPEND",
            "projected_overrun_eur": -85000,
            "days_before_monthend": 15,
            "threshold_breached": "HOURS_UTILISATION < 70%",
            "severity": "AMBER",
            "traditional_report_date_id": 20240508,
            "days_saved": 23,
            "signal_status": "CONFIRMED"
        },
        {
            "signal_id": 4,
            "detected_date_id": 20241007,
            "cost_centre_id": 3,
            "signal_type": "LOGISTICS_COST_SPIKE",
            "projected_overrun_eur": 156000,
            "days_before_monthend": 24,
            "threshold_breached": "PO_VOLUME > 120% BUDGET",
            "severity": "AMBER",
            "traditional_report_date_id": 20241108,
            "days_saved": 32,
            "signal_status": "CONFIRMED"
        },
        {
            "signal_id": 5,
            "detected_date_id": 20240916,
            "cost_centre_id": 2,
            "signal_type": "MARGIN_COMPRESSION",
            "projected_overrun_eur": 94000,
            "days_before_monthend": 14,
            "threshold_breached": "CONTRIBUTION_MARGIN < 25%",
            "severity": "AMBER",
            "traditional_report_date_id": 20241008,
            "days_saved": 22,
            "signal_status": "CONFIRMED"
        }
    ]

    df = pd.DataFrame(signals)
    df.to_sql("FACT_SIGNAL_LOG", conn4, if_exists="replace", index=False)
    print(f"  FACT_SIGNAL_LOG: {len(df)} rows created")
    conn4.commit()
    conn4.close()
    return df


# ============================================================
# RUN ALL FACT TABLE GENERATORS
# ============================================================

print("\nSTARTING DATA GENERATION - FACT TABLES")
print("=" * 50)

generate_fact_gl_entries()
generate_fact_operational()
generate_fact_signal_log()

print("=" * 50)
print("ALL DATA GENERATION COMPLETE")
print("Database is ready for SQL analytics")  