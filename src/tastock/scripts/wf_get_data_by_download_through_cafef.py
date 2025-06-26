"""
Download Workflow Script

This script runs the CafeF download workflow.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_VN100
from src.tastock.data.data_downloader import DataWorkflowDownload

def main():
    """Main function"""
    workflow = DataWorkflowDownload()
    
    # Run workflow once
    workflow.run_full_workflow(symbols=SYMBOLS_VN100, portfolio_name='VN100')
    
    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", symbols=SYMBOLS_VN100, portfolio_name='VN100')

if __name__ == "__main__":
    main()