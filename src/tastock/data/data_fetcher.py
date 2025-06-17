"""
DataFetcher Module

This module provides the DataFetcher class for fetching stock data.
It handles caching to avoid duplicate requests.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from .fetcher import Fetcher
from ..core.stock import Stock
from src.constants import DEFAULT_SOURCE

class DataFetcher:
    """
    DataFetcher handles fetching stock data and caching it to avoid duplicate requests.
    """
    
    def __init__(self, source: str = DEFAULT_SOURCE):
        """
        Initialize the DataFetcher.
        
        Args:
            source (str): Data source for stock information
        """
        self.source = source
        self.fetcher = Fetcher(source=source)
        
        # Cache to store fetched data
        self._stock_data_cache = {}  # {symbol_start_date_end_date: dataframe}
        self._financial_data_cache = {}  # {symbol: financial_df}
        
    def fetch_stock_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for the given symbols, using cache when available.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of {symbol: dataframe}
        """
        result = {}
        symbols_to_fetch = []
        
        # Check cache first
        for symbol in symbols:
            cache_key = f"{symbol}_{start_date}_{end_date}"
            if not force_refresh and cache_key in self._stock_data_cache:
                result[symbol] = self._stock_data_cache[cache_key]
            else:
                symbols_to_fetch.append(symbol)
        
        # Fetch only what's not in cache
        if symbols_to_fetch:
            fetched_data = self.fetcher.fetch_history_to_dataframe_from_start_end_date(
                symbols=symbols_to_fetch,
                start_date=start_date,
                end_date=end_date
            )
            
            # Update cache and result
            for symbol, data in fetched_data.items():
                cache_key = f"{symbol}_{start_date}_{end_date}"
                self._stock_data_cache[cache_key] = data
                result[symbol] = data
        
        return result
    
    def fetch_financial_data(self, symbol: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Fetch financial data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Optional[pd.DataFrame]: Financial data DataFrame or None if fetch fails
        """
        if not force_refresh and symbol in self._financial_data_cache:
            return self._financial_data_cache[symbol]
        
        # Create a temporary Stock object to fetch financial data
        try:
            stock = Stock(
                symbol=symbol,
                start_date=datetime.now().strftime('%Y-%m-%d'),  # Just need today for financial data
                end_date=datetime.now().strftime('%Y-%m-%d'),
                source=self.source
            )
            
            if stock.financial_ratios_df is not None:
                self._financial_data_cache[symbol] = stock.financial_ratios_df
                return stock.financial_ratios_df
            
            return None
        except Exception as e:
            print(f"Error fetching financial data for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data."""
        self._stock_data_cache.clear()
        self._financial_data_cache.clear()