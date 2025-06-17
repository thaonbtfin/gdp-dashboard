"""
Sample script demonstrating how to use the tastock module.
"""

import pandas as pd

from src.tastock.data.fetcher import Fetcher
from src.tastock.core.stock import Stock
from src.tastock.core.portfolio import Portfolio
from src.tastock.utils.helpers import Helpers
from src.constants import DEFAULT_SOURCE, SYMBOLS_DH, SYMBOLS_TH, DEFAULT_OUTPUT_DIR, SYMBOLS_VN30, TEMP_DIR
from src.tastock.data.calculator import Calculator

OUTPUT_DIR = DEFAULT_OUTPUT_DIR + 'fetchedData/sample'

def sample_fetch_periods_and_save_to_csv_file():
    """Sample function to fetch data for a period and save to CSV."""
    print(sample_fetch_periods_and_save_to_csv_file.__name__)

    source = DEFAULT_SOURCE

    # Initialize the Fetcher with parameters
    fetcher = Fetcher(
            symbols='ACB',
            source=source,
            output_dir=OUTPUT_DIR+'/periods'
        )
    
    # Fetch historical data for the given period (number of business days)
    fetched_df_period = fetcher.fetch_history_to_dataframe_for_periods(
        period=1251,
    )
    
    # Save the fetched DataFrame to a CSV file
    Helpers.save_multiple_dataframes_to_single_csv(
            dataframes=fetched_df_period,
            filename_prefix=f"history_period_",
            output_dir=OUTPUT_DIR + '/history_period',
            use_sub_dir=True
        )    

    # Save each symbol's DataFrame into separate CSV files in a folder
    Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
        dataframes=fetched_df_period,
        filename_suffix=f"_history_period_",
        output_dir=OUTPUT_DIR + '/history_period',
        use_sub_dir=True
    )

def sample_fetch_from_start_end_date_and_save_to_csv_file():
    """Sample function to fetch data for a date range and save to CSV."""
    print(sample_fetch_from_start_end_date_and_save_to_csv_file.__name__)

    symbols = ['ACB', 'FPT']
    start_date = '2025-06-01'
    end_date = '2025-06-05'
    source = DEFAULT_SOURCE

    # Initialize the Fetcher with parameters
    fetcher = Fetcher(
            symbols=symbols,
            source=source,
            output_dir=OUTPUT_DIR + '/start_end_date'
        )
    
    # Fetch historical data for the specified symbols and date range
    fetched_df = fetcher.fetch_history_to_dataframe_from_start_end_date(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Save the fetched DataFrame to a CSV file
    Helpers.save_multiple_dataframes_to_single_csv(
            dataframes=fetched_df,
            filename_prefix=f"history_",
            output_dir=OUTPUT_DIR + '/history_start_end_date',
            use_sub_dir=True
        )    

    # Save each symbol's DataFrame into separate CSV files in a folder
    Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
        dataframes=fetched_df,
        filename_suffix=f"_history_",
        output_dir=OUTPUT_DIR + '/history_start_end_date',
        use_sub_dir=True
    )

def sample_calculator_moving_average():
    """Sample function to calculate moving averages."""
    # Fetch data
    fetcher = Fetcher(symbols='ACB', start_date='2023-12-01', end_date='2023-12-31')
    dataframes = fetcher.fetch_history_to_dataframe_from_start_end_date()

    acb_df = dataframes.get('ACB')

    if acb_df is not None and not acb_df.empty:
        # Calculate SMA
        sma_20_series = Calculator.calculate_moving_average(acb_df, window=20, price_column='close', ma_type='SMA')
        
        # Add it as a new column to the DataFrame
        if not sma_20_series.empty:
            acb_df['SMA_20'] = sma_20_series
            print("ACB DataFrame with SMA_20:")
            print(acb_df.tail())

        # Calculate EMA
        ema_10_series = Calculator.calculate_moving_average(acb_df, window=10, price_column='close', ma_type='EMA')
        if not ema_10_series.empty:
            acb_df['EMA_10'] = ema_10_series
            print("\nACB DataFrame with EMA_10:")
            print(acb_df.tail())
    else:
        print("ACB data is None or empty. Skipping save operation.")
        return

def sample_calculate_stock_performance_metrics_to_stock_object():
    """Sample function to calculate stock performance metrics."""
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
        # Display the DataFrame
        print("\nConsolidated Stock Performance Metrics:")
        print(metrics_df)

        # Save all metrics to a single CSV file
        csv_filepath = Helpers.save_single_dataframe_to_csv(
            df=metrics_df,
            filename_prefix="all_symbols_performance_metrics",
            output_dir=OUTPUT_DIR + '/stock_performance_metrics',
            use_sub_dir=True
        )
        print(f"\nAll stock performance metrics saved to: {csv_filepath}")

def sample_calculate_portfolio_performance_metrics():
    """Sample function to calculate portfolio performance metrics."""
    print(f"\nRunning: {sample_calculate_portfolio_performance_metrics.__name__}")

    portfolio_symbols = SYMBOLS_TH # Example portfolio
    start_date, end_date = Helpers.get_start_end_dates(1251)
    source = DEFAULT_SOURCE
    portfolio_name = "MyTechAndBankPortfolio"

    # Call the static method from the Portfolio class
    metrics_df = Portfolio.get_portfolio_metrics_df(
        symbols=portfolio_symbols,
        start_date=start_date,
        end_date=end_date,
        source=source,
        weights=None,
        name=portfolio_name
    )

    if metrics_df is not None and not metrics_df.empty:
        print(f"\nPortfolio Performance Metrics for {portfolio_name}:")
        if not metrics_df.empty:
            print(metrics_df.iloc[0])

        # Save portfolio metrics to a CSV file
        csv_filepath = Helpers.save_single_dataframe_to_csv(
            df=metrics_df,
            filename_prefix=f"portfolio_{portfolio_name}_performance_metrics",
            output_dir=OUTPUT_DIR + '/portfolio_performance_metrics',
            use_sub_dir=True
        )
        print(f"\nPortfolio performance metrics for {portfolio_name} saved to: {csv_filepath}")
    else:
        print(f"Could not calculate performance metrics for portfolio {portfolio_name}.")

if __name__ == "__main__":
    sample_fetch_periods_and_save_to_csv_file()
    sample_fetch_from_start_end_date_and_save_to_csv_file()
    # sample_calculator_moving_average()
    # sample_calculate_stock_performance_metrics_to_stock_object()
    # sample_calculate_portfolio_performance_metrics()