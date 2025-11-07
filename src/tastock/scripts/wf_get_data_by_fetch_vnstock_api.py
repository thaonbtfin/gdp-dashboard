"""
Fetch Workflow Script

This script runs the API fetch workflow.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_BIZUNI_NOW, SYMBOLS_VN100, SYMBOLS_VN30, SYMBOLS_DH, SYMBOLS_TH
from src.tastock.data.workflow_fetcher import DataWorkflowFetch

def main():
    """Main function"""
    workflow = DataWorkflowFetch()

    # Run workflow for all portfolios
    portfolios = [
        # (SYMBOLS_BIZUNI_NOW, 'BizUni_Now'),
        # (SYMBOLS_VN100, 'VN100'),
        (SYMBOLS_VN30, 'VN30')
        # (SYMBOLS_DH, 'DH'),
        # (SYMBOLS_TH, 'TH')
    ]
    
    # Run workflow for single portfolio
    for symbols, portfolio_name in portfolios:
        workflow.run_full_workflow(symbols=symbols, portfolio_name=portfolio_name)
    
    # Uncomment to run for multiple portfolios
    # workflow.run_multiple_portfolios()
    
    # After processing all portfolios
    workflow.copy_history_to_root()

    # Keep 3 date folders and Cleanup others
    workflow.cleanup_old_date_folders()

    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", 'VN30', SYMBOLS_VN30)

if __name__ == "__main__":
    main()