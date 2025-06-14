import sys
import os
# print(os.getcwd())
sys.path.insert(0, os.getcwd())

import pandas as pd

from src.tastock.fetcher import Fetcher
from src.tastock.stock import Stock
from src.tastock.portfolio import Portfolio
from src.tastock.helpers import Helpers
from src.constants import DEFAULT_SOURCE, SYMBOLS_DH, SYMBOLS_TH, DEFAULT_OUTPUT_DIR, SYMBOLS_VN30, TEMP_DIR
from src.tastock.calculator import Calculator

OUTPUT_DIR = DEFAULT_OUTPUT_DIR + 'fetchedData/sample'

def sample_fetch_periods_and_save_to_csv_file():

    print(sample_fetch_periods_and_save_to_csv_file.__name__)

    source = DEFAULT_SOURCE

    # Initialize the Fetcher with parameters
    fetcher = Fetcher(
            symbols='ACB',
            source=source,
            output_dir=OUTPUT_DIR
        )
    
    # Fetch historical data for the given period (number of business days)
    fetched_df_period = fetcher.fetch_history_to_dataframe_for_periods(
        period=1251,
    )
    # print(f'{fetched_df_period}')  # Uncomment to inspect fetched data
    
    # Save the fetched DataFrame to a CSV file
    Helpers.save_dataframes_to_csv_file(
        fetched_df_period
    )

    # Save all fetched DataFrames into a single merged CSV file
    Helpers.save_dataframes_to_csv_files(
        fetched_df_period,
        fetcher.base_output_dir,
        fetcher.source,
        fetcher.use_sub_dir
    )

def sample_fetch_from_start_end_date_and_save_to_csv_file():

    print(sample_fetch_from_start_end_date_and_save_to_csv_file.__name__)

    symbols = ['ACB', 'FPT']
    start_date = '2025-06-01'
    end_date = '2025-06-05'
    source = DEFAULT_SOURCE

    # Initialize the Fetcher with parameters
    fetcher = Fetcher(
            symbols=symbols,
            source=source,
            output_dir=OUTPUT_DIR
        )
    
    # Fetch historical data for the specified symbols and date range
    fetched_df = fetcher.fetch_history_to_dataframe_from_start_end_date(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    # Print the fetched DataFrame (uncomment to inspect)
    # print(f'{fetched_df}')  # Uncomment to inspect fetched data
    
    # Save the fetched DataFrame to a CSV file
    Helpers.save_dataframes_to_csv_file(
        fetched_df
    )

    # Save each symbol's DataFrame into separate CSV files in a folder
    Helpers.save_dataframes_to_csv_files(
        fetched_df,
        fetcher.base_output_dir,
        fetcher.source,
        fetcher.use_sub_dir
    )

def sample_calculator_moving_average():
    # In your main.py or another script where you process data:

    # --- Fetch data (example) ---
    fetcher = Fetcher(symbols='ACB', start_date='2023-12-01', end_date='2023-12-31')
    dataframes = fetcher.fetch_history_to_dataframe_from_start_end_date()

    acb_df = dataframes.get('ACB')

    if acb_df is not None and not acb_df.empty:
        # --- Calculate SMA ---
        # sma_20_series = Calculator.calculate_simple_moving_average(acb_df, window=20)
        sma_20_series = Calculator.calculate_moving_average(acb_df, window=20, price_column='close', ma_type='SMA')
        
        # Add it as a new column to the DataFrame
        if not sma_20_series.empty:
            acb_df['SMA_20'] = sma_20_series
            print("ACB DataFrame with SMA_20:")
            print(acb_df.tail())

        # --- Calculate EMA ---
        ema_10_series = Calculator.calculate_moving_average(acb_df, window=10, price_column='close', ma_type='EMA')
        if not ema_10_series.empty:
            acb_df['EMA_10'] = ema_10_series
            print("\nACB DataFrame with EMA_10:")
            print(acb_df.tail())

        # --- Perform other calculations ---
        # Example: Add profit rate columns (if you haven't already)
        # updated_dataframes = Calculator.add_profit_rate_columns_to_dataframe({'ACB': acb_df.copy()})
        # acb_df_with_profit = updated_dataframes['ACB']
        # print("\nACB DataFrame with Profit Rate:")
        # print(acb_df_with_profit.tail())
    else:
        print("ACB data is None or empty. Skipping save operation.")
        return # Exit the function if acb_df is not valid

    # This line saves acb_df, which now includes 'SMA_20' and 'EMA_10' if they were added.
    # save_dataframes_to_csv_file(acb_df)

def sample_calculate_stock_performance_metrics_to_stock_object():

    print(f"\nRunning: {sample_calculate_stock_performance_metrics_to_stock_object.__name__}")
    symbols = ['ACB','FPT'] 
    # Use a longer period for more meaningful calculations
    start_date = '2021-01-01' 
    end_date = '2023-12-31'
    source = DEFAULT_SOURCE
    
    metrics_df = Stock.get_multiple_stocks_metrics_df(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        source=source
    )

    if metrics_df is not None and not metrics_df.empty:
        # Display the DataFrame (optional)
        print("\nConsolidated Stock Performance Metrics:")
        print(metrics_df)

        # Save all metrics to a single CSV file using the new helper
        csv_filepath = Helpers.save_single_dataframe_to_csv(
            df=metrics_df,
            filename_prefix="all_symbols_performance_metrics",
            output_dir=OUTPUT_DIR, # Uses the OUTPUT_DIR defined in sample.py
            use_sub_dir=False # Saves directly into OUTPUT_DIR without creating a 'data_timestamp' subdir
        )
        print(f"\nAll stock performance metrics saved to: {csv_filepath}")

def sample_calculate_portfolio_performance_metrics():
    print(f"\nRunning: {sample_calculate_portfolio_performance_metrics.__name__}")

    portfolio_symbols = SYMBOLS_TH # Example portfolio
    start_date, end_date = Helpers.get_start_end_dates(1251)
    source = DEFAULT_SOURCE
    portfolio_name = "MyTechAndBankPortfolio"

    # Call the new static method from the Portfolio class
    metrics_df = Portfolio.get_portfolio_metrics_df(
        symbols=portfolio_symbols,
        start_date=start_date,
        end_date=end_date,
        source=source,
        weights=None, # Or specify weights: [0.4, 0.3, 0.3] for SYMBOLS_TH if it has 3 symbols
        name=portfolio_name
    )

    if metrics_df is not None and not metrics_df.empty:
        print(f"\nPortfolio Performance Metrics for {portfolio_name}:")
        # Display the DataFrame (optional, as it's a single row)
        # For a single row DataFrame, printing the Series might be cleaner:
        if not metrics_df.empty:
            print(metrics_df.iloc[0])

        # Save portfolio metrics to a CSV file using the helper
        csv_filepath = Helpers.save_single_dataframe_to_csv(
            df=metrics_df,
            # filename_prefix="all_symbols_performance_metrics",
            filename_prefix=f"portfolio_{portfolio_name}_performance_metrics",
            output_dir=OUTPUT_DIR, # Uses the OUTPUT_DIR defined in sample.py
            use_sub_dir=False # Saves directly into OUTPUT_DIR without creating a 'data_timestamp' subdir
        )
        print(f"\nPortfolio performance metrics for {portfolio_name} saved to: {csv_filepath}")
    else:
        print(f"Could not calculate performance metrics for portfolio {portfolio_name}.")

def main():
    """
    Example usage of Fetcher.
    """

if __name__ == "__main__":
    # main()
    sample_fetch_periods_and_save_to_csv_file()
    sample_fetch_from_start_end_date_and_save_to_csv_file()
    # sample_calculator_moving_average()                                # not use for now
    sample_calculate_stock_performance_metrics_to_stock_object()      # use this
    sample_calculate_portfolio_performance_metrics()                  # use this