# FinSignal — Business Problem Statement

## Company Context

**Company:** PräzisionWerk GmbH
**Industry:** Precision Manufacturing (Automotive Supply Chain)
**Size:** ~200 employees, €65M annual revenue
**Location:** Stuttgart, Germany
**ERP System:** SAP (financial data) + Excel (operational tracking)

---

## Current Situation

PräzisionWerk GmbH operates six cost centres: Sales, Manufacturing, Logistics,
R&D, Administration, and Finance & Controlling. Each department tracks its
operational activity in separate Excel files. The Finance Controlling team
consolidates these files manually every month to produce the Management Report.

The monthly Controlling report is delivered to the CFO on day 8 after month-end.

---

## The Core Problem

**By the time the Controller sees a budget overrun, the money is already spent.**

The current process is purely backward-looking. It reports what happened last
month. It cannot detect what is about to happen this month.

Specific pain points:

1. **Late visibility** — A cost overrun in a given cost centre becomes visible
   on day 8 of the following month. The overrun itself happened weeks earlier.
   Nobody saw it develop in real time.

2. **Disconnected data** — Operational data (production orders, material
   consumption, headcount hours) and financial data (budget, actuals) live in
   completely separate files with no automatic link between them.

3. **No early warning** — There is no mechanism to detect that a cost centre is
   consuming materials or hours at a pace that will mathematically result in
   a budget overrun by month-end.

4. **Manual consolidation** — The Controller spends multiple days every month
   copying, cleaning, and merging Excel files before any analysis can begin.

5. **Reactive decisions** — Leadership receives information too late to take
   corrective action within the same financial period.

---

## The Consequence

In Q1 2025, Manufacturing exceeded its cost budget by a projected **€1.32M** —
the largest single cost centre overrun in the dataset, and the anchor example
for FinSignal's detection story. The signal that this overrun was developing
was present in operational data weeks before it would have appeared in the
traditional month-end report.

---

## The Solution: FinSignal

FinSignal is an operational-financial early warning system that connects
operational leading indicators to financial outcomes in real time.

Instead of asking "what happened last month?", FinSignal asks:
**"Based on what is happening this week operationally, what will the
financial result be at month-end — and which cost centres need attention now?"**

---

## How It Works

1. Operational data (production output, material intake, hours logged) is
   extracted weekly from department Excel files via an automated Python pipeline.

2. This operational data is linked to the financial budget in a unified
   SQL database using a shared key structure (cost centre + date + product line).

3. A signal detection engine calculates the projected month-end financial
   outcome based on the current operational pace.

4. A Power BI dashboard surfaces three things:
   - Which cost centres are on track (green)
   - Which are trending toward overrun (amber — act now)
   - Which have already breached their threshold (red — escalate)

5. The underlying model supports Actual, Budget, and Forecast scenarios
   (`ACT` / `BUD` / `FOR`), so projected outcomes can be compared directly
   against both the original budget and a rolling forecast.

---

## Success Metrics

| Metric | Target | Achieved |
|---|---|---|
| Early warning lead time | Minimum 3 weeks before month-end close | **25.6 days average · 37 days maximum** |
| Data quality score | 100% across 8 automated checks | **100%** ✓ |
| Cost centres monitored | 6 departments, real-time | **6** ✓ |
| Manual consolidation time | Reduced from days to hours | Designed to eliminate manual file merging via automated ETL |
| Projected overruns detected early | — | **€2.84M across 6 cost centres** |

---

## Why This Gap Exists

Large enterprises buy Anaplan, Workday Adaptive Planning, or OneStream to
solve this problem. These platforms cost €50,000–€200,000 per year.

The German Mittelstand cannot afford these platforms. They have SAP for
transactions and Excel for everything else. The gap between these two tools
is exactly where FinSignal operates.

---

*Document version: 2.0 | Author: Mohammad M. Kureshi | Project: FinSignal*
