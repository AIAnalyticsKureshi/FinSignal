# ============================================================
# FinSignal — Signal Detection Engine
# Project: Operational-Financial Early Warning System
# Company: PräzisionWerk GmbH, Stuttgart
# Author: Mohammad M. Kureshi
#
# PURPOSE:
# This is the HEART of FinSignal.
# It reads weekly operational data from FACT_OPERATIONAL,
# calculates the consumption pace vs budget for each
# cost centre, projects the month-end financial outcome,
# and automatically inserts early warning signals into
# FACT_SIGNAL_LOG.
#
# This replaces manually typed signals with real,
# calculated, data-driven alerts.
#
# LOGIC:
# 1. For each cost centre, read weekly operational data
# 2. Calculate pace = actual consumption / budget consumption
# 3. Project month-end outcome = pace * monthly budget
# 4. If projection exceeds threshold, fire a signal
# 5. Calculate days_saved vs traditional report date
#
# PIPELINE POSITION:
# generate_data.py → transform.py → signal_engine.py
# ============================================================

import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (DB_PATH, AMBER_THRESHOLD_PCT, RED_THRESHOLD_PCT,
                    CC_MANUFACTURING, CC_SALES, CC_LOGISTICS, CC_RD)

conn = sqlite3.connect(DB_PATH)

print("=" * 55)
print("FINSIGNAL — SIGNAL DETECTION ENGINE")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Amber threshold: >{AMBER_THRESHOLD_PCT*100:.0f}% of budget pace")
print(f"Red threshold:   >{RED_THRESHOLD_PCT*100:.0f}% of budget pace")
print("=" * 55)


# ============================================================
# STEP 1 — CLEAR EXISTING SIGNALS
# We recalculate all signals fresh every time this runs
# This ensures signals are always based on latest data
# ============================================================

conn.execute("DELETE FROM FACT_SIGNAL_LOG")
conn.commit()
print("\nCleared existing signals. Recalculating...")


# ============================================================
# STEP 2 — LOAD OPERATIONAL DATA
# Read weekly operational records with date information
# ============================================================

operational_query = """
    SELECT
        o.op_id,
        o.date_id,
        d.full_date,
        d.week_number,
        d.month_number,
        d.fiscal_year,
        o.cost_centre_id,
        c.cost_centre_name,
        o.material_consumed_kg,
        o.material_budget_kg,
        o.production_hours_actual,
        o.production_hours_budget,
        o.purchase_orders_placed,
        o.purchase_orders_budget,
        o.headcount_active,
        o.headcount_budget
    FROM FACT_OPERATIONAL o
    JOIN DIM_DATE d ON o.date_id = d.date_id
    JOIN DIM_COST_CENTRE c ON o.cost_centre_id = c.cost_centre_id
    ORDER BY d.full_date, o.cost_centre_id
"""

df_op = pd.read_sql_query(operational_query, conn)
print(f"\nLoaded {len(df_op)} operational records")


# ============================================================
# STEP 3 — LOAD FINANCIAL BUDGET DATA
# Get monthly budget amounts per cost centre
# We need this to calculate projected financial overrun in EUR
# ============================================================

budget_query = """
    SELECT
        f.cost_centre_id,
        f.fiscal_period,
        SUM(f.amount) as total_budget_eur
    FROM FACT_GL_ENTRIES f
    WHERE f.scenario_id = 2
    AND f.entry_type = 'BUDGET'
    GROUP BY f.cost_centre_id, f.fiscal_period
"""

df_budget = pd.read_sql_query(budget_query, conn)


# ============================================================
# STEP 4 — SIGNAL DETECTION LOGIC
# For each cost centre, for each week:
# Calculate pace and project month-end outcome
# ============================================================

signals = []
signal_id = 1

# Group operational data by year, month, cost centre
grouped = df_op.groupby(
    ["fiscal_year", "month_number", "cost_centre_id", "cost_centre_name"]
)

for (year, month, cc_id, cc_name), group in grouped:

    # Sort by date to process week by week
    group = group.sort_values("full_date")

    # Get cumulative consumption week by week
    for i, (_, week_row) in enumerate(group.iterrows()):

        week_num = i + 1  # Which week of the month (1,2,3,4)
        weeks_remaining = 4 - week_num

        # Skip last week — no time to act
        if weeks_remaining == 0:
            continue

        # ------------------------------------------------
        # MATERIAL CONSUMPTION SIGNAL
        # Only relevant for cost centres that use materials
        # ------------------------------------------------
        if week_row["material_budget_kg"] > 0:

            # Pace = how fast are we consuming vs budget
            material_pace = (
                week_row["material_consumed_kg"] /
                week_row["material_budget_kg"]
            )

            # Project: if we continue at this pace for full month
            projected_pace = material_pace

            # Determine severity
            severity = None
            if projected_pace > (1 + RED_THRESHOLD_PCT):
                severity = "RED"
            elif projected_pace > (1 + AMBER_THRESHOLD_PCT):
                severity = "AMBER"

            if severity:
                # Calculate projected overrun in EUR
                fiscal_period = f"{year}-{month:02d}"
                budget_eur = df_budget[
                    (df_budget["cost_centre_id"] == cc_id) &
                    (df_budget["fiscal_period"] == fiscal_period)
                ]["total_budget_eur"].sum()

                projected_overrun_eur = budget_eur * (projected_pace - 1)

                # Calculate days saved vs traditional report
                # Traditional report comes on day 8 of next month
                if month == 12:
                    trad_report_date = date(year + 1, 1, 8)
                else:
                    trad_report_date = date(year, month + 1, 8)

                # Detection date is the Monday of this week
                detection_date = pd.to_datetime(
                    week_row["full_date"]
                ).date()

                days_saved = (trad_report_date - detection_date).days

                # Last day of the month
                if month == 12:
                    last_day = date(year, 12, 31)
                else:
                    last_day = date(year, month + 1, 1) - __import__('datetime').timedelta(days=1)

                days_before_monthend = (last_day - detection_date).days

                # Convert dates to date_id format (YYYYMMDD)
                detected_date_id = int(
                    detection_date.strftime("%Y%m%d")
                )
                trad_date_id = int(
                    trad_report_date.strftime("%Y%m%d")
                )

                signals.append({
                    "signal_id": signal_id,
                    "detected_date_id": detected_date_id,
                    "cost_centre_id": cc_id,
                    "signal_type": "MATERIAL_COST_OVERRUN",
                    "projected_overrun_eur": round(
                        projected_overrun_eur, 2
                    ),
                    "days_before_monthend": days_before_monthend,
                    "threshold_breached": (
                        f"MATERIAL_PACE > "
                        f"{(1+RED_THRESHOLD_PCT)*100:.0f}%"
                        if severity == "RED"
                        else f"MATERIAL_PACE > "
                        f"{(1+AMBER_THRESHOLD_PCT)*100:.0f}%"
                    ),
                    "severity": severity,
                    "traditional_report_date_id": trad_date_id,
                    "days_saved": days_saved,
                    "signal_status": "CONFIRMED"
                })
                signal_id += 1

        # ------------------------------------------------
        # PRODUCTION HOURS SIGNAL
        # Detects underspend (project delays) and overspend
        # ------------------------------------------------
        if week_row["production_hours_budget"] > 0:

            hours_pace = (
                week_row["production_hours_actual"] /
                week_row["production_hours_budget"]
            )

            severity = None

            # Underspend — R&D project delays
            if hours_pace < (1 - RED_THRESHOLD_PCT):
                severity = "AMBER"
                signal_type = "HOURS_UNDERSPEND"
            # Overspend
            elif hours_pace > (1 + RED_THRESHOLD_PCT):
                severity = "RED"
                signal_type = "HOURS_OVERSPEND"

            if severity:
                fiscal_period = f"{year}-{month:02d}"
                budget_eur = df_budget[
                    (df_budget["cost_centre_id"] == cc_id) &
                    (df_budget["fiscal_period"] == fiscal_period)
                ]["total_budget_eur"].sum()

                projected_overrun_eur = budget_eur * abs(
                    hours_pace - 1
                )

                if month == 12:
                    trad_report_date = date(year + 1, 1, 8)
                else:
                    trad_report_date = date(year, month + 1, 8)

                detection_date = pd.to_datetime(
                    week_row["full_date"]
                ).date()

                days_saved = (trad_report_date - detection_date).days

                if month == 12:
                    last_day = date(year, 12, 31)
                else:
                    last_day = date(year, month + 1, 1) - __import__('datetime').timedelta(days=1)

                days_before_monthend = (
                    last_day - detection_date
                ).days

                detected_date_id = int(
                    detection_date.strftime("%Y%m%d")
                )
                trad_date_id = int(
                    trad_report_date.strftime("%Y%m%d")
                )

                signals.append({
                    "signal_id": signal_id,
                    "detected_date_id": detected_date_id,
                    "cost_centre_id": cc_id,
                    "signal_type": signal_type,
                    "projected_overrun_eur": round(
                        projected_overrun_eur, 2
                    ),
                    "days_before_monthend": days_before_monthend,
                    "threshold_breached": (
                        f"HOURS_PACE < "
                        f"{(1-RED_THRESHOLD_PCT)*100:.0f}%"
                        if "UNDER" in signal_type
                        else f"HOURS_PACE > "
                        f"{(1+RED_THRESHOLD_PCT)*100:.0f}%"
                    ),
                    "severity": severity,
                    "traditional_report_date_id": trad_date_id,
                    "days_saved": days_saved,
                    "signal_status": "CONFIRMED"
                })
                signal_id += 1


# ============================================================
# STEP 5 — INSERT SIGNALS INTO DATABASE
# ============================================================

if signals:
    df_signals = pd.DataFrame(signals)
    df_signals.to_sql(
        "FACT_SIGNAL_LOG", conn,
        if_exists="replace", index=False
    )
    print(f"\nSignals detected and inserted: {len(signals)}")

    # Summary by severity
    red_count = len(
        [s for s in signals if s["severity"] == "RED"]
    )
    amber_count = len(
        [s for s in signals if s["severity"] == "AMBER"]
    )
    print(f"  RED signals:   {red_count}")
    print(f"  AMBER signals: {amber_count}")

    # Average days saved
    avg_days = sum(
        s["days_saved"] for s in signals
    ) / len(signals)
    print(f"  Avg days saved vs traditional report: "
          f"{avg_days:.1f} days")

    # Show top 5 most critical signals
    print("\nTOP 5 MOST CRITICAL SIGNALS:")
    print("-" * 40)
    df_top = df_signals.nlargest(5, "projected_overrun_eur")[
        ["cost_centre_id", "signal_type",
         "severity", "projected_overrun_eur", "days_saved"]
    ]
    for _, row in df_top.iterrows():
        print(f"  CC{row['cost_centre_id']} | "
              f"{row['signal_type']} | "
              f"{row['severity']} | "
              f"€{row['projected_overrun_eur']:,.0f} | "
              f"{row['days_saved']} days saved")

else:
    print("\nNo signals detected above threshold")

conn.commit()
conn.close()

print("\n" + "=" * 55)
print("SIGNAL ENGINE COMPLETE")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Run validate.py to verify data quality")
print("=" * 55)