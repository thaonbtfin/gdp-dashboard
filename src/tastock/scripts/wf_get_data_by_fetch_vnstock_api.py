"""
Data Workflow Fetch Script

This script provides a complete workflow for:
1. Fetching stock data via API
2. Processing stock data for portfolios
3. Saving data in structured folder format
4. Scheduling the workflow
"""

import os
import sys
import shutil
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Warning: 'schedule' module not available. Install with: pip install schedule")
import time
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, List

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import SYMBOLS_VN30, PORTFOLIOS
from src.tastock.workflows.wf_components import StructuredDataProcessor, FileCopier
from src.tastock.utils.helpers import Helpers
from src.tastock.data.data_manager import DataManager

class DataFetcher:
    """Handles fetching stock data via API with structured output"""
    
    def __init__(self, base_output_dir: str = 'data'):
        self.data_manager = DataManager(base_output_dir=base_output_dir)
        self.processor = StructuredDataProcessor(base_output_dir)
    
    def process_from_api_data(self, symbols: List[str], start_date: str, end_date: str, portfolio_name: str = 'VN30', period: int = 1251) -> bool:
        """Process data from API with structured output"""
        try:
            print(f"Fetching {portfolio_name} data from {start_date} to {end_date}")
            
            # Fetch data via API
            stock_data = self.data_manager.fetch_stock_data(symbols, start_date, end_date)
            
            if not stock_data:
                print("No data fetched")
                return False
            
            # Trim to exact period if specified
            if period:
                for symbol in stock_data:
                    df = stock_data[symbol]
                    if not df.empty and 'time' in df.columns:
                        df = df.sort_values('time').tail(period).reset_index(drop=True)
                        stock_data[symbol] = df
            
            print(f"Fetched {len(stock_data)} symbols for {portfolio_name}")
            
            # Process and save in structured format
            return self.processor.process_and_save_structured(stock_data, portfolio_name, symbols)
            
        except Exception as e:
            print(f"API processing failed: {e}")
            return False

# Classes are now imported from workflow_components

class DataWorkflowFetch:
    """Main workflow orchestrator for API-based data fetching"""
    
    def __init__(self, data_dir: str = 'data'):
        self.fetcher = DataFetcher(data_dir)
        self.copier = FileCopier(data_dir, data_dir)
    
    def run_full_workflow(self, portfolio_name: str = 'VN30', symbols: List[str] = None, period: int = 1251) -> bool:
        """Run the complete fetch workflow"""
        print("=== Starting Data Fetch Workflow ===")
        
        if symbols is None:
            symbols = SYMBOLS_VN30
        
        # Step 1: Get date range and process data via API
        start_date, end_date = Helpers.get_start_end_dates(period)
        print(f"\n1. Processing {portfolio_name} via API from {start_date} to {end_date}")
        
        success = self.fetcher.process_from_api_data(symbols, start_date, end_date, portfolio_name, period)
        if not success:
            print("Data processing failed")
            return False
        
        # Step 2: Copy latest files to root
        print(f"\n2. Copying latest files to root...")
        success = self.copier.copy_latest_files()
        if not success:
            print("File copying failed")
            return False
        
        print(f"\n=== Fetch Workflow completed successfully ===")
        return True
    
    def run_multiple_portfolios(self, portfolios: dict = None) -> bool:
        """Run workflow for multiple portfolios"""
        if portfolios is None:
            portfolios = PORTFOLIOS
        
        print("=== Starting Multiple Portfolio Fetch Workflow ===")
        
        success_count = 0
        for portfolio_name, symbols in portfolios.items():
            print(f"\n--- Processing Portfolio: {portfolio_name} ---")
            if self.run_full_workflow(portfolio_name, symbols):
                success_count += 1
            else:
                print(f"Failed to process portfolio: {portfolio_name}")
        
        print(f"\n=== Completed {success_count}/{len(portfolios)} portfolios ===")
        return success_count == len(portfolios)
    
    def schedule_workflow(self, time_str: str = "09:00", portfolio_name: str = 'VN30', symbols: List[str] = None):
        """Schedule the workflow to run daily"""
        if not SCHEDULE_AVAILABLE:
            print("Schedule module not available. Install with: pip install schedule")
            return
        
        print(f"Scheduling fetch workflow to run daily at {time_str}")
        
        schedule.every().day.at(time_str).do(
            lambda: self.run_full_workflow(portfolio_name, symbols)
        )
        
        print("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nScheduler stopped")

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