"""
DataManager Module

This module provides a centralized way to manage data for both portfolios and symbols
in the tastock application. It coordinates between fetching, calculating, and storing data.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from functools import lru_cache

from .data_fetcher import DataFetcher
from .data_calculator import DataCalculator
from .data_storage import DataStorage
from ..core.portfolio import Portfolio
from src.constants import DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR

class DataManager:
    """
    DataManager coordinates between fetching, calculating, and storing data for stocks and portfolios.
    """
    
    def __init__(
        self,
        base_output_dir: str = DEFAULT_OUTPUT_DIR,
        source: str = DEFAULT_SOURCE
    ):
        """
        Initialize the DataManager.
        
        Args:
            base_output_dir (str): Base directory for data storage
            source (str): Data source for stock information
        """
        self.base_output_dir = base_output_dir
        self.source = source
        
        # Initialize components
        self.fetcher = DataFetcher(source=source)
        self.calculator = DataCalculator()
        self.storage = DataStorage(base_output_dir=base_output_dir)
        
    def fetch_stock_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for the given symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of {symbol: dataframe}
        """
        return self.fetcher.fetch_stock_data(symbols, start_date, end_date, force_refresh)
    
    def calculate_performance_metrics(
        self, 
        symbol: str, 
        data: pd.DataFrame = None,
        force_recalculate: bool = False
    ) -> Dict:
        """
        Calculate performance metrics for a symbol.
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data DataFrame (if None, must be in cache)
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Dict: Performance metrics dictionary
        """
        return self.calculator.calculate_performance_metrics(symbol, data, force_recalculate)
    
    def calculate_intrinsic_value(
        self, 
        symbol: str,
        force_recalculate: bool = False
    ) -> Optional[float]:
        """
        Calculate intrinsic value for a symbol.
        
        Args:
            symbol (str): Stock symbol
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Optional[float]: Intrinsic value or None if calculation fails
        """
        # Fetch financial data first
        financial_data = self.fetcher.fetch_financial_data(symbol)
        
        # Calculate intrinsic value
        return self.calculator.calculate_intrinsic_value(
            symbol, 
            financial_data=financial_data,
            source=self.source,
            force_recalculate=force_recalculate
        )
    
    def save_stock_data(
        self, 
        symbol: str, 
        data: pd.DataFrame,
        portfolio_name: Optional[str] = None
    ) -> str:
        """
        Save stock data to CSV file.
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data DataFrame
            portfolio_name (str): Portfolio name (if part of a portfolio)
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_stock_data(symbol, data, portfolio_name)
    
    def save_portfolio_history(
        self, 
        portfolio_name: str, 
        data: Dict[str, pd.DataFrame]
    ) -> Tuple[str, str]:
        """
        Save portfolio history data to CSV files.
        
        Args:
            portfolio_name (str): Portfolio name
            data (Dict[str, pd.DataFrame]): Dictionary of {symbol: dataframe}
            
        Returns:
            Tuple[str, str]: Paths to portfolio history file and merged history file
        """
        return self.storage.save_portfolio_history(portfolio_name, data)
    
    def save_performance_metrics(
        self, 
        metrics_data: Dict[str, Dict],
        portfolio_name: Optional[str] = None
    ) -> str:
        """
        Save performance metrics to CSV file.
        
        Args:
            metrics_data (Dict[str, Dict]): Dictionary of {symbol: metrics_dict}
            portfolio_name (str): Portfolio name (if for a specific portfolio)
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_performance_metrics(metrics_data, portfolio_name)
    
    def save_intrinsic_values(
        self, 
        intrinsic_values: Dict[str, float]
    ) -> str:
        """
        Save intrinsic values to CSV file.
        
        Args:
            intrinsic_values (Dict[str, float]): Dictionary of {symbol: intrinsic_value}
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_intrinsic_values(intrinsic_values)
    
    def save_financial_data(
        self, 
        financial_data: Dict[str, pd.DataFrame]
    ) -> str:
        """
        Save financial data to CSV file.
        
        Args:
            financial_data (Dict[str, pd.DataFrame]): Dictionary of {symbol: financial_df}
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_financial_data(financial_data)
    
    def process_portfolio(
        self, 
        portfolio_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        weights: List[float] = None,
        save_data: bool = True
    ) -> Dict:
        """
        Process a portfolio: fetch data, calculate metrics, and optionally save to files.
        
        Args:
            portfolio_name (str): Portfolio name
            symbols (List[str]): List of stock symbols in the portfolio
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            weights (List[float]): List of weights for each symbol (optional)
            save_data (bool): Whether to save data to files
            
        Returns:
            Dict: Dictionary with portfolio data and metrics
        """
        # Fetch data for all symbols
        stock_data = self.fetch_stock_data(symbols, start_date, end_date)
        
        # Calculate performance metrics for each symbol
        performance_metrics = {}
        for symbol, data in stock_data.items():
            metrics = self.calculate_performance_metrics(symbol, data)
            performance_metrics[symbol] = metrics
        
        # Create portfolio object
        portfolio = Portfolio(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            source=self.source,
            weights=weights,
            name=portfolio_name,
            fetched_data=stock_data
        )
        
        portfolio_metrics = portfolio.get_performance_metrics()
        portfolio_value_series = portfolio.get_portfolio_value_series()
        
        result = {
            'portfolio_name': portfolio_name,
            'stock_data': stock_data,
            'performance_metrics': performance_metrics,
            'portfolio_metrics': portfolio_metrics,
            'portfolio_value_series': portfolio_value_series
        }
        
        # Save data if requested
        if save_data:
            # Save individual stock data and portfolio history
            self.save_portfolio_history(portfolio_name, stock_data)
            
            # Save performance metrics
            self.save_performance_metrics(performance_metrics, portfolio_name)
            
            # Save portfolio metrics
            portfolio_metrics_dict = {portfolio_name: portfolio_metrics}
            self.save_performance_metrics(portfolio_metrics_dict, f"{portfolio_name}_portfolio")
        
        return result
    
    def load_data_from_local_files(self, folder_path: str, symbols_filter: List[str] = None, start_date: str = None, end_date: str = None, period: int = None) -> Dict[str, pd.DataFrame]:
        """
        Load stock data from local CSV files in the specified folder.
        Optimized for large CSV files using vectorized pandas operations.
        
        Args:
            folder_path (str): Path to folder containing CSV files
            symbols_filter (List[str]): Optional list to filter specific symbols
            start_date (str): Start date in YYYY-MM-DD format (optional)
            end_date (str): End date in YYYY-MM-DD format (optional)
            period (int): Number of data points to return (optional)
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of {symbol: dataframe}
        """
        import glob
        from datetime import datetime, timedelta
        
        # Extend start_date if period is specified to ensure enough data
        if period and start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            # Add buffer days: period/5 years * 20 days/year + 50 extra days
            buffer_days = int(period / 5 * 20) + 50
            extended_start = start_dt - timedelta(days=buffer_days)
            query_start_date = extended_start.strftime('%Y-%m-%d')
        else:
            query_start_date = start_date
        
        stock_data = {}
        
        # Get all CSV files in the folder
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        
        for file_path in csv_files:
            try:
                # Read CSV file with optimized settings for large files
                df = pd.read_csv(file_path, dtype={
                    '<Ticker>': 'string',
                    '<DTYYYYMMDD>': 'string',
                    '<Open>': 'float64',
                    '<High>': 'float64', 
                    '<Low>': 'float64',
                    '<Close>': 'float64',
                    '<Volume>': 'int64'
                })
                
                # Filter symbols if specified, but always include VNAll-INDEX
                if symbols_filter:
                    # Add VNAll-INDEX to filter list if not present
                    filter_symbols = list(symbols_filter)
                    if 'VNAll-INDEX' not in filter_symbols and 'VNINDEX' in filter_symbols:
                        filter_symbols.append('VNAll-INDEX')
                    df = df[df['<Ticker>'].isin(filter_symbols)]
                
                # Skip if no data after filtering
                if df.empty:
                    continue
                
                # Vectorized date conversion
                df['time'] = pd.to_datetime(df['<DTYYYYMMDD>'], format='%Y%m%d')
                
                # Rename columns to standard format
                df = df.rename(columns={
                    '<Open>': 'open',
                    '<High>': 'high', 
                    '<Low>': 'low',
                    '<Close>': 'close',
                    '<Volume>': 'volume',
                    '<Ticker>': 'symbol'
                })
                
                # Select only needed columns
                df = df[['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']]
                
                # Filter by date range if specified
                if query_start_date or end_date:
                    if query_start_date:
                        df = df[df['time'] >= query_start_date]
                    if end_date:
                        df = df[df['time'] <= end_date]
                
                # Group by symbol and create separate DataFrames
                for symbol, group_df in df.groupby('symbol'):
                    # Sort by time and reset index
                    symbol_df = group_df.drop('symbol', axis=1).sort_values('time').reset_index(drop=True)
                    
                    if symbol not in stock_data:
                        stock_data[symbol] = symbol_df
                    else:
                        # Concatenate if symbol exists in multiple files
                        stock_data[symbol] = pd.concat([stock_data[symbol], symbol_df], ignore_index=True)
                        # Remove duplicates based on time and sort
                        stock_data[symbol] = stock_data[symbol].drop_duplicates(subset=['time'], keep='last')
                        stock_data[symbol] = stock_data[symbol].sort_values('time').reset_index(drop=True)
                        
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        # Trim data to exact period length if specified
        if period:
            # Find the symbol with the most data to use as base, prioritize VNINDEX
            max_symbol = None
            max_count = 0
            
            # First check if VNINDEX exists and has data
            if 'VNINDEX' in stock_data:
                df = stock_data['VNINDEX']
                if not df.empty and 'time' in df.columns:
                    max_symbol = 'VNINDEX'
                    max_count = len(df)
            
            # If VNINDEX not available or empty, find symbol with most data
            if max_symbol is None:
                for symbol in stock_data:
                    df = stock_data[symbol]
                    if not df.empty and 'time' in df.columns:
                        count = len(df)
                        if count > max_count:
                            max_count = count
                            max_symbol = symbol
            
            if max_symbol:
                # Use the most complete symbol's last 'period' dates as base
                base_df = stock_data[max_symbol].sort_values('time').tail(period)
                base_times = base_df['time'].tolist()
                
                # Trim all symbols to match these dates
                for symbol in stock_data:
                    df = stock_data[symbol]
                    if not df.empty and 'time' in df.columns:
                        # Filter to base times and reindex to ensure exact period length
                        df_filtered = df[df['time'].isin(base_times)].sort_values('time')
                        
                        # Create complete dataframe with all base times
                        complete_df = pd.DataFrame({'time': base_times})
                        df_merged = complete_df.merge(df_filtered, on='time', how='left')
                        
                        # Fill missing values - use forward fill for VNINDEX, 0 for others
                        for col in df_merged.columns:
                            if col != 'time':
                                if symbol == 'VNINDEX':
                                    df_merged[col] = df_merged[col].ffill().bfill()
                                else:
                                    df_merged[col] = df_merged[col].fillna(0)
                        
                        stock_data[symbol] = df_merged.reset_index(drop=True)
        
        # Fix VNINDEX symbol name (VNAll-INDEX -> VNINDEX) and move to first position
        if 'VNAll-INDEX' in stock_data:
            vnindex_data = stock_data.pop('VNAll-INDEX')
            # Create new ordered dict with VNINDEX first
            new_stock_data = {'VNINDEX': vnindex_data}
            new_stock_data.update(stock_data)
            stock_data = new_stock_data
            print("Renamed VNAll-INDEX to VNINDEX and moved to first position")
        elif 'VNINDEX' in stock_data:
            # Move existing VNINDEX to first position
            vnindex_data = stock_data.pop('VNINDEX')
            new_stock_data = {'VNINDEX': vnindex_data}
            new_stock_data.update(stock_data)
            stock_data = new_stock_data
            print("Moved VNINDEX to first position")
        
        return stock_data
    
    def get_close_prices(self, symbols: List[str], start_date: str = None, end_date: str = None, 
                        folder_path: str = None, period: int = None) -> pd.DataFrame:
        """
        Efficiently query historical close prices for specified symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format (optional)
            end_date (str): End date in YYYY-MM-DD format (optional)
            folder_path (str): Path to CSV files (if loading from files)
            
        Returns:
            pd.DataFrame: DataFrame with time index and close prices as columns
        """
        if folder_path:
            # Load data from files with symbol filter for efficiency
            stock_data = self.load_data_from_local_files(folder_path, symbols_filter=symbols, start_date=start_date, end_date=end_date, period=period)
        else:
            # Use existing data or fetch if needed
            stock_data = self.fetch_stock_data(symbols, start_date or '2020-01-01', end_date or '2024-12-31')
        
        close_prices_data = []
        
        for symbol, df in stock_data.items():
            if df.empty or 'close' not in df.columns:
                continue
                
            # Filter by date range if specified
            symbol_df = df.copy()
            if start_date:
                symbol_df = symbol_df[symbol_df['time'] >= start_date]
            if end_date:
                symbol_df = symbol_df[symbol_df['time'] <= end_date]
            
            # Select only time and close price
            close_df = symbol_df[['time', 'close']].copy()
            close_df['time'] = pd.to_datetime(close_df['time'])
            close_df = close_df.drop_duplicates(subset=['time']).set_index('time')
            close_df = close_df.rename(columns={'close': symbol})
            close_prices_data.append(close_df)
        
        if not close_prices_data:
            return pd.DataFrame()
        
        # Merge all close prices into single DataFrame
        result_df = pd.concat(close_prices_data, axis=1, join='outer', sort=True)
        result_df = result_df.fillna(0)
        result_df.index.name = 'time'
        result_df = result_df.reset_index()
        result_df['time'] = result_df['time'].dt.strftime('%Y-%m-%d')
        
        return result_df
    
    def process_all_symbols_from_files(
        self,
        folder_path: str,
        symbols: List[str] = None,
        start_date: str = None,
        end_date: str = None,
        period: int = None,
        calculate_intrinsic: bool = False,
        save_data: bool = True
    ) -> Dict:
        """
        Process symbols from local CSV files instead of fetching from external sources.
        
        Args:
            folder_path (str): Path to folder containing CSV files
            symbols (List[str]): Optional list to filter specific symbols
            calculate_intrinsic (bool): Whether to calculate intrinsic values
            save_data (bool): Whether to save data to files
            
        Returns:
            Dict: Dictionary with all processed data
        """
        # Load data from local files with symbol and date filtering
        stock_data = self.load_data_from_local_files(folder_path, symbols_filter=symbols, start_date=start_date, end_date=end_date, period=period)
        
        # Calculate performance metrics for each symbol
        performance_metrics = {}
        for symbol, data in stock_data.items():
            if not data.empty:
                metrics = self.calculate_performance_metrics(symbol, data)
                performance_metrics[symbol] = metrics
        
        result = {
            'stock_data': stock_data,
            'performance_metrics': performance_metrics
        }
        
        # Calculate intrinsic values if requested
        if calculate_intrinsic:
            intrinsic_values = {}
            financial_data = {}
            
            for symbol in stock_data.keys():
                # Fetch financial data
                fin_data = self.fetcher.fetch_financial_data(symbol)
                if fin_data is not None:
                    financial_data[symbol] = fin_data
                
                # Calculate intrinsic value
                iv = self.calculate_intrinsic_value(symbol)
                intrinsic_values[symbol] = iv
            
            result['intrinsic_values'] = intrinsic_values
            result['financial_data'] = financial_data
        
        # Save data if requested
        if save_data:
            # Extract close prices from loaded data
            if stock_data:
                close_prices_data = []
                for symbol, df in stock_data.items():
                    if not df.empty and 'close' in df.columns:
                        close_df = df[['time', 'close']].copy()
                        close_df['time'] = pd.to_datetime(close_df['time'])
                        close_df = close_df.drop_duplicates(subset=['time']).set_index('time')
                        close_df = close_df.rename(columns={'close': symbol})
                        close_prices_data.append(close_df)
                
                if close_prices_data:
                    merged_df = pd.concat(close_prices_data, axis=1, join='outer', sort=True).reset_index()
                    merged_df = merged_df.fillna(0)
                    merged_df['time'] = merged_df['time'].dt.strftime('%Y-%m-%d')
                    
                    # Save to dated folder
                    dated_folder = self.storage._create_dated_folder()
                    merged_file_path = os.path.join(
                        dated_folder, 
                        f"history_data_all_symbols_{self.storage._get_dated_folder_name()}.csv"
                    )
                    merged_df.to_csv(merged_file_path, index=False)
                    
                    # Copy to root data folder
                    root_all_symbols_path = os.path.join(self.base_output_dir, "history_data_all_symbols.csv")
                    merged_df.to_csv(root_all_symbols_path, index=False)
            
            # Save performance metrics
            self.save_performance_metrics(performance_metrics)
            
            # Save intrinsic values if calculated
            if calculate_intrinsic and intrinsic_values:
                self.save_intrinsic_values(intrinsic_values)
                
                # Save financial data if available
                if financial_data:
                    self.save_financial_data(financial_data)
        
        return result
    
    def process_all_symbols(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        period: int = None,
        calculate_intrinsic: bool = True,
        save_data: bool = True,
        use_local_files: bool = False,
        local_folder_path: str = None
    ) -> Dict:
        """
        Process all symbols: fetch data or load from local files, calculate metrics and intrinsic values.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            calculate_intrinsic (bool): Whether to calculate intrinsic values
            save_data (bool): Whether to save data to files
            use_local_files (bool): Whether to use local files instead of fetching
            local_folder_path (str): Path to local files folder
            
        Returns:
            Dict: Dictionary with all processed data
        """
        if use_local_files and local_folder_path:
            return self.process_all_symbols_from_files(
                folder_path=local_folder_path,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                period=period,
                calculate_intrinsic=calculate_intrinsic,
                save_data=save_data
            )
        
        # Original implementation - fetch data from external sources
        # Fetch data for all symbols
        stock_data = self.fetch_stock_data(symbols, start_date, end_date)
        
        # Calculate performance metrics for each symbol
        performance_metrics = {}
        for symbol, data in stock_data.items():
            metrics = self.calculate_performance_metrics(symbol, data)
            performance_metrics[symbol] = metrics
        
        result = {
            'stock_data': stock_data,
            'performance_metrics': performance_metrics
        }
        
        # Calculate intrinsic values if requested
        if calculate_intrinsic:
            intrinsic_values = {}
            financial_data = {}
            
            for symbol in symbols:
                # Fetch financial data
                fin_data = self.fetcher.fetch_financial_data(symbol)
                if fin_data is not None:
                    financial_data[symbol] = fin_data
                
                # Calculate intrinsic value
                iv = self.calculate_intrinsic_value(symbol)
                intrinsic_values[symbol] = iv
            
            result['intrinsic_values'] = intrinsic_values
            result['financial_data'] = financial_data
        
        # Save data if requested
        if save_data:
            # Save merged history data
            dfs = []
            for symbol, df in stock_data.items():
                if 'time' in df.columns and 'close' in df.columns:
                    temp_df = df[['time', 'close']].copy()
                    temp_df['time'] = temp_df['time'].astype(str)
                    # Rename close column to symbol name to preserve individual values
                    temp_df = temp_df.rename(columns={'close': symbol})
                    dfs.append(temp_df.set_index('time'))
            
            if dfs:
                # Merge dataframes on time index, preserving individual symbol values
                merged_df = pd.concat(dfs, axis=1, join='outer').reset_index()
                merged_df = merged_df.fillna(0)
                merged_df = merged_df.rename(columns={'index': 'time'})
                
                # Save to dated folder
                dated_folder = self.storage._create_dated_folder()
                merged_file_path = os.path.join(
                    dated_folder, 
                    f"history_data_all_symbols_{self.storage._get_dated_folder_name()}.csv"
                )
                merged_df.to_csv(merged_file_path, index=False)
                
                # Copy to root data folder
                root_all_symbols_path = os.path.join(self.base_output_dir, "history_data_all_symbols.csv")
                merged_df.to_csv(root_all_symbols_path, index=False)
            
            # Save performance metrics
            self.save_performance_metrics(performance_metrics)
            
            # Save intrinsic values if calculated
            if calculate_intrinsic and intrinsic_values:
                self.save_intrinsic_values(intrinsic_values)
                
                # Save financial data if available
                if financial_data:
                    self.save_financial_data(financial_data)
        
        return result
    
    def load_latest_data(self, data_type: str = 'history') -> pd.DataFrame:
        """
        Load the latest data from the root data folder.
        
        Args:
            data_type (str): Type of data to load ('history', 'perf', 'intrinsic', 'fin', 'bizuni')
            
        Returns:
            pd.DataFrame: Loaded DataFrame or empty DataFrame if file not found
        """
        return self.storage.load_latest_data(data_type)
    
    def clear_caches(self):
        """Clear all caches."""
        self.fetcher.clear_cache()
        self.calculator.clear_cache()