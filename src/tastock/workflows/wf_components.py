"""
Workflow Components Module

This module provides reusable components for data workflows including:
- DataDownloader: Downloads and extracts CafeF data
- DataProcessor: Processes data with basic structure
- StructuredDataProcessor: Processes data with portfolio folder structure
- FileCopier: Copies latest files to root data folder
"""

import os
import shutil
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Tuple, List
import requests
import zipfile
from urllib.parse import urlparse
from email.message import Message

from ..data.data_manager import DataManager
from ..utils.helpers import Helpers
from src.constants import SYMBOLS_VN30

# DataDownloader moved back to download script - not shared

class StructuredDataProcessor:
    """Handles data processing with structured folder output"""
    
    def __init__(self, base_output_dir: str = 'data'):
        self.data_manager = DataManager(base_output_dir=base_output_dir)
        self.base_output_dir = Path(base_output_dir)
    
    # API processing moved to fetch script - not shared
    
    def process_from_local_files(self, data_folder: Path, portfolio_name: str = 'VN30', symbols: list = None, period: int = 1251) -> bool:
        """Process data from local files with structured output"""
        if symbols is None:
            symbols = SYMBOLS_VN30
        
        try:
            start_date, end_date = Helpers.get_start_end_dates(period)
            print(f"Processing {portfolio_name} data from {start_date} to {end_date}")
            
            # Load data from local files
            stock_data = self.data_manager.load_data_from_local_files(
                folder_path=str(data_folder),
                symbols_filter=symbols,
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            
            if not stock_data:
                print("No data found")
                return False
            
            print(f"Processed {len(stock_data)} symbols for {portfolio_name}")
            
            # Process and save in structured format
            return self.process_and_save_structured(stock_data, portfolio_name, symbols)
            
        except Exception as e:
            print(f"Processing from local files failed: {e}")
            return False
    
    def process_and_save_structured(self, stock_data: dict, portfolio_name: str = 'VN30', symbols: List[str] = None) -> bool:
        """Process data and save in structured format"""
        if not stock_data:
            return False
        
        try:
            # Create date-based folder structure
            current_date = datetime.now().strftime('%Y%m%d')
            date_folder = self.base_output_dir / current_date
            portfolio_folder = date_folder / portfolio_name
            symbols_folder = portfolio_folder / 'symbols'
            
            # Ensure directories exist
            symbols_folder.mkdir(parents=True, exist_ok=True)
            
            # Calculate performance metrics
            performance_metrics = {}
            for symbol, df in stock_data.items():
                if not df.empty:
                    try:
                        metrics = self.data_manager.calculate_performance_metrics(symbol, df)
                        performance_metrics[symbol] = metrics
                        
                        # Save individual symbol file
                        symbol_file = symbols_folder / f"{symbol}_history_{current_date}.csv"
                        df.to_csv(symbol_file, index=False)
                        
                    except Exception as e:
                        print(f"Error processing {symbol}: {e}")
            
            # Save portfolio history file
            portfolio_history_file = symbols_folder / f"history_{portfolio_name}_{current_date}.csv"
            self._save_portfolio_history(stock_data, portfolio_history_file)
            
            # Save performance metrics file
            if performance_metrics:
                perf_file = symbols_folder / f"perf_{portfolio_name}_{current_date}.csv"
                self._save_performance_metrics(performance_metrics, perf_file)
            
            # Save merged files in portfolio folder
            self._save_merged_files(stock_data, performance_metrics, portfolio_folder)
            
            print(f"Data saved to structured folders under: {date_folder}")
            return True
            
        except Exception as e:
            print(f"Structured processing failed: {e}")
            return False
    
    def _save_portfolio_history(self, stock_data: dict, file_path: Path):
        """Save portfolio history CSV"""
        dfs = []
        for symbol, df in stock_data.items():
            if not df.empty and 'time' in df.columns and 'close' in df.columns:
                temp_df = df[['time', 'close']].copy()
                temp_df['time'] = temp_df['time'].astype(str)
                temp_df = temp_df.rename(columns={'close': symbol})
                dfs.append(temp_df.set_index('time'))
        
        if dfs:
            merged_df = pd.concat(dfs, axis=1, join='outer').reset_index()
            merged_df = merged_df.rename(columns={'index': 'time'})
            merged_df = merged_df.fillna(0)
            merged_df.to_csv(file_path, index=False)
    
    def _save_performance_metrics(self, performance_metrics: dict, file_path: Path):
        """Save performance metrics CSV"""
        metrics_list = []
        for symbol, metrics in performance_metrics.items():
            metrics_row = {'symbol': symbol}
            metrics_row.update(metrics)
            metrics_list.append(metrics_row)
        
        if metrics_list:
            metrics_df = pd.DataFrame(metrics_list)
            metrics_df.to_csv(file_path, index=False)
    
    def _save_merged_files(self, stock_data: dict, performance_metrics: dict, portfolio_folder: Path):
        """Save merged files in portfolio folder"""
        # Save merged history
        history_file = portfolio_folder / 'history_data_all_symbols.csv'
        self._save_portfolio_history(stock_data, history_file)
        
        # Save merged performance metrics
        if performance_metrics:
            perf_file = portfolio_folder / 'perf_all_symbols.csv'
            self._save_performance_metrics(performance_metrics, perf_file)

# DataFetcher functionality integrated into StructuredDataProcessor

class FileCopier:
    """Handles copying latest files to root data folder"""
    
    def __init__(self, source_dir: str = 'data', target_dir: str = 'data'):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
    
    def copy_latest_files(self) -> bool:
        """Copy latest CSV files to root data folder"""
        try:
            files_to_copy = [
                'history_data_all_symbols.csv',
                'perf_all_symbols.csv'
            ]
            
            for filename in files_to_copy:
                latest_file = self._find_latest_file(filename)
                if latest_file:
                    target_file = self.target_dir / filename
                    if latest_file.resolve() != target_file.resolve():
                        shutil.copy2(latest_file, target_file)
                        print(f"Copied {filename} to root data folder")
                    else:
                        print(f"{filename} already in root data folder")
                else:
                    print(f"Warning: {filename} not found")
            
            return True
            
        except Exception as e:
            print(f"File copying failed: {e}")
            return False
    
    def _find_latest_file(self, filename: str) -> Optional[Path]:
        """Find the latest version of a file in dated folders"""
        pattern = f"*/*/{filename}"
        matching_files = list(self.source_dir.glob(pattern))
        
        if matching_files:
            latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
            return latest_file
        
        return None

class DataFileManager:
    """Handles common data file operations"""
    
    @staticmethod
    def copy_history_to_root(base_output_dir: str = 'data') -> bool:
        """Copy history_data_all_symbols.csv to history_data.csv"""
        try:
            base_dir = Path(base_output_dir)
            source_file = base_dir / 'history_data_all_symbols.csv'
            target_file = base_dir / 'history_data.csv'
            
            if not source_file.exists():
                print(f"Source file not found: {source_file}")
                return False
            
            shutil.copy2(source_file, target_file)
            print(f"Copied {source_file.name} to {target_file.name}")
            return True
            
        except Exception as e:
            print(f"Failed to copy history file: {e}")
            return False