"""
Example script demonstrating how to use the DataManager class.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
from datetime import datetime, timedelta

from src.constants import PORTFOLIOS, SYMBOLS_VN30, DATA_DIR
from src.tastock.data_manager import DataManager

def get_date_range(days_back=30):
    """Get a date range from days_back days ago to yesterday."""
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def main():
    """Main function demonstrating DataManager usage."""
    # Initialize DataManager with data directory
    data_manager = DataManager(base_output_dir=os.path.join(DATA_DIR))
    
    # Get date range for the last 30 days
    start_date, end_date = get_date_range(30)
    print(f"Processing data from {start_date} to {end_date}")
    
    # Example 1: Process a single portfolio
    portfolio_name = "VN30"
    symbols = PORTFOLIOS.get(portfolio_name, [])[:5]  # Using first 5 symbols for demo
    
    print(f"\nProcessing portfolio: {portfolio_name} with {len(symbols)} symbols")
    portfolio_result = data_manager.process_portfolio(
        portfolio_name=portfolio_name,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        save_data=True
    )
    
    # Print portfolio metrics
    print(f"\nPortfolio metrics for {portfolio_name}:")
    for metric, value in portfolio_result['portfolio_metrics'].items():
        print(f"  {metric}: {value}")
    
    # Example 2: Process all symbols in VN30
    print("\nProcessing all VN30 symbols")
    all_symbols = SYMBOLS_VN30[:5]  # Using first 5 symbols for demo
    
    all_symbols_result = data_manager.process_all_symbols(
        symbols=all_symbols,
        start_date=start_date,
        end_date=end_date,
        calculate_intrinsic=True,
        save_data=True
    )
    
    # Print intrinsic values
    print("\nIntrinsic values:")
    for symbol, value in all_symbols_result['intrinsic_values'].items():
        print(f"  {symbol}: {value}")
    
    # Example 3: Load latest data
    print("\nLoading latest history data")
    latest_history = data_manager.load_latest_data('history')
    if not latest_history.empty:
        print(f"  Loaded history data with {len(latest_history)} rows and columns: {', '.join(latest_history.columns)}")
    else:
        print("  No history data found")
    
    print("\nLoading latest performance metrics")
    latest_perf = data_manager.load_latest_data('perf')
    if not latest_perf.empty:
        print(f"  Loaded performance metrics with {len(latest_perf)} rows")
    else:
        print("  No performance metrics found")

if __name__ == "__main__":
    main()