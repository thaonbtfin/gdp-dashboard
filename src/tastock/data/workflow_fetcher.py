"""
Workflow Fetcher Module

This module provides workflow classes for API-based data fetching.
"""

from typing import List
from .data_manager import DataManager
from ..workflows.wf_components import StructuredDataProcessor, FileCopier
from ..utils.helpers import Helpers

class APIDataFetcher:
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

class DataWorkflowFetch:
    """Main workflow orchestrator for API-based data fetching"""
    
    def __init__(self, data_dir: str = 'data'):
        self.fetcher = APIDataFetcher(data_dir)
        self.copier = FileCopier(data_dir, data_dir)
    
    def run_full_workflow(self, portfolio_name: str = 'VN30', symbols: List[str] = None, period: int = 1251) -> bool:
        """Run the complete fetch workflow"""
        print("=== Starting Data Fetch Workflow ===")
        
        from src.constants import SYMBOLS_VN30
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
        from src.constants import PORTFOLIOS
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
        try:
            import schedule
            print(f"Scheduling fetch workflow to run daily at {time_str}")
            
            schedule.every().day.at(time_str).do(
                lambda: self.run_full_workflow(portfolio_name, symbols)
            )
            
            print("Scheduler started. Press Ctrl+C to stop.")
            import time
            while True:
                schedule.run_pending()
                time.sleep(60)
        except ImportError:
            print("Schedule module not available. Install with: pip install schedule")
        except KeyboardInterrupt:
            print("\nScheduler stopped")