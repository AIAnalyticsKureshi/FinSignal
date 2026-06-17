# ============================================================
# FinSignal — Central Configuration File
# Project: Operational-Financial Early Warning System
# Author: Mohammad M. Kureshi
#
# PURPOSE:
# All project settings live here in one place.
# Every other Python script imports from this file.
# If anything changes (database path, date range, thresholds)
# you change it here ONCE and everything updates automatically.
# This is standard professional Python project structure.
# ============================================================

from datetime import date
import os

# ============================================================
# DATABASE SETTINGS
# ============================================================

# Path to the SQLite database file
# os.path.join builds the correct path for any operating system
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "finsignal.db")

# ============================================================
# DATE RANGE SETTINGS
# ============================================================

# Start and end of our data period
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 6, 30)

# The date format used throughout the project
DATE_FORMAT = "%Y-%m-%d"

# ============================================================
# COMPANY SETTINGS
# ============================================================

COMPANY_NAME = "PräzisionWerk GmbH"
COMPANY_LOCATION = "Stuttgart, Germany"
COMPANY_REVENUE_TARGET = 45_000_000  # €45 million annual revenue
REPORTING_CURRENCY = "EUR"

# ============================================================
# SIGNAL DETECTION THRESHOLDS
# These define when FinSignal fires a warning
# ============================================================

# If actual pace exceeds budget pace by this percentage, fire AMBER
AMBER_THRESHOLD_PCT = 0.10   # 10% over budget pace

# If actual pace exceeds budget pace by this percentage, fire RED
RED_THRESHOLD_PCT = 0.20     # 20% over budget pace

# Minimum days before month end to consider a signal meaningful
MIN_DAYS_FOR_SIGNAL = 5

# ============================================================
# DATA QUALITY SETTINGS
# ============================================================

# Minimum quality score to consider data trustworthy
MIN_QUALITY_SCORE = 100.0

# Path to save the DQ scorecard
DQ_SCORECARD_PATH = os.path.join(BASE_DIR, "data", "processed", "dq_scorecard.json")

# ============================================================
# REPORTING SETTINGS
# ============================================================

# Path to save the Controlling Memo PDF
MEMO_OUTPUT_PATH = os.path.join(BASE_DIR, "reporting", "controlling_memo.pdf")

# Path to save the architecture diagram
ARCHITECTURE_DIAGRAM_PATH = os.path.join(BASE_DIR, "docs", "architecture.png")

# ============================================================
# COST CENTRE IDs
# Reference these by name instead of numbers in your scripts
# Much easier to read and maintain
# ============================================================

CC_MANUFACTURING = 1
CC_SALES = 2
CC_LOGISTICS = 3
CC_RD = 4
CC_ADMINISTRATION = 5
CC_FINANCE = 6

# ============================================================
# SCENARIO IDs
# ============================================================

SCENARIO_ACTUAL = 1
SCENARIO_BUDGET = 2
SCENARIO_FORECAST = 3

# ============================================================
# RANDOM SEED
# Ensures data is identical every time you regenerate
# ============================================================

RANDOM_SEED = 42