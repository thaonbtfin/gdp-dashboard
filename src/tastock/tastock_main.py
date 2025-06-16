import sys
import os
# print(os.getcwd())
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np # Added for np.nan

from src.tastock.fetcher import Fetcher
from src.tastock.stock import Stock
from src.tastock.portfolio import Portfolio
from src.tastock.helpers import Helpers
from src.constants import *
from src.tastock.calculator import Calculator

# output_dir = DEFAULT_output_dir + 'fetchedData/sample'
output_dir = 'data'

class Assistant:

    @staticmethod
    def fetch_history_data_and_save_to_csv_file(    # THIS IS GOING TO BE DELETED AS OUTDATE FOR USE
        period: int = 1251,
        symbols = SYMBOLS, 
        source = DEFAULT_SOURCE, 
        output_dir = DATA_DIR + "/historical_data",
        use_sub_dir = True,
        merged_filename_prefix = f"history",
        symbol_filename_suffix = f"_history",
        include_timestamp_in_filename = False
    ):
    # # def sample_fetch_periods_and_save_to_csv_file():

        print(f'\n--- Running symbols fetch executing from  {Assistant.fetch_history_data_and_save_to_csv_file.__name__} ---')
        print(f'THIS IS GOING TO BE DELETED AS OUTDATE FOR USE')

    #     # Initialize the Fetcher with parameters
    #     fetcher = Fetcher(
    #             symbols = symbols,
    #             source = source,
    #             output_dir = output_dir
    #         )
        
    #     # Fetch historical data for the given period (number of business days)
    #     fetched_df_period = fetcher.fetch_history_to_dataframe_for_periods(
    #         period = period,
    #         symbols = symbols
    #     )
    #     # print(f'{fetched_df_period}')  # Uncomment to inspect fetched data
        
    #     if not fetched_df_period or all(df.empty for df in fetched_df_period.values()):
    #         print(f"No data fetched or all dataframes are empty for symbols: {symbols} for period: {period} in fetch_history_data_and_save_to_csv_file. Skipping save.")
    #         return {} # Return empty dict if no data or all fetched dataframes are empty

    #     # Save the fetched DataFrame to a CSV file
    #     Helpers.save_multiple_dataframes_to_single_csv(
    #             dataframes = fetched_df_period,
    #             filename_prefix = merged_filename_prefix,
    #             output_dir = output_dir, # Uses the output_dir defined in sample.py
    #             use_sub_dir = use_sub_dir, # Saves directly into output_dir without creating a 'data_timestamp' subdir
    #             include_timestamp_in_filename = include_timestamp_in_filename
    #         )    

    #     # Save each symbol's DataFrame into separate CSV files in a folder
    #     Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
    #         dataframes = fetched_df_period,
    #         filename_suffix = symbol_filename_suffix,
    #         output_dir = output_dir, # Uses the output_dir defined in sample.py
    #         use_sub_dir = use_sub_dir, # Saves directly into output_dir without creating a 'data_timestamp' subdir
    #         include_timestamp_in_filename = include_timestamp_in_filename
    #     )

        # return fetched_df_period
        return print(f'THIS IS GOING TO BE DELETED AS OUTDATE FOR USE')

    @staticmethod
    def fetch_portfolios_data_and_save_to_csv(
    # def fetch_portfolios_data_and_calculate_performance_to_save_to_csv(
        portfolios_map: dict, # Key: portfolio_name (str), Value: list_of_symbols (List[str])
        period: int = 1251,
        source: str = DEFAULT_SOURCE,
        base_output_dir: str = output_dir, # Default to module-level 'data'
        use_sub_dir_for_portfolio_folders: bool = False, # If True: Creates 'base_output_dir/portfolio_name/'
        use_sub_dir_for_timestamp_folders: bool = False, # If True: Passed to child func, creates '.../data_timestamp/'
        include_timestamp_in_filenames: bool = False
    ):
        """
        Fetches history data for multiple portfolios, saves CSV files for each,
        and returns a dictionary of DataFrames.

        Args:
            portfolios_map (dict): A dictionary where keys are portfolio names (str)
                                   and values are lists of stock symbols (List[str]).
            period (int): Number of business days for history.
            source (str): Data source.
            base_output_dir (str): The root directory where portfolio data will be saved.
                                   Each portfolio's data will be in a subdirectory named after the portfolio key.
            use_sub_dir_for_portfolio_folders (bool): If True, creates a subdirectory
                                                      under base_output_dir for each portfolio.
                                                      Files will be saved in 'base_output_dir/portfolio_name/'.
                                                      If False, all portfolio files are saved directly under
                                                      base_output_dir (potentially mixed if not careful with prefixes).
            use_sub_dir_for_timestamp_folders (bool): If True, creates a timestamped subdirectory
                                                       (e.g., 'data_YYYYMMDD_HHMMSS') within each
                                                       portfolio's effective output directory for the actual data files.
            include_timestamp_in_filenames (bool): If True, includes a timestamp in the
                                                   generated CSV filenames.

        Returns:
            dict: A dictionary where keys are portfolio names and values are
                  the dictionaries of DataFrames ({symbol: DataFrame}) for that portfolio.
                  Returns None for a portfolio if an error occurred or it was skipped.
        """

        all_portfolios_returned_data = {}
        print(f"\n--- Starting optimized batch fetch for {len(portfolios_map)} portfolio(s). ---")

        # 1. Collect all unique symbols from all portfolios
        all_unique_symbols = set()
        for symbols_list_for_portfolio in portfolios_map.values():
            if isinstance(symbols_list_for_portfolio, list) and symbols_list_for_portfolio:
                all_unique_symbols.update(symbols_list_for_portfolio)
        
        unique_symbols_list = list(all_unique_symbols)

        if not unique_symbols_list:
            print("No unique symbols found across all portfolios. Nothing to fetch.")
            for portfolio_name in portfolios_map.keys():
                all_portfolios_returned_data[portfolio_name] = {}
            return all_portfolios_returned_data

        print(f"Found {len(unique_symbols_list)} unique symbol(s) to fetch: {unique_symbols_list}")

        # 2. Fetch data for all unique symbols once
        master_fetcher = Fetcher(
            symbols=unique_symbols_list, # Initialize Fetcher with all unique symbols
            source=source,
            # output_dir for Fetcher instance is not critical here as saving is handled later by Helpers
            output_dir=base_output_dir 
        )
        master_fetched_data = master_fetcher.fetch_history_to_dataframe_for_periods(
            period=period,
            symbols=unique_symbols_list # Explicitly pass symbols here too
        )

        if not master_fetched_data or all(df.empty for df in master_fetched_data.values()):
            print(f"Failed to fetch data for unique symbols or all data was empty. Aborting portfolio processing.")
            for portfolio_name in portfolios_map.keys():
                all_portfolios_returned_data[portfolio_name] = {} # Indicate no data
            return all_portfolios_returned_data
        
        print(f"Successfully fetched data for {len(master_fetched_data)} unique symbol(s).")

        # Save historical data for all unique symbols to a single CSV file
        # This file will be saved in the timestamped base_output_dir.
        if master_fetched_data and not all(df.empty for df in master_fetched_data.values()):
            print(f"\nSaving historical data for all {len(master_fetched_data)} unique fetched symbols to a single CSV...")
            Helpers.save_multiple_dataframes_to_single_csv(
                dataframes=master_fetched_data,
                filename_prefix="history_data_symbols", # Descriptive prefix
                output_dir=base_output_dir, # This is the timestamped directory from the caller
                use_sub_dir=False, # Save directly in base_output_dir
                include_timestamp_in_filename=include_timestamp_in_filenames # Consistent with other files
            )
        else:
            print("Skipping save of all unique symbols history CSV as no master data was fetched or all was empty.")

        # 4. Calculate and save intrinsic values for all unique symbols
        Assistant.calculate_and_save_intrinsic_values(
            symbols_list=unique_symbols_list,
            period_for_stock_init=period, # Use the same period for Stock class date context
            source=source,
            output_dir_for_intrinsic_csv=base_output_dir, # Save at the root of the batch output
            use_sub_dir_for_timestamp=use_sub_dir_for_timestamp_folders,
            include_timestamp_in_filename=include_timestamp_in_filenames
        )

        # 3. Process each portfolio for saving using the master fetched data
        for portfolio_name, symbols_list_for_portfolio in portfolios_map.items():
            if not isinstance(symbols_list_for_portfolio, list) or not symbols_list_for_portfolio:
                print(f"Skipping portfolio '{portfolio_name}': symbol list is empty or not a list.")
                # all_portfolios_fetched_data[portfolio_name] = {} # Store empty dict for skipped/empty
                all_portfolios_returned_data[portfolio_name] = {}
                continue

            # print(f"\nProcessing portfolio: '{portfolio_name}' with symbols: {symbols_list}")
            print(f"\nProcessing and saving for portfolio executing from '{portfolio_name}' with symbols: {symbols_list_for_portfolio}")

            # Filter data for the current portfolio from the master fetched data
            dataframes_for_current_portfolio = {
                sym: master_fetched_data[sym]
                for sym in symbols_list_for_portfolio
                if sym in master_fetched_data and not master_fetched_data[sym].empty
            }

            if not dataframes_for_current_portfolio:
                print(f"No valid data available for symbols in portfolio '{portfolio_name}' from the master fetch. Skipping save.")
                all_portfolios_returned_data[portfolio_name] = {}
                continue

            current_portfolio_target_dir = base_output_dir
            if use_sub_dir_for_portfolio_folders:
                current_portfolio_target_dir = os.path.join(base_output_dir, portfolio_name)
            
            # Ensure the directory exists. Helpers.save_* methods also create directories.
            # os.makedirs(current_portfolio_target_dir, exist_ok=True)

            portfolio_specific_merged_prefix = f"history_{portfolio_name}"
            # portfolio_specific_symbol_suffix = f"_{portfolio_name}_history"
            portfolio_specific_symbol_suffix = f"_{portfolio_name}_history" # Suffix for individual files if saved

            try:
                merged_csv_filepath = Helpers.save_multiple_dataframes_to_single_csv(
                    dataframes=dataframes_for_current_portfolio,
                    filename_prefix=portfolio_specific_merged_prefix,
                    output_dir=current_portfolio_target_dir,
                    use_sub_dir=use_sub_dir_for_timestamp_folders,
                    include_timestamp_in_filename=include_timestamp_in_filenames
                )

                # Optionally, save individual symbol files (if still needed)
                Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
                    dataframes=dataframes_for_current_portfolio,
                    filename_suffix=portfolio_specific_symbol_suffix,
                    output_dir=current_portfolio_target_dir + "/symbols",   # save to sub-folder
                    use_sub_dir=use_sub_dir_for_timestamp_folders,
                    include_timestamp_in_filename=include_timestamp_in_filenames
                )

                # After saving the merged CSV, calculate and save its performance
                if merged_csv_filepath and os.path.exists(merged_csv_filepath):
                    print(f"Calculating performance for portfolio '{portfolio_name}' from CSV: {merged_csv_filepath}")
                    # performance_report_output_dir = os.path.join(current_portfolio_target_dir, "performance_reports")
                    # Ensure the performance report directory exists
                    # os.makedirs(performance_report_output_dir, exist_ok=True)
                    
                    Assistant.calculate_portfolio_performance_from_csv(
                        historical_data_csv_path=merged_csv_filepath,
                        portfolio_name=portfolio_name, # Use the original portfolio name
                        # weights=None, # Default to equal weights, or pass specific weights if available
                        # output_dir=performance_report_output_dir,
                        # metrics_filename_prefix="perf", # Filename prefix for the report
                        output_dir=current_portfolio_target_dir, # Save in the same folder as history CSV
                        metrics_filename_prefix=f"perf_{portfolio_name}", # Filename prefix for the report
                        include_timestamp_in_filename=True # Or False, depending on preference
                    )
                else:
                    print(f"Skipping performance calculation for '{portfolio_name}' as merged CSV path is invalid or file not found.")

                all_portfolios_returned_data[portfolio_name] = dataframes_for_current_portfolio
                print(f"Successfully processed and saved data for portfolio: '{portfolio_name}'.")
            except Exception as e:
                # print(f"Error processing portfolio '{portfolio_name}': {e}")
                # all_portfolios_fetched_data[portfolio_name] = None # Indicate failure
                print(f"Error saving data for portfolio '{portfolio_name}': {e}")
                all_portfolios_returned_data[portfolio_name] = None # Indicate failure for this portfolio

        print(f"\nBatch fetch completed for all {len(portfolios_map)} portfolio(s).")
        # return all_portfolios_fetched_data
        return all_portfolios_returned_data

    @staticmethod
    def fetch_portfolios_data_and_calculate_performance_to_save_to_csv(portfolios=PORTFOLIOS):

        print(f'\n--- Running batch portfolio fetch from {Assistant.fetch_portfolios_data_and_calculate_performance_to_save_to_csv.__name__} ---')
        
        portfolios_to_process = portfolios

        all_portfolios_data = Assistant.fetch_portfolios_data_and_save_to_csv(
            portfolios_map = portfolios_to_process,
            period = 10,  # Using a short period for faster testing
            # base_output_dir = "data/batch_portfolio_data", # Custom base directory for this batch run
            base_output_dir = DATA_DIR + "/historical_data/" + Helpers.name_today_datetime(), # Custom base directory for this batch run
            # use_sub_dir_for_portfolio_folders = True, # Creates 'base_output_dir/portfolio_name/'
            # use_sub_dir_for_timestamp_folders = True, # Creates '.../data_timestamp/' inside each portfolio folder
            use_sub_dir_for_portfolio_folders = True, # Creates 'base_output_dir/portfolio_name/' (Correct)
            use_sub_dir_for_timestamp_folders = False, # Save files directly under 'portfolio_name' folder
            include_timestamp_in_filenames = True
        )

        print("\n--- Batch Fetch Results Summary ---")
        if all_portfolios_data:
            for portfolio_name, data_frames_dict in all_portfolios_data.items():
                if data_frames_dict is not None and data_frames_dict: # Check if not None and not empty
                    print(f"Portfolio '{portfolio_name}': Fetched data for symbols {list(data_frames_dict.keys())}")
                    # Example: print head of the first symbol's DataFrame in this portfolio
                    # first_symbol = list(data_frames_dict.keys())[0]
                    # print(f"  Data for {first_symbol}:\n{data_frames_dict[first_symbol].head(2)}")
                elif data_frames_dict == {}: # Explicitly empty, e.g. from empty symbol list
                    print(f"Portfolio '{portfolio_name}': No data fetched (e.g., symbol list was empty).")
                else: # Was None, indicating an error during processing
                    print(f"Portfolio '{portfolio_name}': Failed to fetch data or an error occurred.")
        else:
            print("No data returned from batch fetch process.")

    @staticmethod
    def calculate_portfolio_performance_from_csv(
        historical_data_csv_path: str,
        portfolio_name: str = "PortfolioFromCSV",
        weights: list = None, # Optional: if None, Portfolio will use equal weights
        # output_dir: str = "data/reports",
        output_dir: str = REPORTS_DIR,
        metrics_filename_prefix: str = "perf",
        include_timestamp_in_filename: bool = True
    ):
        """
        Reads historical stock data from a CSV file, calculates portfolio performance,
        and saves the metrics to another CSV file.

        Args:
            historical_data_csv_path (str): Path to the input CSV file.
                                            Expected format: 'time' column, and other columns
                                            representing stock symbols with their close prices.
            portfolio_name (str): Name for the portfolio.
            weights (list, optional): List of weights for each symbol. Defaults to equal weights.
            output_dir (str): Directory to save the performance metrics CSV.
            metrics_filename_prefix (str): Prefix for the output metrics CSV file.
            include_timestamp_in_filename (bool): Whether to include a timestamp in the metrics filename.

        Returns:
            pd.DataFrame: The DataFrame containing the calculated portfolio performance metrics,
                          or an empty DataFrame if an error occurs.
        """
        print(f"\n--- Running portfolio performance calculation from CSV: {historical_data_csv_path} ---")
        try:
            raw_df = pd.read_csv(historical_data_csv_path)
        except FileNotFoundError:
            print(f"Error: Historical data CSV file not found at {historical_data_csv_path}")
            return pd.DataFrame()

        if 'time' not in raw_df.columns:
            print("Error: 'time' column not found in the historical data CSV.")
            return pd.DataFrame()

        # Prepare data for Portfolio class: dict of {symbol: DataFrame_with_time_and_close}
        fetched_data = {}
        symbols = [col for col in raw_df.columns if col != 'time']

        if not symbols:
            print("Error: No symbol columns found in the historical data CSV (besides 'time').")
            return pd.DataFrame()

        for symbol in symbols:
            # Ensure 'time' is in a consistent format if needed, though Portfolio handles datetime conversion
            # For Portfolio, each symbol's DataFrame needs 'time' and 'close' columns.
            symbol_df = raw_df[['time', symbol]].copy()
            symbol_df.rename(columns={symbol: 'close'}, inplace=True)
            fetched_data[symbol] = symbol_df

        # Instantiate Portfolio with pre-fetched data
        # start_date and end_date are not strictly needed here as data is provided
        portfolio_obj = Portfolio(
            symbols=symbols,
            fetched_data=fetched_data,
            weights=weights,
            name=portfolio_name
        )

        # metrics_df = portfolio_obj.get_portfolio_metrics_df(symbols, None, None, fetched_data=fetched_data, weights=weights, name=portfolio_name)
        metrics_data = portfolio_obj.get_performance_metrics() # This returns a dict or None
        
        # if not metrics_df.empty:
        if metrics_data:
            metrics_df = pd.DataFrame([metrics_data])
            # Add portfolio_name as the first column, using the name from the portfolio object
            metrics_df.insert(0, 'portfolio_name', portfolio_obj.get_name())
        else:
            metrics_df = pd.DataFrame() # Empty DataFrame if no metrics were calculated
        
        if not metrics_df.empty: # Check if metrics_df was successfully created
            # output_filename = f"{metrics_filename_prefix}_{portfolio_name}"
            output_filename = metrics_filename_prefix # metrics_filename_prefix now includes portfolio_name
            Helpers.save_single_dataframe_to_csv(
                df=metrics_df,
                filename_prefix=output_filename,
                # output_dir=output_dir,
                output_dir=output_dir, # This will be current_portfolio_target_dir
                use_sub_dir=False, # Save directly in output_dir
                include_timestamp_in_filename=include_timestamp_in_filename
            )
            print(f"Portfolio performance metrics for '{portfolio_name}' saved.")
        else:
            print(f"Could not calculate performance metrics for portfolio '{portfolio_name}'.")
        
        return metrics_df

    @staticmethod
    def calculate_and_save_intrinsic_values(
        symbols_list: list,
        period_for_stock_init: int,
        source: str = DEFAULT_SOURCE,
        output_dir_for_intrinsic_csv: str = output_dir,
        use_sub_dir_for_timestamp: bool = False,
        include_timestamp_in_filename: bool = True,
        filename_prefix: str = "intrinsic_value_symbols"
    ):
        """
        Calculates Graham intrinsic value for a list of symbols and saves them to a CSV file.
        The Stock class's _fetch_and_calculate_intrinsic_value is called during its instantiation.

        Args:
            symbols_list (list): List of stock symbols.
            period_for_stock_init (int): The period (number of days) to determine start/end dates
                                         for Stock object instantiation. These dates are primarily
                                         for the Stock object's historical price fetching context;
                                         intrinsic value relies on latest financial ratios.
            source (str): Data source for vnstock.
            output_dir_for_intrinsic_csv (str): Directory to save the intrinsic value CSV.
            use_sub_dir_for_timestamp (bool): Whether to use a timestamped subdirectory for the CSV.
            include_timestamp_in_filename (bool): Whether to include a timestamp in the CSV filename.
            filename_prefix (str): Prefix for the intrinsic value CSV file.
        """
        print(f"\n--- Calculating and Saving Intrinsic Values for {len(symbols_list)} symbol(s) ---")
        all_symbols_intrinsic_data = []
        
        # Determine start/end dates for Stock class instantiation context
        start_date_stock_init, end_date_stock_init = Helpers.get_start_end_dates(period=period_for_stock_init)

        for symbol in symbols_list:
            print(f"Processing intrinsic value for: {symbol}")
            try:
                stock_obj = Stock(
                    symbol=symbol,
                    start_date=start_date_stock_init,
                    end_date=end_date_stock_init,
                    source=source
                )
                intrinsic_value = stock_obj.get_intrinsic_value_graham()
                all_symbols_intrinsic_data.append({
                    'symbol': symbol,
                    # 'graham_intrinsic_value': f"{intrinsic_value:,.2f}" if intrinsic_value is not None and pd.notna(intrinsic_value) else "N/A"
                    'graham_intrinsic_value': intrinsic_value if intrinsic_value is not None and pd.notna(intrinsic_value) else np.nan # Save as number or NaN
                })
            except Exception as e:
                print(f"Error calculating intrinsic value for {symbol}: {e}")
                all_symbols_intrinsic_data.append({'symbol': symbol, 'graham_intrinsic_value': "Error"})

        if all_symbols_intrinsic_data:
            intrinsic_df = pd.DataFrame(all_symbols_intrinsic_data)
            Helpers.save_single_dataframe_to_csv(
                df=intrinsic_df,
                filename_prefix=filename_prefix,
                output_dir=output_dir_for_intrinsic_csv,
                use_sub_dir=use_sub_dir_for_timestamp,
                include_timestamp_in_filename=include_timestamp_in_filename
            )
            print(f"Intrinsic values for all unique symbols saved.")
        else:
            print("No intrinsic value data to save.")
        
        return pd.DataFrame(all_symbols_intrinsic_data) if all_symbols_intrinsic_data else pd.DataFrame()

if __name__ == "__main__":
    # --- Fetch batch portfolios and save their raw history data ---
    # This method orchestrates several actions for a collection of portfolios (e.g., PORTFOLIOS_TEST):
    # 1. Fetches historical stock data for all unique symbols across all defined portfolios.
    # 2. For each portfolio:
    #    a. Saves a merged CSV of historical data for all its symbols (e.g., 'data/historical_data/YYYYMMDD_HHMM/VN30/history_VN30_timestamp.csv').
    #    b. Saves individual CSV files for each symbol within that portfolio's folder (e.g., 'data/historical_data/YYYYMMDD_HHMM/VN30/symbols/ACB_VN30_history_timestamp.csv').
    #    c. Calculates performance metrics based on the merged historical data and saves these metrics to a CSV (e.g., 'data/historical_data/YYYYMMDD_HHMM/VN30/perf_VN30_timestamp.csv').
    # 3. Calculates Graham intrinsic values for all unique symbols fetched and saves them to a single CSV file (e.g., 'data/historical_data/YYYYMMDD_HHMM/intrinsic_value_symbols_timestamp.csv').
    # The PORTFOLIOS_TEST input is a dictionary like:
    #   PORTFOLIOS_TEST = {"VN30": ['ACB', 'BCM'], "VN100": ['AAA', 'ACB'], ...}
    # The method primarily produces side effects (creating files) and prints summaries to the console.
    # It internally calls `fetch_portfolios_data_and_save_to_csv` which returns a dictionary mapping portfolio names to dictionaries of fetched DataFrames ({symbol: DataFrame}), or None/empty dict if errors/no data.
    Assistant.fetch_portfolios_data_and_calculate_performance_to_save_to_csv(PORTFOLIOS_TEST)
    # Assistant.fetch_portfolios_data_and_calculate_performance_to_save_to_csv(PORTFOLIOS_TEST["VN30"])
