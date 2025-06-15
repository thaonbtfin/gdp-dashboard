import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from datetime import datetime, timedelta
from src.constants import DEFAULT_OUTPUT_DIR, DEFAULT_PERIOD, DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_USE_SUB_DIR

class Helpers():    
    """
    A collection of helper functions for data processing and file management.
    """
    # This class is primarily used as a namespace for static methods

    # Example usage (commented out)

    # @staticmethod
    # def format_date(date):
    #     return date.strftime("%Y-%m-%d")

    # @staticmethod
    # def calculate_age(birthdate):
    #     from datetime import datetime
    #     today = datetime.today()
    #     age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    #     return age

    @staticmethod
    def create_output_dir(base_output_dir, use_sub_dir=True):
        """
        Create and return the output directory path.
        If use_sub_dir is True, create a subdirectory with the current timestamp.
        """
        now_str = datetime.now().strftime('%Y%m%d')
        # now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        # now_str = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
        if use_sub_dir:
            final_output_dir = os.path.join(base_output_dir, f'data_{now_str}')
        else:
            final_output_dir = base_output_dir
        os.makedirs(final_output_dir, exist_ok=True)
        print(f"Directory created: {final_output_dir}")
        return final_output_dir

    # @staticmethod
    def name_today_datetime():
        """
        Return the current date and time as a string in 'YYYYMMDD_HHMM' format.
        """
        # return datetime.now().strftime('%Y%m%d_%H%M')
        return datetime.now().strftime('%Y%m%d')

    # @staticmethod
    def get_start_end_dates(period=DEFAULT_PERIOD):
        """
        Returns START_DATE and END_DATE as strings in 'YYYY-MM-DD' format.
        END_DATE is last weekday (Friday if today is Sat/Sun).
        START_DATE is END_DATE minus `periods` weekdays.
        """
        today = datetime.today()
        if today.weekday() == 5:  # Saturday
            end_date = today - timedelta(days=1)
        elif today.weekday() == 6:  # Sunday
            end_date = today - timedelta(days=2)
        else:
            end_date = today - timedelta(days=1)

        # Calculate the start date by subtracting the number of weekdays (period) from the end date
        start_date = pd.bdate_range(end=end_date, periods=period, freq='B')[0]  # Get the last date in the range

        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    @staticmethod
    def get_periods_between_start_end_dates(start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        """
        
        """
        # Generate business days between the two dates (inclusive)
        weekdays = pd.bdate_range(start=start_date, end=end_date)
        if not weekdays.empty:
            periods = len(weekdays)
        else:
            periods = 0
        return periods

    @staticmethod
    def read_csv(csv_filepath):
        """
        Read a CSV file and return its DataFrame.
        """
        return pd.read_csv(csv_filepath)

    @staticmethod
    def save_dataframes_to_csv_files(dataframes, output_dir=None, use_sub_dir=True, sort_by_time=True):
            """
            Save each DataFrame in the dataframes dict to a CSV file in the output directory.
            - Removes '-' from the 'time' column if present.
            - Sorts the DataFrame so the latest date is at the top (descending by 'time').
            - Saves each DataFrame to a CSV file named '{symbol}_{source}_history.csv'.

            Args:
            dataframes (dict): Dictionary of {symbol: DataFrame}.
            output_dir (str): Base output directory.
            use_sub_dir (bool): Whether to use a timestamped subdirectory.
            sort_by_time (bool): Sort descending by time.

            Returns:
                str: Path to the output directory containing the saved CSV files.
            """
            final_output_dir = Helpers.create_output_dir(output_dir, use_sub_dir)

            for key, df in dataframes.items():
                symbol = key if isinstance(key, str) else key[0]
                filename = f"{symbol.lower()}_history.csv"
                filepath = os.path.join(final_output_dir, filename)

                if 'time' in df.columns:
                    df['time'] = df['time'].astype(str).str.replace('-', '', regex=False)
                    df = df.sort_values('time', ascending=not sort_by_time).reset_index(drop=True)

                df.to_csv(filepath, index=False)
                print(f"Saved {symbol} data to {filepath}")

            return final_output_dir

    @staticmethod
    def save_dataframes_to_csv_file(dataframes, csv_filepath=None, sort_by_time=True):
        """
        Save the merged DataFrame to a single CSV file.
        Returns the csv_filepath.
        """
        # Create the output directory (with subdirectory if needed)
        if not csv_filepath:
            # If no filepath provided, create one based on base_output_dir and use_sub_dir
            final_output_dir = Helpers.create_output_dir(DEFAULT_OUTPUT_DIR, DEFAULT_USE_SUB_DIR)
            # Use a default filename if not provided
            csv_filepath = os.path.join(final_output_dir, f"history_prices.csv")
        else:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

        # Merge on 'time' column
        dfs = []
        for key, df in dataframes.items():
            symbol = key if isinstance(key, str) else key[0]
            # If 'time' column exists, format it and sort descending (sort_by_time=True)
            if 'time' in df.columns:
                df = df[['time', 'close']].copy()
                # Remove '-' from date strings
                df['time'] = df['time'].astype(str).str.replace('-', '', regex=False)
                # Sort so latest date is at the top
                df = df.sort_values('time', ascending=sort_by_time).reset_index(drop=True)
                df = df.rename(columns={'close': symbol})
                dfs.append(df.set_index('time'))
        if dfs:
            df_merged = pd.concat(dfs, axis=1, join='outer').reset_index()
            df_merged = df_merged.sort_values('time', ascending=False)
        else:
            df_merged = pd.DataFrame()

        df_merged.to_csv(csv_filepath, index=False)
        print(f"Saved dataframes to {csv_filepath}")

        return csv_filepath

    @staticmethod
    def save_multiple_dataframes_to_multiple_csv_files_in_directory(
        dataframes: dict,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        use_sub_dir: bool = True,
        filename_prefix_map: dict = None,
        filename_suffix: str = "",
        include_timestamp_in_filename: bool = True,
        index: bool = False
    ) -> str:
        """
        Saves multiple DataFrames from a dictionary to individual CSV files
        with flexible naming and directory options.

        Args:
            dataframes (dict): Dictionary of {key: DataFrame}.
            output_dir (str): The primary directory where files will be saved.
            use_sub_dir (bool): If True, creates a timestamped subdirectory within 'output_dir'.
                                If False, uses 'output_dir' directly.
            filename_prefix_map (dict, optional): A map of {key_from_dataframes: custom_prefix}.
                                                  If a key is not found or map is None,
                                                  the key from dataframes dict is used as prefix.
            filename_suffix (str): A suffix to append to the filename before the timestamp and extension.
                                   Example: "_data" -> prefix_data_timestamp.csv.
                                   Ensure it starts with '_' or similar if separation is desired.
            include_timestamp_in_filename (bool): If True, appends a timestamp to each filename.
            index (bool): Whether to write DataFrame index as a column in the CSV.

        Returns:
            str: The full path to the target directory where files were (or would be) saved.
        """
        target_dir = Helpers.create_output_dir(output_dir, use_sub_dir=use_sub_dir)

        if not dataframes:
            print(f"No dataframes provided. Target directory is: {target_dir}")
            return target_dir

        timestamp_str_base = Helpers.name_today_datetime()

        for key, df_item in dataframes.items():
            if not isinstance(df_item, pd.DataFrame):
                print(f"Warning: Item for key '{key}' is not a DataFrame. Skipping.")
                continue

            current_prefix = str(filename_prefix_map.get(key, key)) if filename_prefix_map else str(key)
            safe_prefix = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in current_prefix)
            processed_suffix = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in filename_suffix) if filename_suffix else ""
            timestamp_part = f"_{timestamp_str_base}" if include_timestamp_in_filename else ""
            
            csv_filename = f"{safe_prefix}{processed_suffix}{timestamp_part}.csv"
            csv_filepath = os.path.join(target_dir, csv_filename)

            df_item.to_csv(csv_filepath, index=index)
            print(f"DataFrame for key '{key}' saved to: {csv_filepath}")
        return target_dir

    @staticmethod
    def save_multiple_dataframes_to_single_csv(
        dataframes: dict,
        filename_prefix: str,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        use_sub_dir: bool = True,
        include_timestamp_in_filename: bool = True,
        sort_by_time: bool = True,
        index: bool = False
    ) -> str:
        """
        Merges multiple DataFrames from a dictionary into a single DataFrame
        and saves it to a CSV file with flexible naming and directory options.
        Each key in the dataframes dict is used as the column name for 'close' prices.

        Args:
            dataframes (dict): Dictionary of {symbol: DataFrame}. Each DataFrame must
                               have 'time' and 'close' columns.
            filename_prefix (str): Prefix for the CSV filename (e.g., "merged_stock_data").
            output_dir (str): The primary directory where the file will be saved.
            use_sub_dir (bool): If True, creates a timestamped subdirectory within 'output_dir'.
            include_timestamp_in_filename (bool): If True, appends a timestamp to the filename.
            sort_by_time (bool): If True, sorts the merged DataFrame by the 'time' column descending.
            index (bool): Whether to write DataFrame index as a column in the CSV.

        Returns:
            str: The full path to the saved CSV file.
        """
        target_dir = Helpers.create_output_dir(output_dir, use_sub_dir=use_sub_dir) if use_sub_dir else output_dir
        if not use_sub_dir: # Ensure base output_dir exists if not using sub_dir
            os.makedirs(target_dir, exist_ok=True)

        timestamp_str = f"_{Helpers.name_today_datetime()}" if include_timestamp_in_filename else ""
        csv_filename = f"{filename_prefix}{timestamp_str}.csv"
        csv_filepath = os.path.join(target_dir, csv_filename)

        # Merge on 'time' column
        dfs_to_merge = []
        for key, df_item in dataframes.items():
            symbol = key if isinstance(key, str) else str(key) # Ensure symbol is a string
            if 'time' in df_item.columns and 'close' in df_item.columns:
                processed_df = df_item[['time', 'close']].copy()
                processed_df['time'] = processed_df['time'].astype(str).str.replace('-', '', regex=False)
                # Sorting individual DFs before merge isn't strictly necessary if final merge is sorted
                processed_df = processed_df.rename(columns={'close': symbol})
                dfs_to_merge.append(processed_df.set_index('time'))
        
        df_merged = pd.DataFrame()
        if dfs_to_merge:
            df_merged = pd.concat(dfs_to_merge, axis=1, join='outer').reset_index()
            if sort_by_time and 'time' in df_merged.columns:
                df_merged = df_merged.sort_values('time', ascending=False).reset_index(drop=True)

        df_merged.to_csv(csv_filepath, index=index)
        print(f"Multiple DataFrames merged and saved to: {csv_filepath}")
        return csv_filepath

    @staticmethod
    def save_single_dataframe_to_csv(
        df: pd.DataFrame,
        filename_prefix: str,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        use_sub_dir: bool = True,
        include_timestamp_in_filename: bool = True,
        index: bool = False
    ) -> str:
        """
        Saves a single DataFrame to a CSV file with flexible naming and directory options.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            filename_prefix (str): Prefix for the CSV filename (e.g., "metrics_report").
            output_dir (str): The primary directory where the file (or its sub-directory) will be saved.
            use_sub_dir (bool): If True, creates a timestamped subdirectory within 'output_dir'
                                and saves the file there. If False, saves directly in 'output_dir'.
            include_timestamp_in_filename (bool): If True, appends a timestamp to the filename.
            index (bool): Whether to write DataFrame index as a column.

        Returns:
            str: The full path to the saved CSV file.
        """
        target_dir = Helpers.create_output_dir(output_dir, use_sub_dir=use_sub_dir) if use_sub_dir else output_dir
        if not use_sub_dir: # Ensure base output_dir exists if not using sub_dir
            os.makedirs(target_dir, exist_ok=True)

        timestamp_str = f"_{Helpers.name_today_datetime()}" if include_timestamp_in_filename else ""
        csv_filename = f"{filename_prefix}{timestamp_str}.csv"
        csv_filepath = os.path.join(target_dir, csv_filename)

        df.to_csv(csv_filepath, index=index)
        print(f"DataFrame saved to: {csv_filepath}")
        return csv_filepath
    