# ============================================================
# FinSignal — Data Quality Validation Script
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
#
# What this script does:
# Runs 8 automated data quality checks on finsignal.db
# Produces a scorecard showing pass/fail for each check
# A 100% score means the data is trustworthy for analysis
# ============================================================

import sqlite3
import json
from datetime import datetime

from config import DB_PATH, DQ_SCORECARD_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 55)
print("FINSIGNAL — DATA QUALITY VALIDATION REPORT")
print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Database: {DB_PATH}")
print("=" * 55)

results = []


# ============================================================
# CHECK 1 — NULL COUNT CHECK
# No critical column should have empty values
# In finance data, a transaction with no amount or no date
# is meaningless and dangerous
# ============================================================

def check_nulls():
    checks = [
        ("FACT_GL_ENTRIES",    "amount"),
        ("FACT_GL_ENTRIES",    "date_id"),
        ("FACT_GL_ENTRIES",    "cost_centre_id"),
        ("FACT_GL_ENTRIES",    "scenario_id"),
        ("FACT_OPERATIONAL",   "material_consumed_kg"),
        ("FACT_OPERATIONAL",   "production_hours_actual"),
        ("FACT_SIGNAL_LOG",    "projected_overrun_eur"),
        ("FACT_SIGNAL_LOG",    "days_saved"),
    ]

    total_nulls = 0
    for table, column in checks:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
        null_count = cursor.fetchone()[0]
        total_nulls += null_count

    passed = total_nulls == 0
    results.append({
        "check_id": 1,
        "check_name": "Null Count Check",
        "description": "No critical columns contain NULL values",
        "passed": passed,
        "detail": f"Total nulls found: {total_nulls}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 1 — Null Count Check: {status}")
    print(f"  Detail: {total_nulls} null values found in critical columns")


# ============================================================
# CHECK 2 — REFERENTIAL INTEGRITY CHECK
# Every foreign key in fact tables must point to a valid
# record in the dimension table
# Example: every cost_centre_id in FACT_GL_ENTRIES must
# exist in DIM_COST_CENTRE
# ============================================================

def check_referential_integrity():
    checks = [
        ("FACT_GL_ENTRIES", "cost_centre_id", "DIM_COST_CENTRE", "cost_centre_id"),
        ("FACT_GL_ENTRIES", "account_id",     "DIM_ACCOUNT",     "account_id"),
        ("FACT_GL_ENTRIES", "scenario_id",    "DIM_SCENARIO",    "scenario_id"),
        ("FACT_GL_ENTRIES", "product_line_id","DIM_PRODUCT_LINE","product_line_id"),
        ("FACT_OPERATIONAL","cost_centre_id", "DIM_COST_CENTRE", "cost_centre_id"),
    ]

    total_orphans = 0
    for fact_table, fk_col, dim_table, pk_col in checks:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {fact_table}
            WHERE {fk_col} NOT IN (SELECT {pk_col} FROM {dim_table})
        """)
        orphan_count = cursor.fetchone()[0]
        total_orphans += orphan_count

    passed = total_orphans == 0
    results.append({
        "check_id": 2,
        "check_name": "Referential Integrity Check",
        "description": "All foreign keys point to valid dimension records",
        "passed": passed,
        "detail": f"Orphaned records found: {total_orphans}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 2 — Referential Integrity: {status}")
    print(f"  Detail: {total_orphans} orphaned foreign key records found")


# ============================================================
# CHECK 3 — PERIOD COVERAGE CHECK
# Every month in our date range must have financial data
# Missing months would create gaps in the P&L report
# ============================================================

def check_period_coverage():
    cursor.execute("""
        SELECT COUNT(DISTINCT fiscal_period)
        FROM FACT_GL_ENTRIES
        WHERE entry_type = 'ACTUAL'
    """)
    actual_periods = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT fiscal_period)
        FROM FACT_GL_ENTRIES
        WHERE entry_type = 'BUDGET'
    """)
    budget_periods = cursor.fetchone()[0]

    # We expect 18 months: Jan 2024 to Jun 2025
    expected_periods = 18
    passed = (actual_periods >= expected_periods and
              budget_periods >= expected_periods)

    results.append({
        "check_id": 3,
        "check_name": "Period Coverage Check",
        "description": "All 18 months have both Actual and Budget data",
        "passed": passed,
        "detail": f"Actual periods: {actual_periods}, Budget periods: {budget_periods}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 3 — Period Coverage: {status}")
    print(f"  Detail: {actual_periods} actual periods, {budget_periods} budget periods")
    print(f"  Expected: {expected_periods} periods minimum")


# ============================================================
# CHECK 4 — BUDGET COMPLETENESS CHECK
# Every cost centre must have budget data
# A cost centre with no budget cannot be measured
# ============================================================

def check_budget_completeness():
    cursor.execute("""
        SELECT COUNT(DISTINCT cost_centre_id)
        FROM FACT_GL_ENTRIES
        WHERE scenario_id = 2
    """)
    cc_with_budget = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM DIM_COST_CENTRE")
    total_cc = cursor.fetchone()[0]

    passed = cc_with_budget == total_cc
    results.append({
        "check_id": 4,
        "check_name": "Budget Completeness Check",
        "description": "All cost centres have budget data assigned",
        "passed": passed,
        "detail": f"{cc_with_budget} of {total_cc} cost centres have budget"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 4 — Budget Completeness: {status}")
    print(f"  Detail: {cc_with_budget} of {total_cc} cost centres have budget data")


# ============================================================
# CHECK 5 — DUPLICATE KEY CHECK
# No two budget entries should exist for the same
# cost centre + account + period combination
# Duplicates would double-count costs in the P&L
# ============================================================

def check_duplicates():
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT f.cost_centre_id, f.account_id, f.fiscal_period,
                   f.scenario_id, f.date_id, COUNT(*) as cnt
            FROM FACT_GL_ENTRIES f
            GROUP BY f.cost_centre_id, f.account_id, f.fiscal_period,
                     f.scenario_id, f.date_id
            HAVING COUNT(*) > 1
        )
    """)
    duplicate_count = cursor.fetchone()[0]

    passed = duplicate_count == 0
    results.append({
        "check_id": 5,
        "check_name": "Duplicate Key Check",
        "description": "No duplicate cost centre + account + period combinations",
        "passed": passed,
        "detail": f"Duplicate combinations found: {duplicate_count}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 5 — Duplicate Key Check: {status}")
    print(f"  Detail: {duplicate_count} duplicate combinations found")


# ============================================================
# CHECK 6 — REVENUE POSITIVE CHECK
# All revenue entries must be positive numbers
# A negative revenue entry indicates a data error
# ============================================================

def check_revenue_positive():
    cursor.execute("""
        SELECT COUNT(*)
        FROM FACT_GL_ENTRIES f
        JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
        WHERE a.is_revenue = 1
        AND f.amount <= 0
        AND f.entry_type = 'ACTUAL'
    """)
    negative_revenue = cursor.fetchone()[0]

    passed = negative_revenue == 0
    results.append({
        "check_id": 6,
        "check_name": "Revenue Positive Check",
        "description": "All actual revenue entries are positive values",
        "passed": passed,
        "detail": f"Negative revenue entries found: {negative_revenue}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 6 — Revenue Positive Check: {status}")
    print(f"  Detail: {negative_revenue} negative revenue entries found")


# ============================================================
# CHECK 7 — DATE RANGE INTEGRITY CHECK
# All dates must fall within our expected range
# Jan 2024 to Jun 2025
# Out of range dates indicate a data loading error
# ============================================================

def check_date_range():
    cursor.execute("""
        SELECT COUNT(*)
        FROM FACT_GL_ENTRIES f
        JOIN DIM_DATE d ON f.date_id = d.date_id
        WHERE d.full_date < '2024-01-01'
        OR d.full_date > '2025-06-30'
    """)
    out_of_range = cursor.fetchone()[0]

    passed = out_of_range == 0
    results.append({
        "check_id": 7,
        "check_name": "Date Range Integrity Check",
        "description": "All entries fall within Jan 2024 to Jun 2025",
        "passed": passed,
        "detail": f"Out of range entries: {out_of_range}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 7 — Date Range Integrity: {status}")
    print(f"  Detail: {out_of_range} entries outside expected date range")


# ============================================================
# CHECK 8 — SIGNAL LOG INTEGRITY CHECK
# Every signal must have days_saved > 0
# A signal that saves zero days is meaningless
# Also checks that detected date is before traditional date
# ============================================================

def check_signal_integrity():
    cursor.execute("""
        SELECT COUNT(*)
        FROM FACT_SIGNAL_LOG
        WHERE days_saved <= 0
    """)
    invalid_signals = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM FACT_SIGNAL_LOG
        WHERE detected_date_id >= traditional_report_date_id
    """)
    wrong_order = cursor.fetchone()[0]

    total_issues = invalid_signals + wrong_order
    passed = total_issues == 0

    results.append({
        "check_id": 8,
        "check_name": "Signal Log Integrity Check",
        "description": "All signals detected before traditional report date",
        "passed": passed,
        "detail": f"Invalid signals: {invalid_signals}, Wrong order: {wrong_order}"
    })
    status = "PASS ✓" if passed else "FAIL ✗"
    print(f"\nCHECK 8 — Signal Log Integrity: {status}")
    print(f"  Detail: {invalid_signals} invalid signals, {wrong_order} wrong order")


# ============================================================
# RUN ALL CHECKS
# ============================================================

check_nulls()
check_referential_integrity()
check_period_coverage()
check_budget_completeness()
check_duplicates()
check_revenue_positive()
check_date_range()
check_signal_integrity()


# ============================================================
# SCORECARD SUMMARY
# ============================================================

passed_checks = sum(1 for r in results if r["passed"])
total_checks = len(results)
score_pct = (passed_checks / total_checks) * 100

print("\n" + "=" * 55)
print("DATA QUALITY SCORECARD SUMMARY")
print("=" * 55)
print(f"Checks Passed:  {passed_checks} of {total_checks}")
print(f"Quality Score:  {score_pct:.0f}%")
print(f"Status:         {'ALL CHECKS PASSED ✓' if score_pct == 100 else 'ISSUES FOUND — REVIEW ABOVE'}")
print("=" * 55)

# Save scorecard to JSON file
scorecard = {
    "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "database": DB_PATH,
    "total_checks": total_checks,
    "passed_checks": passed_checks,
    "quality_score_pct": score_pct,
    "status": "PASSED" if score_pct == 100 else "FAILED",
    "checks": results
}

with open(DQ_SCORECARD_PATH, "w") as f:
    json.dump(scorecard, f, indent=2)

print(f"\nScorecard saved to: data/processed/dq_scorecard.json")

conn.close()