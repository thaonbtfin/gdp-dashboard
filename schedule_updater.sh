#!/bin/bash
# TAstock Data Updater - Automated Scheduler
# Runs weekdays at 6 PM (Monday-Friday)

cd "$(dirname "$0")"
python3 src/tastock/workflows/wf_stock_data_updater.py >> data/scheduler.log 2>&1