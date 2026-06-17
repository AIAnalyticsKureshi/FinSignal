# ============================================================
# FinSignal — ETL Transform Script
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
#
# PURPOSE:
# Reads raw Excel files from data/raw/
# Applies data cleaning and transformation rules
# Loads clean data into finsignal.db
#
# PIPELINE:
# generate_data.py → data/raw/ → transform.py → finsignal.db
#
# HOW TO RUN:
# python etl/transform.py
# ============================================================

import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, BASE_DIR

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

print("=" * 55)
print("FINSIGNAL — ETL TRANSFORM PIPELINE")
print(f"Source:   {RAW_DATA_PATH}")
print(f"Target:   {DB_PATH}")
print(f"Started:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)

conn = sqlite3.connect(DB_PATH)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_excel(filename):
    filepath = os.path.join(RAW_DATA_PATH, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw file not found: {filepath}")
    df = pd.read_excel(filepath)
    print(f"\n  Reading: {filename} ({len(df)} rows)")
    return df


def load_to_db(df, table_name):
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"  Loaded:  {table_name} — {len(df)} rows inserted")


# ============================================================
# TRANSFORM FUNCTIONS
# Each function reads one Excel file, cleans it, loads it
# ============================================================

def transform_dim_date():
    df = read_excel("dim_date.xlsx")

    # Ensure correct data types
    df["date_id"] = df["date_id"].astype(int)
    df["full_date"] = pd.to_datetime(df["full_date"]).dt.strftime("%Y-%m-%d")
    df["day_of_week"] = df["day_of_week"].astype(int)
    df["week_number"] = df["week_number"].astype(int)
    df["month_number"] = df["month_number"].astype(int)
    df["month_name"] = df["month_name"].astype(str).str.strip()
    df["quarter"] = df["quarter"].astype(int)
    df["fiscal_year"] = df["fiscal_year"].astype(int)
    df["is_month_end"] = df["is_month_end"].astype(int)
    df["is_quarter_end"] = df["is_quarter_end"].astype(int)
    df["ytd_flag"] = df["ytd_flag"].astype(int)

    # Remove any duplicates
    df = df.drop_duplicates(subset=["date_id"])

    load_to_db(df, "DIM_DATE")


def transform_dim_cost_centre():
    df = read_excel("dim_cost_centre.xlsx")

    df["cost_centre_id"] = df["cost_centre_id"].astype(int)
    df["cost_centre_code"] = df["cost_centre_code"].astype(str).str.strip()
    df["cost_centre_name"] = df["cost_centre_name"].astype(str).str.strip()
    df["manager_name"] = df["manager_name"].astype(str).str.strip()
    df["department_type"] = df["department_type"].astype(str).str.strip()
    df["budget_owner"] = df["budget_owner"].astype(str).str.strip()
    df["headcount_budget"] = df["headcount_budget"].astype(int)

    df = df.drop_duplicates(subset=["cost_centre_id"])

    load_to_db(df, "DIM_COST_CENTRE")


def transform_dim_account():
    df = read_excel("dim_account.xlsx")

    df["account_id"] = df["account_id"].astype(int)
    df["account_code"] = df["account_code"].astype(str).str.strip()
    df["account_name"] = df["account_name"].astype(str).str.strip()
    df["account_category"] = df["account_category"].astype(str).str.strip()
    df["pl_order"] = df["pl_order"].astype(int)
    df["is_revenue"] = df["is_revenue"].astype(int)
    df["is_cost"] = df["is_cost"].astype(int)

    df = df.drop_duplicates(subset=["account_id"])

    load_to_db(df, "DIM_ACCOUNT")


def transform_dim_scenario():
    df = read_excel("dim_scenario.xlsx")

    df["scenario_id"] = df["scenario_id"].astype(int)
    df["scenario_code"] = df["scenario_code"].astype(str).str.strip()
    df["scenario_name"] = df["scenario_name"].astype(str).str.strip()
    df["scenario_type"] = df["scenario_type"].astype(str).str.strip()
    df["is_actuals"] = df["is_actuals"].astype(int)
    df["is_budget"] = df["is_budget"].astype(int)
    df["is_forecast"] = df["is_forecast"].astype(int)

    df = df.drop_duplicates(subset=["scenario_id"])

    load_to_db(df, "DIM_SCENARIO")


def transform_dim_product_line():
    df = read_excel("dim_product_line.xlsx")

    df["product_line_id"] = df["product_line_id"].astype(int)
    df["product_code"] = df["product_code"].astype(str).str.strip()
    df["product_name"] = df["product_name"].astype(str).str.strip()
    df["product_category"] = df["product_category"].astype(str).str.strip()
    df["margin_target_pct"] = df["margin_target_pct"].astype(float)
    df["is_active"] = df["is_active"].astype(int)

    df = df.drop_duplicates(subset=["product_line_id"])

    load_to_db(df, "DIM_PRODUCT_LINE")


def transform_fact_gl_entries():
    df = read_excel("fact_gl_entries.xlsx")

    df["entry_id"] = df["entry_id"].astype(int)
    df["date_id"] = df["date_id"].astype(int)
    df["account_id"] = df["account_id"].astype(int)
    df["cost_centre_id"] = df["cost_centre_id"].astype(int)
    df["scenario_id"] = df["scenario_id"].astype(int)
    df["product_line_id"] = df["product_line_id"].astype(int)
    df["amount"] = df["amount"].astype(float).round(2)
    df["entry_type"] = df["entry_type"].astype(str).str.strip()
    df["fiscal_period"] = df["fiscal_period"].astype(str).str.strip()

    # Remove any rows with null amounts
    before = len(df)
    df = df.dropna(subset=["amount", "date_id", "cost_centre_id"])
    after = len(df)
    if before != after:
        print(f"  Cleaned: {before - after} rows removed (nulls)")

    load_to_db(df, "FACT_GL_ENTRIES")


def transform_fact_operational():
    df = read_excel("fact_operational.xlsx")

    df["op_id"] = df["op_id"].astype(int)
    df["date_id"] = df["date_id"].astype(int)
    df["cost_centre_id"] = df["cost_centre_id"].astype(int)
    df["product_line_id"] = df["product_line_id"].astype(int)
    df["production_hours_actual"] = df["production_hours_actual"].astype(float)
    df["production_hours_budget"] = df["production_hours_budget"].astype(float)
    df["material_consumed_kg"] = df["material_consumed_kg"].astype(float)
    df["material_budget_kg"] = df["material_budget_kg"].astype(float)
    df["purchase_orders_placed"] = df["purchase_orders_placed"].astype(int)
    df["purchase_orders_budget"] = df["purchase_orders_budget"].astype(int)
    df["headcount_active"] = df["headcount_active"].astype(int)
    df["headcount_budget"] = df["headcount_budget"].astype(int)
    df["operational_week"] = df["operational_week"].astype(int)
    df["operational_month"] = df["operational_month"].astype(int)
    df["operational_year"] = df["operational_year"].astype(int)

    load_to_db(df, "FACT_OPERATIONAL")


def transform_fact_signal_log():
    df = read_excel("fact_signal_log.xlsx")

    df["signal_id"] = df["signal_id"].astype(int)
    df["detected_date_id"] = df["detected_date_id"].astype(int)
    df["cost_centre_id"] = df["cost_centre_id"].astype(int)
    df["signal_type"] = df["signal_type"].astype(str).str.strip()
    df["projected_overrun_eur"] = df["projected_overrun_eur"].astype(float)
    df["days_before_monthend"] = df["days_before_monthend"].astype(int)
    df["threshold_breached"] = df["threshold_breached"].astype(str).str.strip()
    df["severity"] = df["severity"].astype(str).str.strip()
    df["traditional_report_date_id"] = df["traditional_report_date_id"].astype(int)
    df["days_saved"] = df["days_saved"].astype(int)
    df["signal_status"] = df["signal_status"].astype(str).str.strip()

    load_to_db(df, "FACT_SIGNAL_LOG")


# ============================================================
# RUN FULL PIPELINE
# Order matters — dimensions must load before facts
# because facts reference dimension IDs
# ============================================================

print("\nLOADING DIMENSION TABLES FIRST")
print("-" * 40)
transform_dim_date()
transform_dim_cost_centre()
transform_dim_account()
transform_dim_scenario()
transform_dim_product_line()

print("\nLOADING FACT TABLES")
print("-" * 40)
transform_fact_gl_entries()
transform_fact_operational()
transform_fact_signal_log()

conn.commit()
conn.close()

print("\n" + "=" * 55)
print("ETL PIPELINE COMPLETE")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Run validate.py to verify data quality")
print("=" * 55)