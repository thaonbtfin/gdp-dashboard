#!/usr/bin/env python3
"""
Stock Data Updater

Executes the complete stock data update workflow:
1. CafeF Data Collection - Download latest stock data
2. Performance Analysis - Calculate historical metrics
3. Investment Signals - Generate trading recommendations
4. Market Data Enhancement - Fetch additional insights
"""

import subprocess
import sys
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_script(script_path, description):
    """Execute a Python script and handle errors"""
    logging.info(f"▶️ Starting: {description}")
    logging.info(f"Executing: {script_path}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, check=True)
        logging.info(f"✅ Completed: {description}")
        if result.stdout:
            logging.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed: {description}")
        logging.error(f"Error: {e.stderr}")
        return False

def main():
    """Execute the complete data pipeline workflow"""
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("▶▶▶ STARTING STOCK DATA UPDATE WORKFLOW")
    logging.info("=" * 60)
    
    # Define script paths relative to tastock directory
    tastock_path = os.path.dirname(os.path.dirname(__file__))
    
    scripts = [
        {
            'path': os.path.join(tastock_path, 'scripts/crawl_cafef_data_and_save_portfolios_to_root_data_folder.py'),
            'description': 'CafeF Data Crawler - Download stock data from CafeF'
        },
        {
            'path': os.path.join(tastock_path, 'scripts/calculate_from_history.py'),
            'description': 'Calculate from History - Process historical performance data'
        },
        {
            'path': os.path.join(tastock_path, 'scripts/generate_investment_signals.py'),
            'description': 'Generate Investment Signals - Create trading recommendations'
        },
        {
            'path': os.path.join(tastock_path, 'scripts/generate_intrinsic_values.py'),
            'description': 'Generate Intrinsic Values - Calculate stock valuations'
        },
        {
            'path': os.path.join(tastock_path, 'crawlers/bizuni_crawler.py'),
            'description': 'BizUni Crawler - Fetch additional market data'
        }
    ]
    
    # Execute scripts in sequence
    success_count = 0
    for i, script in enumerate(scripts, 1):
        logging.info(f"\n[STEP {i}/5] {script['description']}")
        logging.info("-" * 50)
        
        if not os.path.exists(script['path']):
            logging.error(f"Script not found: {script['path']}")
            continue
            
        if run_script(script['path'], script['description']):
            success_count += 1
        else:
            logging.error(f"Pipeline failed at step {i}")
            break
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logging.info("\n" + "=" * 60)
    logging.info("💯 WORKFLOW EXECUTION SUMMARY")
    logging.info("=" * 60)
    logging.info(f"Total scripts: {len(scripts)}")
    logging.info(f"Successful: {success_count}")
    logging.info(f"Failed: {len(scripts) - success_count}")
    logging.info(f"Duration: {duration}")
    
    if success_count == len(scripts):
        logging.info("✅ All scripts completed successfully!")
        return 0
    else:
        logging.error("❌ Some scripts failed. Check logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())