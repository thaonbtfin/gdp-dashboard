"""
Calculate Metrics from History Data Workflow

This script calculates all metrics from existing history_data.csv instead of crawling.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_VN30, SYMBOLS_VN100, SYMBOLS_DH, SYMBOLS_TH, DATA_HISTORY, DEFAULT_OUTPUT_DIR
from src.tastock.data.data_calculator import DataCalculator
from src.tastock.data.data_storage import DataStorage

def main():
    """Calculate metrics from history data."""
    calculator = DataCalculator()
    storage = DataStorage(base_output_dir=DEFAULT_OUTPUT_DIR)
    
    # All symbols to process
    all_symbols = list(set(SYMBOLS_VN30 + SYMBOLS_VN100 + SYMBOLS_DH + SYMBOLS_TH))
    
    print(f"Calculating metrics for {len(all_symbols)} symbols from history data...")
    
    # Calculate metrics from history data
    metrics = calculator.calculate_metrics_from_history(all_symbols)
    
    if metrics:
        # Save performance metrics
        perf_file = storage.save_performance_metrics(metrics)
        print(f"Saved performance metrics to: {perf_file}")
        
        print(f"✅ Processed {len(metrics)} symbols from history data")
        

    else:
        print("❌ No metrics calculated")

if __name__ == "__main__":
    main()