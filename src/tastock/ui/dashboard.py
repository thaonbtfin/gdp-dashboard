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
from .technical_helper import TechnicalHelper
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
    
    @staticmethod
    def technical_analysis_tab(raw_df):
        """Displays technical analysis tab with indicators and charts similar to CafeF."""
        if raw_df.empty:
            st.info("Không có dữ liệu để phân tích kỹ thuật.")
            return
        
        # Load custom CSS
        TechnicalHelper.load_custom_css()
        
        st.header("📈 Phân tích Kỹ thuật", divider="gray")
        
        # Symbol selection
        symbol_columns = [col for col in raw_df.columns if col != 'time']
        if not symbol_columns:
            st.warning("Không tìm thấy mã chứng khoán nào để phân tích.")
            return
        
        # Horizontal layout for controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Default to VNINDEX if available, otherwise first symbol
            default_symbol = 'VNINDEX' if 'VNINDEX' in symbol_columns else symbol_columns[0]
            
            selected_symbol = st.selectbox(
                "Chọn mã chứng khoán:",
                symbol_columns,
                index=symbol_columns.index(default_symbol) if default_symbol in symbol_columns else 0
            )
        
        with col2:
            # Time period selection
            period_options = {
                "1 tháng": 30,
                "3 tháng": 90, 
                "6 tháng": 180,
                "1 năm": 365,
                "2 năm": 730,
                "3 năm": 1095,
                "Tất cả": None
            }
            
            selected_period = st.selectbox(
                "Khoảng thời gian:",
                list(period_options.keys()),
                index=2  # Default to 6 months
            )
        
        with col3:
            # Chart type selection
            chart_types = ["Nến Nhật", "Đường giá", "Cột"]
            chart_type = st.selectbox(
                "Loại biểu đồ:",
                chart_types,
                index=0
            )
        
        # Full width for chart area
        # Get data for selected symbol
        symbol_data = raw_df[['time', selected_symbol]].copy()
        symbol_data = symbol_data.dropna()
        symbol_data['time'] = pd.to_datetime(symbol_data['time'])
        symbol_data = symbol_data.sort_values('time')
        
        # Filter by period
        if period_options[selected_period] is not None:
            cutoff_date = symbol_data['time'].max() - pd.Timedelta(days=period_options[selected_period])
            symbol_data = symbol_data[symbol_data['time'] >= cutoff_date]
        
        if len(symbol_data) < 20:
            st.warning("Không đủ dữ liệu để tính toán các chỉ báo kỹ thuật (cần ít nhất 20 điểm dữ liệu).")
            return
        
        # Calculate technical indicators
        TAstock_st._calculate_comprehensive_indicators(symbol_data, selected_symbol, chart_type)
    
    @staticmethod
    def _calculate_comprehensive_indicators(df, symbol, chart_type):
        """Calculate comprehensive technical indicators similar to CafeF."""
        import numpy as np
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Rename price column for easier access
        df = df.rename(columns={symbol: 'price'})
        
        # Calculate all technical indicators
        TAstock_st._calculate_all_indicators(df)
        
        # Create comprehensive chart layout
        TAstock_st._display_comprehensive_charts(df, symbol, chart_type)
        
        # Display indicator summary table
        TAstock_st._display_indicator_summary(df, symbol)
    
    @staticmethod
    def _calculate_all_indicators(df):
        """Calculate all technical indicators."""
        import numpy as np
        
        # Moving Averages
        df['MA5'] = df['price'].rolling(window=5).mean()
        df['MA10'] = df['price'].rolling(window=10).mean()
        df['MA20'] = df['price'].rolling(window=20).mean()
        df['MA50'] = df['price'].rolling(window=50).mean()
        df['MA100'] = df['price'].rolling(window=100).mean()
        df['MA200'] = df['price'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA12'] = df['price'].ewm(span=12).mean()
        df['EMA26'] = df['price'].ewm(span=26).mean()
        
        # RSI
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        df['RSI'] = calculate_rsi(df['price'])
        
        # MACD
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['price'].rolling(window=20).mean()
        bb_std = df['price'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Stochastic Oscillator
        def calculate_stochastic(high, low, close, k_period=14, d_period=3):
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            return k_percent, d_percent
        
        # For simplicity, use price as both high and low
        df['Stoch_K'], df['Stoch_D'] = calculate_stochastic(df['price'], df['price'], df['price'])
        
        # Williams %R
        def calculate_williams_r(high, low, close, period=14):
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
            return wr
        
        df['Williams_R'] = calculate_williams_r(df['price'], df['price'], df['price'])
        
        # CCI (Commodity Channel Index)
        def calculate_cci(high, low, close, period=20):
            tp = (high + low + close) / 3
            sma_tp = tp.rolling(window=period).mean()
            mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            cci = (tp - sma_tp) / (0.015 * mad)
            return cci
        
        df['CCI'] = calculate_cci(df['price'], df['price'], df['price'])
        
        # Volume indicators (using price change as proxy for volume)
        df['Price_Change'] = df['price'].pct_change()
        df['Volume_Proxy'] = abs(df['Price_Change']) * 1000000  # Simulated volume
        
        # On Balance Volume (OBV)
        df['OBV'] = (np.sign(df['Price_Change']) * df['Volume_Proxy']).cumsum()
        
        # Money Flow Index (simplified)
        df['MFI'] = df['RSI']  # Simplified as MFI for display
    
    @staticmethod
    def _display_comprehensive_charts(df, symbol, chart_type):
        """Display comprehensive technical analysis charts similar to CafeF."""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            # Create subplots with secondary y-axis
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    f'{symbol} - Biểu đồ giá và chỉ báo',
                    'RSI (14)',
                    'MACD',
                    'Stochastic'
                ),
                row_heights=[0.5, 0.2, 0.2, 0.1]
            )
            
            # Main price chart
            if chart_type == "Nến Nhật":
                # Simulate OHLC data from price
                df['open'] = df['price'].shift(1)
                df['high'] = df[['price', 'open']].max(axis=1) * 1.002
                df['low'] = df[['price', 'open']].min(axis=1) * 0.998
                df['close'] = df['price']
                
                fig.add_trace(
                    go.Candlestick(
                        x=df['time'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=symbol
                    ),
                    row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df['time'],
                        y=df['price'],
                        mode='lines',
                        name=symbol,
                        line=dict(color='blue', width=2)
                    ),
                    row=1, col=1
                )
            
            # Moving averages
            colors = ['orange', 'red', 'green', 'purple', 'brown']
            mas = ['MA5', 'MA10', 'MA20', 'MA50', 'MA100']
            
            for i, ma in enumerate(mas):
                if ma in df.columns and not df[ma].isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df['time'],
                            y=df[ma],
                            mode='lines',
                            name=ma,
                            line=dict(color=colors[i % len(colors)], width=1)
                        ),
                        row=1, col=1
                    )
            
            # Bollinger Bands
            if 'BB_Upper' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['time'],
                        y=df['BB_Upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='gray', width=1, dash='dash')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['time'],
                        y=df['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='gray', width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)'
                    ),
                    row=1, col=1
                )
            
            # RSI
            fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=2, col=1
            )
            
            # RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
            
            # MACD
            fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['MACD_Signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='red')
                ),
                row=3, col=1
            )
            
            # MACD Histogram
            fig.add_trace(
                go.Bar(
                    x=df['time'],
                    y=df['MACD_Histogram'],
                    name='Histogram',
                    marker_color='gray',
                    opacity=0.6
                ),
                row=3, col=1
            )
            
            # Stochastic
            fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['Stoch_K'],
                    mode='lines',
                    name='%K',
                    line=dict(color='blue')
                ),
                row=4, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['Stoch_D'],
                    mode='lines',
                    name='%D',
                    line=dict(color='red')
                ),
                row=4, col=1
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=True,
                title_text=f"Phân tích kỹ thuật - {symbol}",
                xaxis_rangeslider_visible=False
            )
            
            # Update y-axes
            fig.update_yaxes(title_text="Giá", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
            fig.update_yaxes(title_text="MACD", row=3, col=1)
            fig.update_yaxes(title_text="Stoch", row=4, col=1, range=[0, 100])
            
            # Wrap chart in container
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except ImportError:
            # Fallback to simple charts if plotly is not available
            # Fallback charts with enhanced styling
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader(f"📊 Biểu đồ giá - {symbol}")
            chart_data = df[['time', 'price', 'MA5', 'MA10', 'MA20']].set_index('time')
            st.line_chart(chart_data)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 RSI")
            rsi_data = df[['time', 'RSI']].set_index('time')
            st.line_chart(rsi_data)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📉 MACD")
            macd_data = df[['time', 'MACD', 'MACD_Signal']].set_index('time')
            st.line_chart(macd_data)
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _display_indicator_summary(df, symbol):
        """Display comprehensive indicator summary table similar to CafeF."""
        st.subheader("📊 Bảng tổng hợp chỉ báo kỹ thuật")
        
        latest = df.iloc[-1]
        
        # Create indicator summary data
        indicators_data = []
        
        # Moving Averages Analysis
        current_price = latest['price']
        
        mas = {
            'MA5': 'MA(5)',
            'MA10': 'MA(10)', 
            'MA20': 'MA(20)',
            'MA50': 'MA(50)',
            'MA100': 'MA(100)',
            'MA200': 'MA(200)'
        }
        
        for ma_key, ma_name in mas.items():
            if ma_key in df.columns and not pd.isna(latest[ma_key]):
                ma_value = latest[ma_key]
                signal = "MUA" if current_price > ma_value else "BÁN"
                color = "🟢" if signal == "MUA" else "🔴"
                indicators_data.append({
                    'Chỉ báo': ma_name,
                    'Giá trị': f"{ma_value:.2f}",
                    'Tín hiệu': f"{color} {signal}",
                    'Loại': 'Đường trung bình'
                })
        
        # Oscillators
        oscillators = [
            ('RSI', 'RSI(14)', lambda x: "MUA" if x < 30 else "BÁN" if x > 70 else "TRUNG TÍNH"),
            ('Stoch_K', 'Stochastic %K', lambda x: "MUA" if x < 20 else "BÁN" if x > 80 else "TRUNG TÍNH"),
            ('Williams_R', 'Williams %R', lambda x: "MUA" if x < -80 else "BÁN" if x > -20 else "TRUNG TÍNH"),
            ('CCI', 'CCI(20)', lambda x: "MUA" if x < -100 else "BÁN" if x > 100 else "TRUNG TÍNH")
        ]
        
        for osc_key, osc_name, signal_func in oscillators:
            if osc_key in df.columns and not pd.isna(latest[osc_key]):
                osc_value = latest[osc_key]
                signal = signal_func(osc_value)
                color = "🟢" if signal == "MUA" else "🔴" if signal == "BÁN" else "🟡"
                indicators_data.append({
                    'Chỉ báo': osc_name,
                    'Giá trị': f"{osc_value:.2f}",
                    'Tín hiệu': f"{color} {signal}",
                    'Loại': 'Dao động'
                })
        
        # MACD Analysis
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            macd_val = latest['MACD']
            macd_signal = latest['MACD_Signal']
            if not pd.isna(macd_val) and not pd.isna(macd_signal):
                signal = "MUA" if macd_val > macd_signal else "BÁN"
                color = "🟢" if signal == "MUA" else "🔴"
                indicators_data.append({
                    'Chỉ báo': 'MACD(12,26)',
                    'Giá trị': f"{macd_val:.4f}",
                    'Tín hiệu': f"{color} {signal}",
                    'Loại': 'Momentum'
                })
        
        # Bollinger Bands
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
            bb_upper = latest['BB_Upper']
            bb_lower = latest['BB_Lower']
            if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                if current_price > bb_upper:
                    signal = "BÁN"
                    color = "🔴"
                elif current_price < bb_lower:
                    signal = "MUA"
                    color = "🟢"
                else:
                    signal = "TRUNG TÍNH"
                    color = "🟡"
                
                indicators_data.append({
                    'Chỉ báo': 'Bollinger Bands',
                    'Giá trị': f"{bb_upper:.2f}/{bb_lower:.2f}",
                    'Tín hiệu': f"{color} {signal}",
                    'Loại': 'Volatility'
                })
        
        # Create enhanced DataFrame display
        if indicators_data:
            styled_df = TechnicalHelper.format_indicator_table(indicators_data)
            if styled_df is not None:
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                indicators_df = pd.DataFrame(indicators_data)
                st.dataframe(indicators_df, use_container_width=True, hide_index=True)
            
            # Summary signals
            buy_signals = sum(1 for item in indicators_data if "MUA" in item['Tín hiệu'])
            sell_signals = sum(1 for item in indicators_data if "BÁN" in item['Tín hiệu'])
            neutral_signals = len(indicators_data) - buy_signals - sell_signals
            
            st.subheader("📈 Phân tích tín hiệu chi tiết")
            
            # Create enhanced signal cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                buy_card = TechnicalHelper.create_signal_summary_card("BUY", buy_signals, "Tín hiệu MUA")
                st.markdown(buy_card, unsafe_allow_html=True)
            
            with col2:
                sell_card = TechnicalHelper.create_signal_summary_card("SELL", sell_signals, "Tín hiệu BÁN")
                st.markdown(sell_card, unsafe_allow_html=True)
            
            with col3:
                neutral_card = TechnicalHelper.create_signal_summary_card("NEUTRAL", neutral_signals, "Tín hiệu TRUNG TÍNH")
                st.markdown(neutral_card, unsafe_allow_html=True)
            
            # Calculate confidence and recommendation first
            total_signals = len(indicators_data)
            confidence = max(buy_signals, sell_signals) / total_signals * 100 if total_signals > 0 else 0
            
            with col4:
                confidence_card = TechnicalHelper.create_signal_summary_card("CONFIDENCE", f"{confidence:.0f}%", "Độ tin cậy")
                st.markdown(confidence_card, unsafe_allow_html=True)
            
            # Enhanced recommendation with styling
            
            if buy_signals > sell_signals:
                recommendation = "MUA"
            elif sell_signals > buy_signals:
                recommendation = "BÁN"
            else:
                recommendation = "TRUNG TÍNH"
            
            recommendation_html = TechnicalHelper.create_recommendation_card(
                recommendation, buy_signals, sell_signals, confidence
            )
            st.markdown(recommendation_html, unsafe_allow_html=True)
        
        # Enhanced price display
        price_change = latest['price'] - df['price'].iloc[-2] if len(df) > 1 else 0
        price_change_pct = (price_change / df['price'].iloc[-2] * 100) if len(df) > 1 and df['price'].iloc[-2] != 0 else 0
        
        # Display enhanced price with styling
        price_html = TechnicalHelper.format_price_display(latest['price'], price_change, price_change_pct)
        st.markdown(price_html, unsafe_allow_html=True)
        
        # Technical summary metrics
        tech_summary = TechnicalHelper.create_technical_summary_metrics(df, symbol)
        
        # Display technical metrics in grid
        st.subheader("📊 Thông tin kỹ thuật chi tiết")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if tech_summary.get('support_level'):
                support_diff = latest['price'] - tech_summary['support_level']
                st.metric(
                    "Hỗ trợ gần nhất",
                    f"{tech_summary['support_level']:,.2f}",
                    delta=f"{support_diff:+,.2f}"
                )
            else:
                st.metric("Hỗ trợ gần nhất", "N/A")
        
        with col2:
            if tech_summary.get('resistance_level'):
                resistance_diff = tech_summary['resistance_level'] - latest['price']
                st.metric(
                    "Kháng cự gần nhất",
                    f"{tech_summary['resistance_level']:,.2f}",
                    delta=f"{resistance_diff:+,.2f}"
                )
            else:
                st.metric("Kháng cự gần nhất", "N/A")
        
        with col3:
            st.metric(
                "Xu hướng",
                tech_summary.get('trend_strength', 'N/A'),
                delta=f"{tech_summary.get('sentiment_icon', '')} {tech_summary.get('market_sentiment', 'N/A')}"
            )
        
        with col4:
            st.metric(
                "Độ biến động",
                tech_summary.get('volatility_rating', 'N/A'),
                delta=f"{tech_summary.get('volatility_value', 0):.1f}%" if tech_summary.get('volatility_value') else None
            )