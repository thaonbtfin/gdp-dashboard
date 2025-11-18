"""
Download Workflow Script

This script runs the CafeF download workflow.
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.portfolio_loader_csv import get_portfolios_csv as get_portfolios
from src.tastock.data.data_downloader import DataWorkflowDownload

def main():
    """Main function"""
    workflow = DataWorkflowDownload()
    
    # Load portfolios from Google Sheets
    print("\n=== PORTFOLIO SOURCE CHECK ===")
    portfolios_dict = get_portfolios()
    
    # Check if portfolios loaded successfully from Google Sheets
    try:
        from src.constants import PORTFOLIOS
        if portfolios_dict == PORTFOLIOS:
            print("📁 PORTFOLIOS SOURCE: CONSTANTS (fallback)")
        else:
            print("📊 PORTFOLIOS SOURCE: GOOGLE SHEETS")
    except ImportError:
        from constants import PORTFOLIOS
        if portfolios_dict == PORTFOLIOS:
            print("📁 PORTFOLIOS SOURCE: CONSTANTS (fallback)")
        else:
            print("📊 PORTFOLIOS SOURCE: GOOGLE SHEETS")
    
    print(f"📋 Loaded {len(portfolios_dict)} portfolios: {list(portfolios_dict.keys())}")
    
    # Show portfolio details for debugging
    for name, symbols in portfolios_dict.items():
        print(f"  📁 {name}: {len(symbols)} symbols")
    print("=" * 35)
    
    # Run workflow for all portfolios
    for portfolio_name, symbols in portfolios_dict.items():
        if symbols:  # Skip empty portfolios
            workflow.run_full_workflow(symbols=symbols, portfolio_name=portfolio_name)
    
    # Merge all portfolios data to root files
    print("\n=== Merging all portfolios data to root ===")
    workflow.merge_all_portfolios_to_root()
    workflow.merge_all_portfolios_perf_to_root()
    
    # After the merge operations
    workflow.copy_history_to_root()

    # Keep 3 date folders and Cleanup others
    workflow.cleanup_old_date_folders()

    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", symbols=SYMBOLS_VN100, portfolio_name='VN100')

if __name__ == "__main__":
    main()