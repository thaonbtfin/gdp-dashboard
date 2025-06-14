import sys
import os
# print(os.getcwd())
sys.path.insert(0, os.getcwd())

import pandas as pd

from src.tastock.fetcher import Fetcher
from src.tastock.stock import Stock
from src.tastock.portfolio import Portfolio
from src.tastock.helpers import Helpers
from src.constants import DEFAULT_SOURCE, SYMBOLS, SYMBOLS_DH, SYMBOLS_TH, SYMBOLS_VN30, PORTFOLIOS
from src.tastock.calculator import Calculator

# output_dir = DEFAULT_output_dir + 'fetchedData/sample'
output_dir = 'data'

class Assistant:

    @staticmethod
    def fetch_history_data_and_save_to_csv_file(
        period: int = 1251,
        symbols = SYMBOLS, 
        source = DEFAULT_SOURCE, 
        output_dir = output_dir,
        use_sub_dir = True,
        merged_filename_prefix = f"history",
        symbol_filename_suffix = f"_history",
        include_timestamp_in_filename = True
    ):
    # def sample_fetch_periods_and_save_to_csv_file():

        print(f'Running {Assistant.fetch_history_data_and_save_to_csv_file.__name__}')

        # Initialize the Fetcher with parameters
        fetcher = Fetcher(
                symbols = symbols,
                source = source,
                output_dir = output_dir
            )
        
        # Fetch historical data for the given period (number of business days)
        fetched_df_period = fetcher.fetch_history_to_dataframe_for_periods(
            period = period,
            symbols = symbols
        )
        # print(f'{fetched_df_period}')  # Uncomment to inspect fetched data
        
        if not fetched_df_period or all(df.empty for df in fetched_df_period.values()):
            print(f"No data fetched or all dataframes are empty for symbols: {symbols} for period: {period} in fetch_history_data_and_save_to_csv_file. Skipping save.")
            return {} # Return empty dict if no data or all fetched dataframes are empty

        # Save the fetched DataFrame to a CSV file
        Helpers.save_multiple_dataframes_to_single_csv(
                dataframes = fetched_df_period,
                filename_prefix = merged_filename_prefix,
                output_dir = output_dir, # Uses the output_dir defined in sample.py
                use_sub_dir = use_sub_dir, # Saves directly into output_dir without creating a 'data_timestamp' subdir
                include_timestamp_in_filename = include_timestamp_in_filename
            )    

        # Save each symbol's DataFrame into separate CSV files in a folder
        Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
            dataframes = fetched_df_period,
            filename_suffix = symbol_filename_suffix,
            output_dir = output_dir, # Uses the output_dir defined in sample.py
            use_sub_dir = use_sub_dir, # Saves directly into output_dir without creating a 'data_timestamp' subdir
            include_timestamp_in_filename = include_timestamp_in_filename
        )

        return fetched_df_period

    @staticmethod
    def fetch_portfolios_data_and_save_to_csv(
        portfolios_map: dict, # Key: portfolio_name (str), Value: list_of_symbols (List[str])
        period: int = 1251,
        source: str = DEFAULT_SOURCE,
        base_output_dir: str = output_dir, # Default to module-level 'data'
        use_sub_dir_for_portfolio_folders: bool = True, # Creates 'base_output_dir/portfolio_name/'
        use_sub_dir_for_timestamp_folders: bool = True, # Passed to child func, creates '.../data_timestamp/'
        include_timestamp_in_filenames: bool = True
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
        # all_portfolios_fetched_data = {}
        # print(f"Starting batch fetch for {len(portfolios_map)} portfolio(s).")

        # for portfolio_name, symbols_list in portfolios_map.items():
        #     if not isinstance(symbols_list, list) or not symbols_list:
                
        all_portfolios_returned_data = {}
        print(f"Starting optimized batch fetch for {len(portfolios_map)} portfolio(s).")

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

        # 3. Process each portfolio for saving using the master fetched data
        for portfolio_name, symbols_list_for_portfolio in portfolios_map.items():
            if not isinstance(symbols_list_for_portfolio, list) or not symbols_list_for_portfolio:
                print(f"Skipping portfolio '{portfolio_name}': symbol list is empty or not a list.")
                # all_portfolios_fetched_data[portfolio_name] = {} # Store empty dict for skipped/empty
                all_portfolios_returned_data[portfolio_name] = {}
                continue

            # print(f"\nProcessing portfolio: '{portfolio_name}' with symbols: {symbols_list}")
            print(f"\nProcessing and saving for portfolio: '{portfolio_name}' with symbols: {symbols_list_for_portfolio}")

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
            os.makedirs(current_portfolio_target_dir, exist_ok=True)

            portfolio_specific_merged_prefix = f"history_{portfolio_name}"
            portfolio_specific_symbol_suffix = f"_{portfolio_name}_history"

            try:
                # fetched_data_for_current_portfolio = Assistant.fetch_history_data_and_save_to_csv_file(
                #     period=period,
                #     symbols=symbols_list,
                #     source=source,
                #     output_dir=current_portfolio_target_dir,
                #     use_sub_dir=use_sub_dir_for_timestamp_folders,
                #     merged_filename_prefix=portfolio_specific_merged_prefix,
                #     symbol_filename_suffix=portfolio_specific_symbol_suffix,
                #     include_timestamp_in_filename=include_timestamp_in_filenames
                Helpers.save_multiple_dataframes_to_single_csv(
                    dataframes=dataframes_for_current_portfolio,
                    filename_prefix=portfolio_specific_merged_prefix,
                    output_dir=current_portfolio_target_dir,
                    use_sub_dir=use_sub_dir_for_timestamp_folders,
                    include_timestamp_in_filename=include_timestamp_in_filenames
                )
                # all_portfolios_fetched_data[portfolio_name] = fetched_data_for_current_portfolio
                Helpers.save_multiple_dataframes_to_multiple_csv_files_in_directory(
                    dataframes=dataframes_for_current_portfolio,
                    filename_suffix=portfolio_specific_symbol_suffix,
                    output_dir=current_portfolio_target_dir,
                    use_sub_dir=use_sub_dir_for_timestamp_folders,
                    include_timestamp_in_filename=include_timestamp_in_filenames
                )
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
    def fetch_batch_portfolios_and_save_to_csv(portfolios=PORTFOLIOS):
        # Example of fetching a single default portfolio (original behavior)
        # print("--- Running single portfolio fetch (default SYMBOLS from method signature) ---")
        # default_data = Assistant.fetch_history_data_and_save_to_csv_file(period=10) # Short period for test
        # if default_data:
        #     print(f"Fetched data for default symbols: {list(default_data.keys())}")

        print("\n--- Running batch portfolio fetch ---")
        
        portfolios_to_process = portfolios

        all_portfolios_data = Assistant.fetch_portfolios_data_and_save_to_csv(
            portfolios_map = portfolios_to_process,
            period = 10,  # Using a short period for faster testing
            base_output_dir = "data/batch_portfolio_data", # Custom base directory for this batch run
            use_sub_dir_for_portfolio_folders = True, # Creates 'base_output_dir/portfolio_name/'
            use_sub_dir_for_timestamp_folders = True, # Creates '.../data_timestamp/' inside each portfolio folder
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
    
    

if __name__ == "__main__":
    Assistant.fetch_history_data_and_save_to_csv_file()
    # Assistant.fetch_batch_portfolios_and_save_to_csv()

    