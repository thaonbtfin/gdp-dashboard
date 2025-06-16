import pandas as pd
import numpy as np
from vnstock import Vnstock
from .fetcher import Fetcher
from src.constants import DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR
from .calculator import Calculator

class Stock:
    """
    A simple class to represent a stock and its performance metrics.
    It fetches its own data upon initialization.
    """

    def __init__(self, symbol: str, start_date: str, end_date: str, source: str = DEFAULT_SOURCE):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.data = None
        self.performance_metrics = None
        self.financial_ratios_df = None
        self.intrinsic_value_graham = None

        self._fetch_data()
        self._calculate_metrics()
        self._fetch_and_calculate_intrinsic_value()

    def _fetch_data(self):
        """
        Fetches historical data for the stock.
        """
        fetcher = Fetcher(
            symbols=[self.symbol],
            start_date=self.start_date,
            end_date=self.end_date,
            source=self.source,
            output_dir=DEFAULT_OUTPUT_DIR
        )
        fetched_data_dict = fetcher.fetch_history_to_dataframe_from_start_end_date(
            symbols=[self.symbol],
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.data = fetched_data_dict.get(self.symbol)

    def _calculate_metrics(self):
        if self.data is not None and not self.data.empty:
            self.performance_metrics = Calculator.calculate_series_performance_metrics(self.data, price_column='close')
        else:
            print(f"Warning: Data for {self.symbol} is None or empty after fetching. Metrics will be None.")
            self.performance_metrics = {metric: None for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

    def _fetch_financial_ratios(self):
        """
        Fetches yearly financial ratios for the stock.
        """
        try:
            self.financial_ratios_df = Vnstock().stock(symbol=self.symbol, source=self.source).finance.ratio(period='year', lang='vi', dropna=True)
            if self.financial_ratios_df.empty:
                print(f"Warning: No financial ratios found for {self.symbol}.")
                self.financial_ratios_df = None
        except Exception as e:
            print(f"Error fetching financial ratios for {self.symbol}: {e}")
            self.financial_ratios_df = None

    def _calculate_intrinsic_value_graham(self):
        """
        Calculates the intrinsic value using the Graham Number formula: sqrt(22.5 * EPS * BVPS)
        Uses the latest yearly EPS and BVPS.
        """
        if self.financial_ratios_df is None or self.financial_ratios_df.empty:
            print(f"Cannot calculate Graham Number for {self.symbol} due to missing financial ratios.")
            return

        try:
            latest_year_data = self.financial_ratios_df.iloc[0]

            eps_column_key = ('Chỉ tiêu định giá', 'EPS (VND)')
            bvps_column_key = ('Chỉ tiêu định giá', 'BVPS (VND)')
            eps = latest_year_data.get(eps_column_key)
            bvps = latest_year_data.get(bvps_column_key)

            if eps is not None and bvps is not None and pd.notna(eps) and pd.notna(bvps):
                if eps > 0 and bvps > 0:
                    self.intrinsic_value_graham = round(np.sqrt(22.5 * float(eps) * float(bvps)), 2)
                    print(f"Calculated Graham Intrinsic Value for {self.symbol}: {self.intrinsic_value_graham:,.2f}")
                else:
                    print(f"Warning: EPS ({eps}) or BVPS ({bvps}) is not positive for {self.symbol}. Graham Number not applicable.")
            else:
                print(f"Warning: Latest EPS or BVPS not found or is NaN for {self.symbol}.")
        except Exception as e:
            print(f"Error calculating Graham Number for {self.symbol}: {e}")

    def _fetch_and_calculate_intrinsic_value(self):
        self._fetch_financial_ratios()
        self._calculate_intrinsic_value_graham()

    def get_intrinsic_value_graham(self):
        return self.intrinsic_value_graham

    def get_performance_metrics(self):
        return self.performance_metrics

    def get_symbol(self):
        return self.symbol
        
    def get_data(self):
        return self.data

    @staticmethod
    def get_multiple_stocks_metrics_df(symbols: list, start_date: str, end_date: str, source: str = DEFAULT_SOURCE) -> pd.DataFrame:
        """
        Calculates performance metrics and Graham intrinsic value for multiple stocks.

        Args:
            symbols (list): List of stock symbols.
            start_date (str): Start date for data fetching.
            end_date (str): End date for data fetching.
            source (str): Data source.

        Returns:
            pd.DataFrame: DataFrame containing 'symbol', performance metrics, and 'graham_intrinsic_value'.
                          Returns an empty DataFrame if the input symbols list is empty.
        """
        all_metrics_data = []

        for symbol in symbols:
            stock_obj = Stock(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                source=source
            )

            graham_value = stock_obj.get_intrinsic_value_graham()
            metrics_entry = {
                'symbol': symbol,
                **stock_obj.performance_metrics,
                'graham_intrinsic_value': f"{graham_value:,.2f}" if graham_value is not None and pd.notna(graham_value) else "N/A"
            }
            all_metrics_data.append(metrics_entry)
        
        if not all_metrics_data:
            return pd.DataFrame()

        return pd.DataFrame(all_metrics_data)