import pandas as pd
from .fetcher import Fetcher # Assuming Fetcher is in api.fetcher relative to this file's execution context
from .calculator import Calculator # Assuming Calculator is in services.calculator
from src.constants import DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR

class Portfolio:
    """
    Represents a portfolio of stocks and calculates its performance metrics.
    """
    # def __init__(self, symbols: list, start_date: str, end_date: str, source: str = DEFAULT_SOURCE, weights: list = None, name: str = "MyPortfolio"):
    def __init__(self, symbols: list, start_date: str = None, end_date: str = None, source: str = DEFAULT_SOURCE, weights: list = None, name: str = "MyPortfolio", fetched_data: dict = None):
        """
        Initializes the Portfolio.

        Args:
            symbols (list): List of stock symbols.
            start_date (str, optional): Start date for data fetching if fetched_data is not provided.
            end_date (str, optional): End date for data fetching if fetched_data is not provided.
            source (str, optional): Data source if fetching. Defaults to DEFAULT_SOURCE.
            weights (list, optional): List of weights for each symbol. Defaults to equal weights.
            name (str, optional): Name of the portfolio. Defaults to "MyPortfolio".
            fetched_data (dict, optional): Pre-fetched historical data. Keys are symbols, values are DataFrames.
                                           If provided, internal fetching is skipped.
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.weights = weights if weights else [1/len(symbols)] * len(symbols) # Equal weights if not provided
        self.name = name
        self.fetched_data = fetched_data # Store pre-fetched data
        self.portfolio_value_series = None
        self.performance_metrics = None
        self._build_portfolio_and_calculate_metrics()

    def _fetch_data(self):
        fetcher = Fetcher(
            symbols=self.symbols, # Initial symbols for fetcher, will be overridden
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
            output_dir=DEFAULT_OUTPUT_DIR # Or a relevant output_dir
        )
        return fetcher.fetch_history_to_dataframe_from_start_end_date(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date
        )

    def _build_portfolio_and_calculate_metrics(self):
        # fetched_data = self._fetch_data()
        if self.fetched_data:
            data_to_process = self.fetched_data
        else:
            data_to_process = self._fetch_data()

        close_prices_list = []
        for symbol in self.symbols:
            # df_symbol = fetched_data.get(symbol)
            df_symbol = data_to_process.get(symbol)
            if df_symbol is not None and not df_symbol.empty and 'close' in df_symbol.columns and 'time' in df_symbol.columns:
                df_symbol['time'] = pd.to_datetime(df_symbol['time'])
                df_symbol = df_symbol.set_index('time')
                close_prices_list.append(df_symbol['close'].rename(symbol))
            else:
                print(f"Warning: Data for {symbol} is missing or invalid. It will be excluded from portfolio {self.name}.")

        if not close_prices_list:
            print(f"No valid stock data found to form portfolio {self.name}. Metrics will be None.")
            self.performance_metrics = {metric: None for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}
            return

        all_closes_df = pd.concat(close_prices_list, axis=1)
        all_closes_df = all_closes_df.ffill().bfill().dropna()

        if all_closes_df.empty:
            print(f"Portfolio {self.name} DataFrame is empty after processing. Metrics will be None.")
            self.performance_metrics = {metric: None for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}
            return

        normalized_closes_df = all_closes_df / all_closes_df.iloc[0]
        
        # For now, using equal weighting as per previous logic.
        # To use self.weights, you'd multiply normalized_closes_df by weights before .sum(axis=1)
        self.portfolio_value_series = normalized_closes_df.mean(axis=1) 

        portfolio_df_for_calc = pd.DataFrame({'time': self.portfolio_value_series.index, 'close': self.portfolio_value_series.values})
        self.performance_metrics = Calculator.calculate_series_performance_metrics(portfolio_df_for_calc, price_column='close')

    def get_performance_metrics(self):
        return self.performance_metrics

    def get_portfolio_value_series(self):
        return self.portfolio_value_series

    def get_name(self):
        return self.name

    def get_symbols(self):
        return self.symbols

    def get_weights(self):
        return self.weights

    @staticmethod
    def get_portfolio_metrics_df(
        symbols: list,
        start_date: str,
        end_date: str,
        source: str = DEFAULT_SOURCE,
        weights: list = None,
        name: str = "MyPortfolio"
    ) -> pd.DataFrame:
        """
        Creates a Portfolio object, calculates its performance metrics,
        and returns them as a DataFrame.

        Args:
            symbols (list): List of stock symbols for the portfolio.
            start_date (str): Start date for data fetching.
            end_date (str): End date for data fetching.
            source (str): Data source.
            weights (list, optional): List of weights for each symbol. Defaults to equal weights.
            name (str, optional): Name of the portfolio. Defaults to "MyPortfolio".

        Returns:
            pd.DataFrame: DataFrame containing the portfolio's performance metrics.
                          Returns an empty DataFrame if metrics cannot be calculated.
        """
        portfolio_obj = Portfolio(symbols, start_date, end_date, source, weights, name)

        if portfolio_obj.performance_metrics:
            metrics_df = pd.DataFrame([portfolio_obj.performance_metrics])
            metrics_df['portfolio_name'] = portfolio_obj.name
            cols = ['portfolio_name'] + [col for col in metrics_df.columns if col != 'portfolio_name']
            return metrics_df[cols]
        return pd.DataFrame()