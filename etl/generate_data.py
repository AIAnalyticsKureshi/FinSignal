# ============================================================
# FinSignal — Data Generation Script
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
#
# PURPOSE:
# This script generates realistic synthetic raw data files
# simulating what PräzisionWerk GmbH departments would export
# from their systems every week.
#
# OUTPUT: Excel files saved to data/raw/
# These files are then picked up by transform.py
#
# PIPELINE:
# generate_data.py → data/raw/ → transform.py → finsignal.db
# ============================================================

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import os
import sys

# Import settings from config.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (START_DATE, END_DATE, RANDOM_SEED,
                    CC_MANUFACTURING, CC_SALES, CC_LOGISTICS,
                    CC_RD, BASE_DIR)

# Set random seed for reproducibility
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Output folder for raw Excel files
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

print("=" * 55)
print("FINSIGNAL — RAW DATA GENERATION")
print(f"Output folder: {RAW_DATA_PATH}")
print("=" * 55)


# ============================================================
# DIMENSION DATA GENERATORS
# These create the reference/lookup data
# ============================================================

def generate_dim_date():
    dates = []
    current = START_DATE
    while current <= END_DATE:
        if current.month == 12:
            last_day = date(current.year, 12, 31)
        else:
            last_day = date(current.year, current.month + 1, 1) - timedelta(days=1)
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
    return pd.DataFrame(dates)


def generate_dim_cost_centre():
    cost_centres = [
        {"cost_centre_id": 1, "cost_centre_code": "CC001",
         "cost_centre_name": "Manufacturing", "manager_name": "Klaus Weber",
         "department_type": "Production", "budget_owner": "COO",
         "headcount_budget": 85},
        {"cost_centre_id": 2, "cost_centre_code": "CC002",
         "cost_centre_name": "Sales", "manager_name": "Petra Müller",
         "department_type": "Revenue", "budget_owner": "CSO",
         "headcount_budget": 32},
        {"cost_centre_id": 3, "cost_centre_code": "CC003",
         "cost_centre_name": "Logistics", "manager_name": "Thomas Bauer",
         "department_type": "Operations", "budget_owner": "COO",
         "headcount_budget": 28},
        {"cost_centre_id": 4, "cost_centre_code": "CC004",
         "cost_centre_name": "Research & Development",
         "manager_name": "Dr. Anna Schmidt",
         "department_type": "Innovation", "budget_owner": "CTO",
         "headcount_budget": 24},
        {"cost_centre_id": 5, "cost_centre_code": "CC005",
         "cost_centre_name": "Administration",
         "manager_name": "Michael Hoffmann",
         "department_type": "Support", "budget_owner": "CFO",
         "headcount_budget": 18},
        {"cost_centre_id": 6, "cost_centre_code": "CC006",
         "cost_centre_name": "Finance & Controlling",
         "manager_name": "Sandra Koch",
         "department_type": "Finance", "budget_owner": "CFO",
         "headcount_budget": 12}
    ]
    return pd.DataFrame(cost_centres)


def generate_dim_account():
    accounts = [
        {"account_id": 1, "account_code": "4000",
         "account_name": "Product Revenue",
         "account_category": "Revenue", "pl_order": 1,
         "is_revenue": 1, "is_cost": 0},
        {"account_id": 2, "account_code": "4100",
         "account_name": "Service Revenue",
         "account_category": "Revenue", "pl_order": 2,
         "is_revenue": 1, "is_cost": 0},
        {"account_id": 3, "account_code": "5000",
         "account_name": "Raw Material Costs",
         "account_category": "COGS", "pl_order": 3,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 4, "account_code": "5100",
         "account_name": "Production Labour Costs",
         "account_category": "COGS", "pl_order": 4,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 5, "account_code": "5200",
         "account_name": "Manufacturing Overhead",
         "account_category": "COGS", "pl_order": 5,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 6, "account_code": "6000",
         "account_name": "Sales & Marketing Expenses",
         "account_category": "OpEx", "pl_order": 6,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 7, "account_code": "6100",
         "account_name": "R&D Expenses",
         "account_category": "OpEx", "pl_order": 7,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 8, "account_code": "6200",
         "account_name": "Administrative Expenses",
         "account_category": "OpEx", "pl_order": 8,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 9, "account_code": "6300",
         "account_name": "Logistics & Distribution",
         "account_category": "OpEx", "pl_order": 9,
         "is_revenue": 0, "is_cost": 1},
        {"account_id": 10, "account_code": "6400",
         "account_name": "Depreciation",
         "account_category": "OpEx", "pl_order": 10,
         "is_revenue": 0, "is_cost": 1}
    ]
    return pd.DataFrame(accounts)


def generate_dim_scenario():
    scenarios = [
        {"scenario_id": 1, "scenario_code": "ACT",
         "scenario_name": "Actual", "scenario_type": "Historical",
         "is_actuals": 1, "is_budget": 0, "is_forecast": 0},
        {"scenario_id": 2, "scenario_code": "BUD",
         "scenario_name": "Budget", "scenario_type": "Plan",
         "is_actuals": 0, "is_budget": 1, "is_forecast": 0},
        {"scenario_id": 3, "scenario_code": "FOR",
         "scenario_name": "Forecast", "scenario_type": "Projection",
         "is_actuals": 0, "is_budget": 0, "is_forecast": 1}
    ]
    return pd.DataFrame(scenarios)


def generate_dim_product_line():
    product_lines = [
        {"product_line_id": 1, "product_code": "PL001",
         "product_name": "Precision Gears",
         "product_category": "Mechanical Components",
         "margin_target_pct": 28.5, "is_active": 1},
        {"product_line_id": 2, "product_code": "PL002",
         "product_name": "Hydraulic Systems",
         "product_category": "Fluid Systems",
         "margin_target_pct": 32.0, "is_active": 1},
        {"product_line_id": 3, "product_code": "PL003",
         "product_name": "Electronic Control Units",
         "product_category": "Electronics",
         "margin_target_pct": 35.0, "is_active": 1},
        {"product_line_id": 4, "product_code": "PL004",
         "product_name": "Assembly Services",
         "product_category": "Services",
         "margin_target_pct": 22.0, "is_active": 1}
    ]
    return pd.DataFrame(product_lines)


# ============================================================
# FACT DATA GENERATORS
# ============================================================

def assign_product_line(cc_id, acc_id):
    if cc_id == 1 and acc_id in [3, 4, 5]:
        return random.choice([1, 2, 3, 3, 4])
    elif cc_id == 2:
        return random.choice([1, 2, 3, 4])
    elif cc_id == 4:
        return 3
    else:
        return random.choice([1, 2, 4])


def generate_fact_gl_entries(date_df):
    print("Generating GL entries...")

    seasonality = {
        1: 0.85, 2: 0.88, 3: 0.92, 4: 0.95,
        5: 0.98, 6: 1.00, 7: 0.90, 8: 0.88,
        9: 1.02, 10: 1.08, 11: 1.12, 12: 1.18
    }

    monthly_budgets = {
        (1, 3): 280000, (1, 4): 195000, (1, 5): 85000,
        (2, 1): 2800000, (2, 2): 450000, (2, 6): 120000,
        (3, 9): 95000, (3, 4): 65000,
        (4, 7): 180000, (4, 4): 95000,
        (5, 8): 75000, (5, 4): 55000,
        (6, 8): 45000, (6, 4): 48000, (6, 10): 25000
    }

    weekly_dates = date_df[date_df["day_of_week"] == 5][
        ["date_id", "month_number", "fiscal_year", "fiscal_period"]
        if "fiscal_period" in date_df.columns
        else ["date_id", "month_number", "fiscal_year"]
    ].copy()

    # Add fiscal_period column
    weekly_dates["fiscal_period"] = (
        weekly_dates["fiscal_year"].astype(str) + "-" +
        weekly_dates["month_number"].astype(str).str.zfill(2)
    )

    entries = []
    entry_id = 1

    for _, row in weekly_dates.iterrows():
        date_id = row["date_id"]
        month = row["month_number"]
        year = row["fiscal_year"]
        fiscal_period = row["fiscal_period"]
        season = seasonality[month]

        for (cc_id, acc_id), budget_amount in monthly_budgets.items():

            # Weekly budget = monthly budget / 4
            weekly_budget = budget_amount / 4

            entries.append({
                "entry_id": entry_id,
                "date_id": date_id,
                "account_id": acc_id,
                "cost_centre_id": cc_id,
                "scenario_id": 2,
                "product_line_id": assign_product_line(cc_id, acc_id),
                "amount": round(weekly_budget, 2),
                "entry_type": "BUDGET",
                "fiscal_period": fiscal_period
            })
            entry_id += 1

            actual_amount = weekly_budget * season
            variation = np.random.uniform(-0.08, 0.08)
            actual_amount = actual_amount * (1 + variation)

            # ANOMALY 1: Manufacturing Raw Materials Q1 2025
            if cc_id == 1 and acc_id == 3 and year == 2025 and month in [1, 2, 3]:
                actual_amount = weekly_budget * 1.22

            # ANOMALY 2: Sales margin compression
            if cc_id == 2 and acc_id == 1:
                actual_amount = weekly_budget * season * 1.08
            if cc_id == 2 and acc_id == 6 and year >= 2024 and month >= 6:
                actual_amount = weekly_budget * 1.18

            # ANOMALY 3: R&D underspend Q2 2024
            if cc_id == 4 and acc_id == 7 and year == 2024 and month in [4, 5, 6]:
                actual_amount = weekly_budget * 0.65

            # ANOMALY 5: Logistics spike Q4 2024
            if cc_id == 3 and acc_id == 9 and year == 2024 and month in [10, 11, 12]:
                actual_amount = weekly_budget * 1.28

            entries.append({
                "entry_id": entry_id,
                "date_id": date_id,
                "account_id": acc_id,
                "cost_centre_id": cc_id,
                "scenario_id": 1,
                "product_line_id": assign_product_line(cc_id, acc_id),
                "amount": round(actual_amount, 2),
                "entry_type": "ACTUAL",
                "fiscal_period": fiscal_period
            })
            entry_id += 1

    return pd.DataFrame(entries)


def generate_fact_operational(date_df):
    print("Generating operational data...")

    weekly_op_budgets = {
        1: {"hours": 1800, "material_kg": 4200, "po": 12, "headcount": 85},
        2: {"hours": 640, "material_kg": 0, "po": 8, "headcount": 32},
        3: {"hours": 560, "material_kg": 800, "po": 15, "headcount": 28},
        4: {"hours": 480, "material_kg": 120, "po": 4, "headcount": 24},
        5: {"hours": 360, "material_kg": 0, "po": 3, "headcount": 18},
        6: {"hours": 240, "material_kg": 0, "po": 2, "headcount": 12}
    }

    monday_dates = date_df[date_df["day_of_week"] == 1][
        ["date_id", "week_number", "month_number", "fiscal_year"]
    ].copy()

    op_entries = []
    op_id = 1

    for _, row in monday_dates.iterrows():
        date_id = row["date_id"]
        week = row["week_number"]
        month = row["month_number"]
        year = row["fiscal_year"]

        for cc_id in range(1, 7):
            budget = weekly_op_budgets[cc_id]
            variation = np.random.uniform(-0.05, 0.05)

            hours_actual = budget["hours"] * (1 + variation)
            material_actual = budget["material_kg"] * (1 + variation)
            po_actual = budget["po"]
            headcount_actual = budget["headcount"]

            if cc_id == 1 and year == 2025 and month in [1, 2, 3]:
                material_actual = budget["material_kg"] * 1.22
                po_actual = int(budget["po"] * 1.15)

            if cc_id == 4 and year == 2024 and month in [4, 5, 6]:
                hours_actual = budget["hours"] * 0.65

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

    return pd.DataFrame(op_entries)


def generate_fact_signal_log():
    signals = [
        {"signal_id": 1, "detected_date_id": 20250114,
         "cost_centre_id": 1, "signal_type": "MATERIAL_COST_OVERRUN",
         "projected_overrun_eur": 320000, "days_before_monthend": 17,
         "threshold_breached": "MATERIAL_BUDGET_PCT > 110%",
         "severity": "RED", "traditional_report_date_id": 20250208,
         "days_saved": 25, "signal_status": "CONFIRMED"},
        {"signal_id": 2, "detected_date_id": 20250121,
         "cost_centre_id": 1, "signal_type": "MATERIAL_COST_OVERRUN",
         "projected_overrun_eur": 298000, "days_before_monthend": 10,
         "threshold_breached": "MATERIAL_BUDGET_PCT > 115%",
         "severity": "RED", "traditional_report_date_id": 20250208,
         "days_saved": 18, "signal_status": "CONFIRMED"},
        {"signal_id": 3, "detected_date_id": 20240415,
         "cost_centre_id": 4, "signal_type": "RD_UNDERSPEND",
         "projected_overrun_eur": -85000, "days_before_monthend": 15,
         "threshold_breached": "HOURS_UTILISATION < 70%",
         "severity": "AMBER", "traditional_report_date_id": 20240508,
         "days_saved": 23, "signal_status": "CONFIRMED"},
        {"signal_id": 4, "detected_date_id": 20241007,
         "cost_centre_id": 3, "signal_type": "LOGISTICS_COST_SPIKE",
         "projected_overrun_eur": 156000, "days_before_monthend": 24,
         "threshold_breached": "PO_VOLUME > 120% BUDGET",
         "severity": "AMBER", "traditional_report_date_id": 20241108,
         "days_saved": 32, "signal_status": "CONFIRMED"},
        {"signal_id": 5, "detected_date_id": 20240916,
         "cost_centre_id": 2, "signal_type": "MARGIN_COMPRESSION",
         "projected_overrun_eur": 94000, "days_before_monthend": 14,
         "threshold_breached": "CONTRIBUTION_MARGIN < 25%",
         "severity": "AMBER", "traditional_report_date_id": 20241008,
         "days_saved": 22, "signal_status": "CONFIRMED"}
    ]
    return pd.DataFrame(signals)


# ============================================================
# SAVE ALL DATA TO EXCEL FILES IN data/raw/
# ============================================================

if __name__ == "__main__":
    print("\nGenerating all dimension and fact data...")
    print("=" * 55)

    # Generate all dataframes
    df_date = generate_dim_date()
    df_cc = generate_dim_cost_centre()
    df_account = generate_dim_account()
    df_scenario = generate_dim_scenario()
    df_product = generate_dim_product_line()
    df_gl = generate_fact_gl_entries(df_date)
    df_op = generate_fact_operational(df_date)
    df_signal = generate_fact_signal_log()

    # Save each to its own Excel file in data/raw/
    files = {
        "dim_date.xlsx": df_date,
        "dim_cost_centre.xlsx": df_cc,
        "dim_account.xlsx": df_account,
        "dim_scenario.xlsx": df_scenario,
        "dim_product_line.xlsx": df_product,
        "fact_gl_entries.xlsx": df_gl,
        "fact_operational.xlsx": df_op,
        "fact_signal_log.xlsx": df_signal
    }

    for filename, df in files.items():
        filepath = os.path.join(RAW_DATA_PATH, filename)
        df.to_excel(filepath, index=False)
        print(f"  Saved: {filename} ({len(df)} rows)")

    print("=" * 55)
    print("All raw Excel files saved to data/raw/")
    print("Now run transform.py to load into database")