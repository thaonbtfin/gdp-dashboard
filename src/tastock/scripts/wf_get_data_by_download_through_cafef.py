"""
Download Workflow Script

This script runs the CafeF download workflow.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_VN100, SYMBOLS_VN30, SYMBOLS_DH, SYMBOLS_TH
from src.tastock.data.data_downloader import DataWorkflowDownload

def main():
    """Main function"""
    workflow = DataWorkflowDownload()
    
    # Run workflow for all portfolios
    portfolios = [
        (SYMBOLS_VN100, 'VN100'),
        (SYMBOLS_VN30, 'VN30'),
        (SYMBOLS_DH, 'DH'),
        (SYMBOLS_TH, 'TH')
    ]
    
    for symbols, portfolio_name in portfolios:
        workflow.run_full_workflow(symbols=symbols, portfolio_name=portfolio_name)
    
    # Merge all portfolios data to root files
    print("\n=== Merging all portfolios data to root ===")
    workflow.merge_all_portfolios_to_root()
    workflow.merge_all_portfolios_perf_to_root()
    
    # After the merge operations
    workflow.copy_history_to_root()

    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", symbols=SYMBOLS_VN100, portfolio_name='VN100')

if __name__ == "__main__":
    main()