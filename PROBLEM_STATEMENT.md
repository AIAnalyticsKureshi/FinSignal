# FinSignal — Business Problem Statement

## Company Context

**Company:** PräzisionWerk GmbH  
**Industry:** Precision Manufacturing (Automotive Supply Chain)  
**Size:** 220 employees, €45M annual revenue  
**Location:** Stuttgart, Germany  
**ERP System:** SAP (financial data) + Excel (operational tracking)

---

## Current Situation

PräzisionWerk GmbH operates six cost centres: Sales, Manufacturing, Logistics,
R&D, Administration, and Finance. Each department tracks its operational activity
in separate Excel files. The Finance Controlling team consolidates these files
manually every month to produce the Management Report.

The monthly Controlling report is delivered to the CFO on day 8 after month-end.

---

## The Core Problem

**By the time the Controller sees a budget overrun, the money is already spent.**

The current process is purely backward-looking. It reports what happened last
month. It cannot detect what is about to happen this month.

Specific pain points:

1. **Late visibility** — A cost overrun in Manufacturing becomes visible on
   February 8th for January's performance. The overrun happened in week 2 of
   January. Nobody saw it for 5 weeks.

2. **Disconnected data** — Operational data (production orders, material
   consumption, headcount hours) and financial data (budget, actuals) live in
   completely separate files with no automatic link between them.

3. **No early warning** — There is no mechanism to detect that Manufacturing is
   consuming materials at 140% of the planned pace in week 2 — which will
   mathematically result in a 40% budget overrun by month-end.

4. **Manual consolidation** — The Controller spends 4-5 days every month
   copying, cleaning, and merging Excel files before any analysis can begin.

5. **Reactive decisions** — Leadership receives information too late to take
   corrective action within the same financial period.

---

## The Consequence

In Q1 2025, Manufacturing exceeded its cost budget by €320,000. This overrun
was visible in the February Controlling report. The signal that this overrun
was developing was present in operational data as early as January 14th —
25 days before anyone saw it.

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

5. A written Controlling Memo is auto-generated with quantified findings
   and specific recommended actions for leadership.

---

## Success Metrics

| Metric | Target |
|---|---|
| Early warning lead time | Minimum 3 weeks before month-end close |
| Manual consolidation time | Reduced from 5 days to under 4 hours |
| Data quality score | 100% across 8 automated checks |
| Cost centres monitored | 6 departments, real-time |
| Scenarios modelled | 3 (Base / Optimistic / Pessimistic) |

---

## Why This Gap Exists

Large enterprises buy Anaplan, Workday Adaptive Planning, or OneStream to
solve this problem. These platforms cost €50,000–€200,000 per year.

The German Mittelstand cannot afford these platforms. They have SAP for
transactions and Excel for everything else. The gap between these two tools
is exactly where FinSignal operates.

---

*Document version: 1.0 | Author: Mohammad M. Kureshi | Project: FinSignal*