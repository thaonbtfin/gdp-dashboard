"""
Download Workflow Script

This script runs the CafeF download workflow.
"""

import os
import sys
import importlib

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.portfolio_loader_csv import get_portfolios_csv as get_portfolios
from src.tastock.data.data_downloader import DataWorkflowDownload

def load_portfolios_prefer_constants():
    """Load portfolios preferring constants.py, fallback to CSV/Google Sheets."""
    for module_name in ("src.constants", "constants"):
        try:
            mod = importlib.import_module(module_name)
            portfolios = getattr(mod, "PORTFOLIOS", None)
            if portfolios:
                return portfolios, "CONSTANTS"
        except Exception:
            # ignore and try next module path
            continue

    # Fallback to CSV/Google Sheets loader
    try:
        portfolios = get_portfolios()
        return portfolios, "GOOGLE SHEETS / CSV"
    except Exception:
        return {}, "FALLBACK_EMPTY"

def main():
    """Main function"""
    workflow = DataWorkflowDownload()

    # Load portfolios with preference for constants
    print("\n=== PORTFOLIO SOURCE CHECK ===")
    portfolios_dict, source = load_portfolios_prefer_constants()

    if source == "CONSTANTS":
        print("📁 PORTFOLIOS SOURCE: CONSTANTS (primary)")
    elif source == "GOOGLE SHEETS / CSV":
        print("📊 PORTFOLIOS SOURCE: GOOGLE SHEETS / CSV (fallback)")
    else:
        print("⚠️ PORTFOLIOS SOURCE: NONE (empty fallback)")

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