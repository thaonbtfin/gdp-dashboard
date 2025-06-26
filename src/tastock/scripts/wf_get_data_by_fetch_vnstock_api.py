"""
Fetch Workflow Script

This script runs the API fetch workflow.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_VN30
from src.tastock.data.workflow_fetcher import DataWorkflowFetch

def main():
    """Main function"""
    workflow = DataWorkflowFetch()
    
    # Run workflow for single portfolio
    workflow.run_full_workflow('VN30', SYMBOLS_VN30)
    
    # Uncomment to run for multiple portfolios
    # workflow.run_multiple_portfolios()
    
    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", 'VN30', SYMBOLS_VN30)

if __name__ == "__main__":
    main()