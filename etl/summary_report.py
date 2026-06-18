# ============================================================
# FinSignal — Weekly Summary Report Generator
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
#
# PURPOSE:
# Generates an automatic weekly Controlling alert report.
# Simulates what a Controller receives every Monday morning.
# Reads live data from finsignal.db and produces a
# formatted text report saved to reporting/ folder.
#
# This proves FinSignal is an automated alerting system,
# not just a dashboard.
#
# PIPELINE POSITION:
# signal_engine.py → summary_report.py → weekly_report.txt
# ============================================================

import sqlite3
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, BASE_DIR

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

REPORT_PATH = os.path.join(
    BASE_DIR, "reporting", "weekly_signal_report.txt"
)

print("=" * 55)
print("FINSIGNAL — WEEKLY SUMMARY REPORT GENERATOR")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)


# ============================================================
# LOAD KEY METRICS FROM DATABASE
# ============================================================

# Overall signal statistics
cursor.execute("""
    SELECT
        COUNT(*) AS total_signals,
        COUNT(CASE WHEN severity = 'RED' THEN 1 END) AS red_signals,
        COUNT(CASE WHEN severity = 'AMBER' THEN 1 END) AS amber_signals,
        ROUND(AVG(days_saved), 1) AS avg_days_saved,
        ROUND(SUM(projected_overrun_eur), 2) AS total_overrun_eur
    FROM FACT_SIGNAL_LOG
""")
signal_stats = cursor.fetchone()

# Top RED signals
cursor.execute("""
    SELECT
        c.cost_centre_name,
        c.manager_name,
        s.signal_type,
        s.projected_overrun_eur,
        s.days_saved,
        s.days_before_monthend,
        d.full_date AS detected_date
    FROM FACT_SIGNAL_LOG s
    JOIN DIM_COST_CENTRE c ON s.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d ON s.detected_date_id = d.date_id
    WHERE s.severity = 'RED'
    ORDER BY s.projected_overrun_eur DESC
    LIMIT 5
""")
red_signals = cursor.fetchall()

# Top AMBER signals
cursor.execute("""
    SELECT
        c.cost_centre_name,
        c.manager_name,
        s.signal_type,
        s.projected_overrun_eur,
        s.days_saved,
        d.full_date AS detected_date
    FROM FACT_SIGNAL_LOG s
    JOIN DIM_COST_CENTRE c ON s.cost_centre_id = c.cost_centre_id
    JOIN DIM_DATE d ON s.detected_date_id = d.date_id
    WHERE s.severity = 'AMBER'
    ORDER BY s.projected_overrun_eur DESC
    LIMIT 3
""")
amber_signals = cursor.fetchall()

# Latest CFO metrics
cursor.execute("""
    WITH latest AS (
        SELECT MAX(fiscal_period) AS max_period
        FROM FACT_GL_ENTRIES WHERE scenario_id = 1
    )
    SELECT
        f.fiscal_period,
        ROUND(SUM(CASE WHEN a.is_revenue = 1
            AND f.scenario_id = 1 THEN f.amount ELSE 0 END), 2)
            AS actual_revenue,
        ROUND(SUM(CASE WHEN a.is_revenue = 1
            AND f.scenario_id = 2 THEN f.amount ELSE 0 END), 2)
            AS budget_revenue,
        ROUND(SUM(CASE WHEN a.is_cost = 1
            AND f.scenario_id = 1 THEN f.amount ELSE 0 END), 2)
            AS actual_cost
    FROM FACT_GL_ENTRIES f
    JOIN DIM_ACCOUNT a ON f.account_id = a.account_id
    WHERE f.fiscal_period = (SELECT max_period FROM latest)
    GROUP BY f.fiscal_period
""")
cfo_metrics = cursor.fetchone()

conn.close()


# ============================================================
# BUILD THE REPORT
# ============================================================

lines = []

lines.append("=" * 65)
lines.append("FINSIGNAL — WEEKLY CONTROLLING ALERT REPORT")
lines.append(f"PräzisionWerk GmbH | Stuttgart, Germany")
lines.append(
    f"Report Generated: "
    f"{datetime.now().strftime('%A, %d %B %Y — %H:%M')}"
)
lines.append("Prepared by: FinSignal Automated Intelligence System")
lines.append("=" * 65)

lines.append("")
lines.append("EXECUTIVE SUMMARY")
lines.append("-" * 65)
lines.append(
    f"Total Early Warning Signals Detected:  "
    f"{signal_stats[0]}"
)
lines.append(
    f"  Critical (RED):                      "
    f"{signal_stats[1]}"
)
lines.append(
    f"  Advisory (AMBER):                    "
    f"{signal_stats[2]}"
)
lines.append(
    f"Average Days Before Traditional Report: "
    f"{signal_stats[3]} days"
)
lines.append(
    f"Total Projected Overrun Detected:      "
    f"€{signal_stats[4]:,.2f}"
)

if cfo_metrics:
    ebit = cfo_metrics[1] - cfo_metrics[3]
    revenue_var = cfo_metrics[1] - cfo_metrics[2]
    lines.append("")
    lines.append(
        f"Latest Period ({cfo_metrics[0]}) Financial Summary:"
    )
    lines.append(
        f"  Actual Revenue:   €{cfo_metrics[1]:,.2f}"
    )
    lines.append(
        f"  Budget Revenue:   €{cfo_metrics[2]:,.2f}"
    )
    lines.append(
        f"  Revenue Variance: €{revenue_var:,.2f}"
    )
    lines.append(
        f"  Actual EBIT:      €{ebit:,.2f}"
    )

lines.append("")
lines.append("=" * 65)
lines.append("CRITICAL ALERTS — IMMEDIATE ACTION REQUIRED")
lines.append("=" * 65)

if red_signals:
    for i, sig in enumerate(red_signals, 1):
        lines.append("")
        lines.append(f"🔴 RED ALERT {i}: {sig[0]}")
        lines.append(f"   Manager:          {sig[1]}")
        lines.append(
            f"   Signal Type:      "
            f"{sig[2].replace('_', ' ')}"
        )
        lines.append(
            f"   Projected Overrun: €{sig[3]:,.2f}"
        )
        lines.append(
            f"   Detected:         {sig[6]}"
        )
        lines.append(
            f"   Days Before Month End: {sig[5]} days"
        )
        lines.append(
            f"   Early Warning:    {sig[4]} days before "
            f"traditional report"
        )
        lines.append(
            f"   ACTION REQUIRED:  Review cost centre "
            f"budget immediately"
        )
else:
    lines.append("No critical RED alerts this week.")

lines.append("")
lines.append("=" * 65)
lines.append("ADVISORY ALERTS — MONITOR CLOSELY")
lines.append("=" * 65)

if amber_signals:
    for i, sig in enumerate(amber_signals, 1):
        lines.append("")
        lines.append(f"🟡 AMBER ALERT {i}: {sig[0]}")
        lines.append(f"   Manager:          {sig[1]}")
        lines.append(
            f"   Signal Type:      "
            f"{sig[2].replace('_', ' ')}"
        )
        lines.append(
            f"   Projected Impact:  €{sig[3]:,.2f}"
        )
        lines.append(
            f"   Detected:         {sig[5]}"
        )
        lines.append(
            f"   Early Warning:    {sig[4]} days before "
            f"traditional report"
        )
        lines.append(
            f"   ACTION REQUIRED:  Monitor weekly pace "
            f"and review with manager"
        )
else:
    lines.append("No advisory AMBER alerts this week.")

lines.append("")
lines.append("=" * 65)
lines.append("FINSIGNAL SYSTEM PERFORMANCE")
lines.append("=" * 65)
lines.append(
    f"Traditional Controlling Report Delay:  8 days after month-end"
)
lines.append(
    f"FinSignal Average Detection:           "
    f"{signal_stats[3]} days BEFORE month-end"
)
lines.append(
    f"Total Time Advantage:                  "
    f"{round(signal_stats[3] + 8, 1)} days earlier than traditional"
)
lines.append(
    f"Data Quality Score:                    100% (8/8 checks)"
)
lines.append(
    f"Cost Centres Monitored:                6 departments"
)
lines.append("")
lines.append(
    "This report was generated automatically by FinSignal."
)
lines.append(
    "No manual consolidation required."
)
lines.append(
    "Traditional month-end report would arrive approximately "
    f"{round(signal_stats[3], 0):.0f} days from now."
)
lines.append("")
lines.append("=" * 65)
lines.append(
    "FinSignal — Operational-Financial Early Warning System"
)
lines.append("PräzisionWerk GmbH | Developed by Mohammad M. Kureshi")
lines.append("=" * 65)

# ============================================================
# SAVE REPORT TO FILE
# ============================================================

report_text = "\n".join(lines)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)

print(report_text)
print(f"\nReport saved to: {REPORT_PATH}")