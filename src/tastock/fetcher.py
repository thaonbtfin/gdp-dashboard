"""
Fetcher Module

This module provides the Fetcher class for fetching historical stock data for given symbols,
saving each symbol's data into CSV files, and merging them on the 'time' column into a final CSV.

Usage (as a script):
    python -m models.fetcher --symbols ACB,VCB --start_date 2024-01-01 --end_date 2024-06-01 --source VCI

Or import and use Fetcher in your own code:
    from models.fetcher import Fetcher = Fetcher(symbols=['ACB', 'VCB'], start_date='2024-01-01', end_date='2024-06-01', source='VCI')
    fetcher.fetch_history_and_merge_csv()
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import pandas as pd

from vnstock import Vnstock
from src.constants import DEFAULT_SYMBOL, DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR
from helpers import Helpers

class Fetcher():
    """
    Fetcher class for downloading and merging historical stock data for multiple symbols.
    """
    def __init__(
        self,
        symbols=DEFAULT_SYMBOL,
        start_date=DEFAULT_START_DATE,
        end_date=DEFAULT_END_DATE,
        source=DEFAULT_SOURCE,
        output_dir=DEFAULT_OUTPUT_DIR,
        use_sub_dir=True
    ):
        """
        Initialize Fetcher.

        Args:
            symbols (list or str): List or comma-separated string of stock symbols.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
            source (str): Data source for stock info (default: 'VCI').
            output_dir (str): Directory to save CSV files.
            use_sub_dir (bool): Whether to use a dated subdirectory.
        """
        super().__init__()  # Initialize BaseModel
        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(',') if s.strip()]
        elif not isinstance(symbols, list):
            raise ValueError("Symbols must be a list or a comma-separated string.")
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.base_output_dir = output_dir
        self.use_sub_dir = use_sub_dir
        
    def fetch_history_to_dataframe_from_start_end_date(self, symbols=None, start_date=None, end_date=None, source=None):
        """
        Fetch historical data for given symbols and date range.
        Args:
            symbols (list or str, optional): List or comma-separated string of stock symbols.
                                            Defaults to `self.symbols`.
            start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to `self.start_date`.
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to `self.end_date`.

        Returns:
            dict: A dictionary where keys are symbols and values are DataFrames of historical data.
                  Example: {'ACB': DataFrame, 'FPT': DataFrame}
        """
        symbols = symbols or self.symbols
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date

        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(',') if s.strip()]

        dataframes = {}
        for symbol in symbols:
            sym_obj = Vnstock().stock()
            df_history = sym_obj.quote.history(start=start_date, end=end_date)
            dataframes[symbol] = df_history

        print(f"Completed fetching dataframes for symbols: {', '.join(symbols)} from {start_date} to {end_date}")
        return dataframes
    
    def fetch_history_to_dataframe_for_periods(self, symbols=None, period=0, source=None):
        """
        Fetch historical data for given symbols for a specified number of business days.

        The method calculates the start and end dates based on the `period`
        and then fetches data, ensuring the returned DataFrame for each symbol
        contains at most `period` rows of data (the latest `period` days).

        Args:
            symbols (list or str, optional): Symbols to fetch. Defaults to `self.symbols`.
            period (int, optional): Number of business days to fetch. Defaults to 0.

        Returns:
            dict: A dictionary where keys are symbols and values are DataFrames
                  trimmed to the specified `period`.
        """
        symbols = symbols or self.symbols

        # Get initial start and end dates
        start_date, end_date = Helpers.get_start_end_dates(period)

        # Calculate years between start_date and end_date
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        years = end_dt.year - start_dt.year

        # Adjust start_date by subtracting (30 * years) days
        # This is a heuristic to ensure enough data is fetched before trimming.
        # It assumes roughly 20-22 trading days per month, so 30 days per year difference
        adjusted_start_date = start_dt - pd.Timedelta(days=(30 * years))

        # Fetch dataframes for all symbols
        dataframes = self.fetch_history_to_dataframe_from_start_end_date(
            start_date=adjusted_start_date.strftime('%Y-%m-%d'),
            end_date=end_date,
            symbols=symbols,
        )

        # Trim each Dataframe to keep only the last `period` rows
        final_dataframes = {}
        for symbol, df in dataframes.items():
            if len(df) > period:
                final_dataframes[symbol] = df.tail(period).reset_index(drop=True)
            else:
                final_dataframes[symbol] = df.reset_index(drop=True)

        print(f"Completed fetching dataframes for period: {period} days")
        return final_dataframes

def run_fetcher():
    """
    Command-line interface for Fetcher.
    """
    parser = argparse.ArgumentParser(description='Fetch symbols data and save to CSV')
    parser.add_argument('--symbols', type=str, default=DEFAULT_SYMBOL, help='Comma separated list of stock symbols')
    parser.add_argument('--start_date', type=str, default=DEFAULT_START_DATE, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, default=DEFAULT_END_DATE, help='End date in YYYY-MM-DD format')
    parser.add_argument('--source', type=str, default=DEFAULT_SOURCE, help='Data source for stock info (default: VCI)')
    parser.add_argument('--output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help='Output directory base (default: %(default)s)')
    parser.add_argument('--use_sub_dir', type=lambda x: (str(x).lower() == 'true'), default=True,
                        help='Use subdirectory with today\'s date (default: True)')
    args = parser.parse_args()

    fetcher = Fetcher(
        symbols=args.symbols,
        start_date=args.start_date,
        end_date=args.end_date,
        source=args.source,
        output_dir=args.output_dir,
        use_sub_dir=args.use_sub_dir
    )
    # Example: Fetch data for the default symbols and date range
    dataframes = fetcher.fetch_history_to_dataframe_from_start_end_date()
    print(f"Fetched data for: {list(dataframes.keys())}")

if __name__ == '__main__':
    run_fetcher()