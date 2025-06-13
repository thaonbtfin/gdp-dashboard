import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from datetime import datetime, timedelta
from constants import DEFAULT_OUTPUT_DIR, DEFAULT_PERIOD, DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_USE_SUB_DIR

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
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
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
        return datetime.now().strftime('%Y%m%d_%H%M')

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