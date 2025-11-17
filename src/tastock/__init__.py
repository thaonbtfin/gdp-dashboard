"""
Tastock Module

This module provides tools for fetching, calculating, and managing stock data.
"""

# Import key classes for easy access
from .data.data_manager import DataManager
# from .core.stock import Stock  # Removed vnstock dependency
# from .core.portfolio import Portfolio  # Removed vnstock dependency
from .data.data_calculator import DataCalculator
# from .data.data_fetcher import DataFetcher  # Removed vnstock dependency
from .data.data_storage import DataStorage