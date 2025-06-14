import numpy as np
import pandas as pd

class Calculator:
    """
    Calculator provides static methods for financial calculations on stock data.
    """
    @staticmethod
    def calculate_profit_rates(df_history, portfolio_value, input_investment):
        """
        Calculate various profit rates and standard deviations based on historical data and user input.

        Args:
            df_history (pd.DataFrame): DataFrame with at least a 'daily profit rate' column.
            portfolio_value (float): Final portfolio value for calculation.
            input_investment (float): Initial investment amount for calculation.

        Returns:
            pd.DataFrame: DataFrame with a single row containing calculated metrics
                          (all as percentages, rounded to 2 decimals).
        """
        # 1. overall_daily_profit_rate (as percent)
        overall_daily_profit_rate = (((portfolio_value / input_investment) ** (1/1250)) - 1) * 100

        # 2. overall_cumulative_profit_rate (as percent)
        overall_cumulative_profit_rate = ((1 + overall_daily_profit_rate / 100) ** 250 - 1) * 100

        # 3. overall_daily_standard_deviation (as percent)
        daily_profit_rate_series = df_history['daily profit rate']
        overall_daily_standard_deviation = np.std(daily_profit_rate_series, ddof=0)

        # 4. overall_annual_standard_deviation (as percent)
        overall_annual_standard_deviation = overall_daily_standard_deviation * np.sqrt(250)
    
        data = {
            'overall_daily_profit_rate': float(round(overall_daily_profit_rate, 2)),
            'overall_cumulative_profit_rate': float(round(overall_cumulative_profit_rate, 2)),
            'overall_daily_standard_deviation': float(round(overall_daily_standard_deviation, 2)),
            'overall_annual_standard_deviation': float(round(overall_annual_standard_deviation, 2))
        }
        return pd.DataFrame([data])

    # @staticmethod
    # def add_profit_rate_columns_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     Add daily and cumulative profit rate columns to a DataFrame with a 'close' column.
    #     Returns a new DataFrame with the added columns, or the original if 'close' column is missing.
    #     """
    #     df_copy = df.copy() # Work on a copy to avoid modifying the original DataFrame

    #     if 'close' in df_copy.columns:  # Check if 'close' column exists
    #         df_copy['daily profit rate'] = df_copy['close'].pct_change() * 100
    #         df_copy['daily profit rate'] = df_copy['daily profit rate'].fillna(0).round(2)
    #         df_copy['cumulative profit rate'] = (1 + df_copy['daily profit rate'] / 100).cumprod() - 1
    #         df_copy['cumulative profit rate'] = df_copy['cumulative profit rate'].fillna(0).round(2)
    #         print("Added profit rate columns to dataframe.")
    #     else:    
    #         print(f"DataFrame must contain 'close' column.")
    #     return df_copy
    
    # @staticmethod
    # def add_profit_rate_columns_to_csv_file(csv_filepath: str):
    #     """
    #     Read a CSV, calculate profit rates, and update the CSV with new columns.
    #     Only works for CSVs with a 'close' column.
    #     """
    #     try:
    #         df = pd.read_csv(csv_filepath)
    #         # add_profit_rate_columns_to_dataframe returns a modified DataFrame
    #         df_modified = Calculator.add_profit_rate_columns_to_dataframe(df)

    #         # Check if 'daily profit rate' was actually added, implying success
    #         if 'daily profit rate' in df_modified.columns:
    #             df_modified.to_csv(csv_filepath, index=False)
    #             print(f"Successfully updated {csv_filepath} with profit rate columns.")
    #         # If not, the add_profit_rate_columns_to_dataframe method would have printed an error
    #         # (e.g., 'close' column missing), so no need to save.
    #     except FileNotFoundError:
    #         print(f"Error: File not found at {csv_filepath}")
    #     except Exception as e:
    #         print(f"An error occurred while processing {csv_filepath}: {e}")
    
    @staticmethod
    def add_profit_rate_columns_to_dataframes(dataframes_dict: dict) -> pd.DataFrame:
        """
        Add daily and cumulative profit rate columns to each DataFrame in a dictionary
        and returns a single concatenated DataFrame.

        Args:
            dataframes_dict (dict): Dictionary of {symbol: DataFrame}.
                                    Each DataFrame must have a 'close' column.

        Returns:
            pd.DataFrame: A single DataFrame containing all processed DataFrames,
                          concatenated with keys from the input dictionary.
                          The outer index level will be named 'symbol'.
                          Returns an empty DataFrame if the input dictionary is empty.
        """
        if not dataframes_dict:
            return pd.DataFrame()

        processed_dfs_list = []
        keys_list = []

        for symbol, df_original in dataframes_dict.items():
            # Work on a copy to avoid modifying the original DataFrame in the input dictionary
            df_copy = df_original.copy()
            # The add_profit_rate_columns_to_dataframe method handles the 'close' column check
            # and returns the modified DataFrame.
            modified_df = Calculator.add_profit_rate_columns_to_dataframe(df_copy)
            processed_dfs_list.append(modified_df)
            keys_list.append(symbol)
        
        if not processed_dfs_list: # Should only happen if dataframes_dict was empty
            return pd.DataFrame()

        concatenated_df = pd.concat(processed_dfs_list, keys=keys_list, names=['symbol', None])
        print(f"Added profit rate columns and concatenated DataFrames for symbols: {list(dataframes_dict.keys())}")
        return concatenated_df
    
    @staticmethod
    def calculate_moving_average(df: pd.DataFrame, window: int, price_column: str = 'close', ma_type: str = 'SMA') -> pd.Series:
        """
        Calculates the moving average (SMA or EMA) for a given price column.

        Args:
            df (pd.DataFrame): DataFrame containing the stock data.
            window (int): The window size for the moving average.
            price_column (str): The name of the column to calculate SMA on (e.g., 'close', 'open').
            ma_type (str): Type of moving average: 'SMA' (Simple) or 'EMA' (Exponential).

        Returns:
            pd.Series: A pandas Series containing the moving average values.
                       Returns an empty Series if the price_column is not found or df is too short
                       or ma_type is invalid.
        """
        if price_column not in df.columns:
            print(f"Error: Column '{price_column}' not found in DataFrame.")
            return pd.Series(dtype=float)
        
        if len(df) < window:
            # For SMA, this is a hard requirement. For EMA, ewm().mean() can produce results,
            # but they might not be meaningful. We'll keep a warning for EMA.
            if ma_type.upper() == 'SMA':
                print(f"Error: DataFrame length ({len(df)}) is less than window size ({window}) for SMA.")
                return pd.Series(dtype=float)
            elif ma_type.upper() == 'EMA':
                print(f"Warning: DataFrame length ({len(df)}) is less than window size ({window}). EMA might be less reliable.")
            
        if ma_type.upper() == 'SMA':
            return df[price_column].rolling(window=window).mean()
        elif ma_type.upper() == 'EMA':
            return df[price_column].ewm(span=window, adjust=False).mean()
        else:
            print(f"Error: Invalid moving average type '{ma_type}'. Choose 'SMA' or 'EMA'.")
            return pd.Series(dtype=float)

    # You can add more static methods for other calculations:
    # - Relative Strength Index (RSI)
    # - Moving Average Convergence Divergence (MACD)
    # - Bollinger Bands

    @staticmethod
    def calculate_series_performance_metrics(
        df: pd.DataFrame, 
        price_column: str = 'close', 
        trading_days_per_year: int = 250
    ) -> dict:
        """
        Calculates performance metrics from a historical price series.

        Args:
            df (pd.DataFrame): DataFrame with historical data, must include price_column.
            price_column (str): The name of the column containing prices (e.g., 'close').
            trading_days_per_year (int): Number of trading days in a year for annualization.

        Returns:
            dict: A dictionary containing the calculated metrics (as percentages):
                  - 'geom_mean_daily_return_pct': Geometric mean daily return.
                  - 'annualized_return_pct': Annualized return based on geometric mean.
                  - 'daily_std_dev_pct': Daily standard deviation of returns.
                  - 'annual_std_dev_pct': Annualized standard deviation of returns.
                  Returns NaNs if calculations cannot be performed (e.g., insufficient data).
        """
        if price_column not in df.columns:
            print(f"Error: Column '{price_column}' not found in DataFrame.")
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        if len(df) < 2:
            print("Error: DataFrame must have at least 2 rows to calculate performance metrics.")
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        prices = df[price_column].dropna()
        if len(prices) < 2:
            print("Error: Not enough valid price data points after dropping NaNs.")
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        first_price = prices.iloc[0]
        last_price = prices.iloc[-1]
        num_periods = len(prices) - 1

        if first_price == 0 or num_periods == 0: # Avoid division by zero or log(0) issues
            geom_mean_daily_return = np.nan
        else:
            geom_mean_daily_return = (last_price / first_price)**(1 / num_periods) - 1
        
        annualized_return = (1 + geom_mean_daily_return)**trading_days_per_year - 1 if not np.isnan(geom_mean_daily_return) else np.nan

        # Calculate daily returns (as rates, e.g., 0.01 for 1%)
        daily_returns = prices.pct_change().dropna()

        if daily_returns.empty:
            daily_std_dev = np.nan
        else:
            # Use ddof=0 for population standard deviation, consistent with other methods if that's the intent
            daily_std_dev = daily_returns.std(ddof=0) 
        
        annual_std_dev = daily_std_dev * np.sqrt(trading_days_per_year) if not np.isnan(daily_std_dev) else np.nan

        return {
            'geom_mean_daily_return_pct': round(geom_mean_daily_return * 100, 4) if not np.isnan(geom_mean_daily_return) else np.nan,
            'annualized_return_pct': round(annualized_return * 100, 4) if not np.isnan(annualized_return) else np.nan,
            'daily_std_dev_pct': round(daily_std_dev * 100, 4) if not np.isnan(daily_std_dev) else np.nan,
            'annual_std_dev_pct': round(annual_std_dev * 100, 4) if not np.isnan(annual_std_dev) else np.nan,
        }
