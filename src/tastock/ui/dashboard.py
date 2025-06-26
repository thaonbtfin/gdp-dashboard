"""
Dashboard Module

This module provides the dashboard UI components for the tastock application.
"""

import streamlit as st
import pandas as pd
import math
import os

from ..core.stock import Stock
from ..utils.helpers import Helpers
from ..data.data_calculator import DataCalculator
from ..data.data_manager import DataManager
from src.constants import DEFAULT_PERIOD, DATA_DIR


class TAstock_def:
    """
    Defines utility functions for the tastock dashboard.
    """

    @staticmethod
    def get_stock_data(df):
        """Grab stock history data from a CSV file and melt it."""

        if df.empty:
            # This message can be shown if df is empty from the start.
            # st.info("Dữ liệu đầu vào trống, không thể xử lý cho biểu đồ lịch sử.")
            return pd.DataFrame()

        raw_stock_df = df

        # Identify symbol columns (all columns except 'time')
        if 'time' not in raw_stock_df.columns:
            st.warning("Cột 'time' không tồn tại trong dữ liệu. Không thể tạo biểu đồ lịch sử.")
            return pd.DataFrame()
            
        symbol_columns = [col for col in raw_stock_df.columns if col != 'time']
        if not symbol_columns:
            st.warning("Không tìm thấy cột mã chứng khoán nào (ngoài cột 'time'). Vui lòng kiểm tra định dạng dữ liệu để tạo biểu đồ.")
            return pd.DataFrame()

        # Melt the DataFrame
        try:
            stock_df = raw_stock_df.melt(
                id_vars=['time'],
                value_vars=symbol_columns,
                var_name='Symbol',
                value_name='Price',
            )
        except Exception as e:
            st.error(f"Lỗi khi chuyển đổi dữ liệu (melt) cho biểu đồ: {e}")
            return pd.DataFrame()

        # Convert 'time' from YYYYMMDD integer to datetime objects
        try:
            stock_df['time'] = pd.to_datetime(stock_df['time']) # More robust if already datetime
        except Exception as e:
            st.error(f"Lỗi khi chuyển đổi cột 'time' sang định dạng ngày tháng cho biểu đồ: {e}.")
            return pd.DataFrame()

        # Remove rows where Price is NaN, as st.line_chart might have issues
        stock_df.dropna(subset=['Price'], inplace=True)

        return stock_df
    
    @staticmethod
    def _display_date_slider(stock_df, key_suffix=""):
        """Displays the date range slider and returns the selected range."""

        # Add some spacing - Slider
        ''
        ''
        if stock_df.empty or 'time' not in stock_df.columns:
            st.warning("Stock data is empty or 'time' column is missing.")
            st.stop()

        # Ensure 'time' column is datetime
        stock_df['time'] = pd.to_datetime(stock_df['time']) 

        min_value = stock_df['time'].min().date()
        max_value = stock_df['time'].max().date()

        from_date, to_date = st.slider(
            'Which date range are you interested in?',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value],
            format="YYYY-MM-DD",
            key=f"date_slider{key_suffix}"
        )

        return from_date, to_date
    
    @staticmethod
    def _display_stock_chart(stock_df, from_date, to_date):
        """Displays the multiselect for symbols and the stock price chart."""

        # Add some spacing - plotview
        ''
        ''

        symbols = sorted(stock_df['Symbol'].unique())

        if not len(symbols):
            st.warning("No symbols found in the data.")
            st.stop()

        default_symbols = [s for s in ['VNINDEX', 'ACB', 'FPT', 'VCB'] if s in symbols]
        if not default_symbols and len(symbols) > 0: # Fallback if default symbols are not present
            default_symbols = symbols[:min(4, len(symbols))]

        selected_symbols = st.multiselect(
            'Which stock symbols would you like to view?',
            symbols,
            default_symbols
        )

        ''
        ''
        ''

        if not selected_symbols:
            st.warning("Select at least one symbol to view the chart.")
            st.stop()

        # Filter the data
        filtered_stock_df = stock_df[
            stock_df['Symbol'].isin(selected_symbols)
            & (stock_df['time'].dt.date <= to_date)
            & (stock_df['time'].dt.date >= from_date)
        ]

        st.header('Stock Prices Over Time', divider='gray')
        ''

        st.line_chart(
            filtered_stock_df,
            x='time',
            y='Price',
            color='Symbol',
        )

        ''
        ''

        # Call the new metrics display method
        TAstock_def._display_stock_metric(selected_symbols, filtered_stock_df, from_date, to_date)
        
    @staticmethod
    def _display_stock_metric(selected_symbols, filtered_stock_df, from_date, to_date):
        """Displays key stock metrics for the selected symbols and date range."""
        # --- Metrics Display ---
        st.header(f'Stock Prices on {to_date.strftime("%Y-%m-%d")} (vs {from_date.strftime("%Y-%m-%d")})', divider='gray')
        ''

        # Use 4 columns for metrics, similar to the GDP dashboard
        cols = st.columns(4)

        for i, symbol in enumerate(selected_symbols):
            col = cols[i % 4]  # Distribute metrics into columns

            with col:
                # Data for the current symbol within the filtered date range
                symbol_specific_df = filtered_stock_df[filtered_stock_df['Symbol'] == symbol]

                if symbol_specific_df.empty:
                    st.metric(label=f'{symbol} Price', value='N/A', delta='N/A', delta_color='off')
                    continue

                # Ensure data is sorted by time to correctly get first and last prices
                symbol_specific_df = symbol_specific_df.sort_values('time')
                
                first_price = symbol_specific_df['Price'].iloc[0] if not symbol_specific_df.empty else math.nan
                last_price = symbol_specific_df['Price'].iloc[-1] if not symbol_specific_df.empty else math.nan
                
                display_last_price = f'{last_price:,.2f}' if not math.isnan(last_price) else 'N/A'
                
                growth_metric = 'N/A'
                delta_color = 'off'

                if not math.isnan(first_price) and not math.isnan(last_price) and first_price != 0:
                    growth_multiple = last_price / first_price
                    growth_metric = f'{growth_multiple:.2f}x'
                    delta_color = 'normal' if growth_multiple >= 1 else 'inverse'
                
                st.metric(label=f'{symbol} Price', value=display_last_price, delta=growth_metric, delta_color=delta_color)
                
    @staticmethod
    def _display_history_table(raw_df):
        """Displays a table of the raw historical data."""

        if not raw_df.empty:
            st.dataframe(raw_df)
        else:
            st.info("Không có dữ liệu chi tiết để hiển thị.")


class TAstock_st:
    """
    Defines the streamlit UI components for the tastock dashboard.
    """

    @staticmethod
    def history_tab(stock_df, key_suffix=""):
        """Displays the history tab with stock chart and metrics."""
        # Check if we have cached moving averages data
        has_cached_ma = False
        try:
            # This could be extended to load moving averages from cached files
            # if they are pre-calculated and stored
            pass
        except Exception:
            pass
            
        from_date, to_date = TAstock_def._display_date_slider(stock_df, key_suffix)
        TAstock_def._display_stock_chart(stock_df, from_date, to_date)
    
    @staticmethod
    def history_sub_tab(stock_df_melted):
        """Displays portfolio sub-tabs within the history tab."""
        # Create portfolio sub-tabs
        portfolio_tabs = st.tabs(["📊 All Portfolios", "VN100", "VN30", "DH", "TH"])
        
        if stock_df_melted.empty:
            for tab in portfolio_tabs:
                with tab:
                    st.info("Không thể xử lý dữ liệu để hiển thị biểu đồ lịch sử. Vui lòng kiểm tra định dạng dữ liệu hoặc các thông báo lỗi trước đó.")
        else:
            # All Portfolios tab
            with portfolio_tabs[0]:
                TAstock_st.history_tab(stock_df_melted, "_all")
            
            # Individual portfolio tabs
            from src.constants import SYMBOLS_VN100, SYMBOLS_VN30, SYMBOLS_DH, SYMBOLS_TH
            portfolios = [
                ("VN100", SYMBOLS_VN100),
                ("VN30", SYMBOLS_VN30), 
                ("DH", SYMBOLS_DH),
                ("TH", SYMBOLS_TH)
            ]
            
            for i, (portfolio_name, symbols) in enumerate(portfolios, 1):
                with portfolio_tabs[i]:
                    # Filter data for this portfolio
                    portfolio_df = stock_df_melted[stock_df_melted['Symbol'].isin(symbols)]
                    if portfolio_df.empty:
                        st.info(f"Không có dữ liệu cho danh mục {portfolio_name}")
                    else:
                        TAstock_st.history_tab(portfolio_df, f"_{portfolio_name.lower()}")
        
    @staticmethod
    def _display_performance_metrics_table(raw_df):
        """Displays a table of performance metrics calculated from the history table data."""
        
        if raw_df.empty:
            st.info("Không có dữ liệu để tính toán chỉ số hiệu suất.")
            return
            
        st.header("Chỉ số Hiệu suất", divider="gray")
        
        # Extract symbols from raw_df (all columns except 'time')
        symbols_list = [col for col in raw_df.columns if col != 'time']
        
        if not symbols_list:
            st.info("Không tìm thấy mã chứng khoán nào trong dữ liệu để tính toán chỉ số hiệu suất.")
            return
            
        # Calculate performance metrics directly without fetching external data
        performance_data_list = []
        
        # Prepare raw_df for calculation (ensure 'time' is DatetimeIndex)
        df_for_perf_calc = raw_df.copy()
        if 'time' in df_for_perf_calc.columns:
            try:
                df_for_perf_calc['time'] = pd.to_datetime(df_for_perf_calc['time'])
                df_for_perf_calc = df_for_perf_calc.set_index('time')
            except Exception as e:
                st.warning(f"Could not process 'time' column for performance calculation: {e}")
                return
                
        for symbol in symbols_list:
            symbol_perf_metrics = {'symbol': symbol}
            if symbol in df_for_perf_calc.columns:
                # Create a DataFrame for the single stock's price series
                single_stock_df = pd.DataFrame(df_for_perf_calc[symbol].dropna()).rename(columns={symbol: 'close'})
                
                if len(single_stock_df) > 1:
                    try:
                        # Calculate performance metrics
                        perf_metrics = DataCalculator.calculate_series_performance_metrics(single_stock_df, price_column='close')
                        symbol_perf_metrics.update(perf_metrics)
                    except Exception as e:
                        st.error(f"Error calculating performance for {symbol}: {e}")
            performance_data_list.append(symbol_perf_metrics)
            
        metrics_df = pd.DataFrame(performance_data_list)
        
        if not metrics_df.empty:
            # Define metric names and their display labels
            metric_labels = {
                'geom_mean_daily_return_pct': 'Lợi nhuận trung bình hàng ngày',
                'annualized_return_pct': 'Lợi nhuận hàng năm',
                'daily_std_dev_pct': 'Độ lệch chuẩn hàng ngày',
                'annual_std_dev_pct': 'Độ lệch chuẩn hàng năm'
            }
            
            # Use all metrics defined in metric_labels
            all_metrics = list(metric_labels.keys())
            
            if metrics_df.shape[0] > 0:
                # Create a new DataFrame with metrics as rows and symbols as columns
                formatted_df = pd.DataFrame(index=all_metrics)
                
                # Set the index names to display labels
                formatted_df.index = [metric_labels.get(m, m) for m in formatted_df.index]
                
                # Add data for each symbol
                for _, row in metrics_df.iterrows():
                    symbol = row['symbol']
                    for metric in all_metrics:
                        value = row.get(metric)
                        if pd.notna(value) and isinstance(value, (int, float)):
                            formatted_df.loc[metric_labels.get(metric, metric), symbol] = f"{value:.2%}"
                        else:
                            formatted_df.loc[metric_labels.get(metric, metric), symbol] = "N/A"
                
                st.dataframe(formatted_df)
            else:
                st.info("Không có chỉ số hiệu suất nào được tính toán.")
        else:
            st.info("Không thể tính toán chỉ số hiệu suất cho các mã chứng khoán.")
    
    @staticmethod
    def detail_tab(raw_df):  # Renamed parameter for clarity (it's the un-melted df)
        """Displays detailed data and performance metrics."""
        
        st.header("Chi tiết Dữ liệu Lịch sử", divider="gray")

        TAstock_def._display_history_table(raw_df)
        
        # Try to load performance metrics from data files first
        try:
            data_manager = DataManager(base_output_dir=DATA_DIR)
            perf_df = data_manager.load_latest_data('perf')
            
            if not perf_df.empty and 'symbol' in perf_df.columns:
                st.header("Chỉ số Hiệu suất (Từ dữ liệu đã lưu)", divider="gray")
                
                # Format the performance metrics for display
                metric_labels = {
                    'geom_mean_daily_return_pct': 'Lợi nhuận trung bình hàng ngày',
                    'annualized_return_pct': 'Lợi nhuận hàng năm',
                    'daily_std_dev_pct': 'Độ lệch chuẩn hàng ngày',
                    'annual_std_dev_pct': 'Độ lệch chuẩn hàng năm'
                }
                
                # Use all metrics defined in metric_labels that exist in the DataFrame
                all_metrics = [m for m in metric_labels.keys() if m in perf_df.columns]
                
                if all_metrics and perf_df.shape[0] > 0:
                    # Create a new DataFrame with metrics as rows and symbols as columns
                    formatted_df = pd.DataFrame(index=all_metrics)
                    
                    # Set the index names to display labels
                    formatted_df.index = [metric_labels.get(m, m) for m in formatted_df.index]
                    
                    # Add data for each symbol
                    for _, row in perf_df.iterrows():
                        symbol = row['symbol']
                        for metric in all_metrics:
                            value = row.get(metric)
                            if pd.notna(value) and isinstance(value, (int, float)):
                                formatted_df.loc[metric_labels.get(metric, metric), symbol] = f"{value:.2%}"
                            else:
                                formatted_df.loc[metric_labels.get(metric, metric), symbol] = "N/A"
                    
                    st.dataframe(formatted_df)
                    
                    # Try to load intrinsic values
                    try:
                        iv_df = data_manager.load_latest_data('intrinsic')
                        if not iv_df.empty and 'symbol' in iv_df.columns and 'intrinsic_value' in iv_df.columns:
                            st.header("Giá trị Nội tại (Từ dữ liệu đã lưu)", divider="gray")
                            
                            # Format intrinsic values as a transposed table (symbols as columns)
                            formatted_iv_df = pd.DataFrame(index=['Giá trị Nội tại'])
                            
                            for _, row in iv_df.iterrows():
                                symbol = row['symbol']
                                value = row.get('intrinsic_value')
                                if pd.notna(value):
                                    try:
                                        # Try to convert to float if it's a string
                                        if isinstance(value, str):
                                            value = float(value.replace(',', ''))
                                        formatted_iv_df.loc['Giá trị Nội tại', symbol] = f"{value:,.2f}"
                                    except:
                                        formatted_iv_df.loc['Giá trị Nội tại', symbol] = value
                                else:
                                    formatted_iv_df.loc['Giá trị Nội tại', symbol] = "N/A"
                            
                            st.dataframe(formatted_iv_df)
                    except Exception as e:
                        # If loading intrinsic values fails, just continue
                        pass
                    
                    # Skip calculating metrics from raw data since we already displayed them
                    return
            
        except Exception as e:
            # If loading from data manager fails, fall back to calculating from raw data
            pass
        
        # Fall back to calculating performance metrics from raw data
        TAstock_st._display_performance_metrics_table(raw_df)