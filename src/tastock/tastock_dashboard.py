import streamlit as st
import streamlit as st
import pandas as pd
import math

from .stock import Stock
from .helpers import Helpers
from .calculator import Calculator # Import Calculator
from ..constants import DEFAULT_PERIOD 


class TAstock_def:

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
        # This conversion should ideally happen once, e.g., in Streamlit_def.load_data
        # If it's already datetime, format might not be needed or could cause issues.
        # Assuming 'time' in raw_stock_df might not be datetime yet from all sources.
        try:
            stock_df['time'] = pd.to_datetime(stock_df['time']) # More robust if already datetime
        except Exception as e:
            st.error(f"Lỗi khi chuyển đổi cột 'time' sang định dạng ngày tháng cho biểu đồ: {e}.")
            return pd.DataFrame()

        # Remove rows where Price is NaN, as st.line_chart might have issues
        stock_df.dropna(subset=['Price'], inplace=True)

        return stock_df
    
    @staticmethod
    def _display_date_slider(stock_df):
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
            format="YYYY-MM-DD"
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
    def _display_intrinsic_values_table(raw_df_for_symbols):    # COMMENTED AS TOO LONG FOR LOADING
        # """
        # Displays a table of Graham intrinsic values and other performance metrics
        # for symbols extracted from the raw_df_for_symbols.
        # """
        # st.subheader("Giá trị Nội tại Graham & Chỉ số Hiệu suất", divider="blue")

        # if raw_df_for_symbols.empty:
        #     st.info("Không có dữ liệu để trích xuất mã cổ phiếu cho việc tính giá trị nội tại.")
        #     return

        # symbols_list = [col for col in raw_df_for_symbols.columns if col.lower() != 'time']

        # if not symbols_list:
        #     st.info("Không tìm thấy mã cổ phiếu nào trong dữ liệu để tính giá trị nội tại.")
        #     return

        # # Define start_date and end_date for Stock object initialization context
        # start_date, end_date = Helpers.get_start_end_dates(period=DEFAULT_PERIOD)

        # with st.spinner(f"Đang tính toán giá trị nội tại và chỉ số cho {len(symbols_list)} mã..."):
        #     try:
        #         # metrics_df = Stock.get_multiple_stocks_metrics_df(
        #         #     symbols=symbols_list,
        #         #     start_date=start_date,
        #         #     end_date=end_date
        #         # )

        #         # Call the helper that combines fetched intrinsic values with locally calculated performance
        #         metrics_df = TAstock_def._calculate_combined_stock_metrics(raw_df_for_symbols, symbols_list)


        #         if metrics_df is not None and not metrics_df.empty:
        #             # st.write("Giá trị nội tại Graham và một số chỉ số hiệu suất chính:")
        #             # display_columns = ['symbol', 'graham_intrinsic_value', 'current_price', 'annualized_return_pct', 'daily_std_dev_pct', 'sharpe_ratio']
        #             st.write("Giá trị nội tại Graham và các chỉ số hiệu suất chính (hiệu suất tính trên dữ liệu lịch sử đã tải):")
        #             display_columns = [
        #                 'symbol', 
        #                 'graham_intrinsic_value', 
        #                 'current_price', 
        #                 'geom_mean_daily_return_pct',
        #                 'annualized_return_pct', 
        #                 'daily_std_dev_pct', 
        #                 'annual_std_dev_pct',
        #                 # 'sharpe_ratio' # Add if Calculator provides it and it's desired
        #             ]
        #             existing_display_columns = [col for col in display_columns if col in metrics_df.columns]
                    
        #             # Format Graham Intrinsic Value and Current Price for better readability
        #             formatted_metrics_df = metrics_df[existing_display_columns].copy()
        #             # Format numerical columns
        #             for col_name in ['graham_intrinsic_value', 'current_price']:
        #                 if col_name in formatted_metrics_df:
        #                     formatted_metrics_df[col_name] = formatted_metrics_df[col_name].apply(
        #                         lambda x: f"{x:,.0f}" if pd.notna(x) and isinstance(x, (int, float)) else ("N/A" if pd.isna(x) else x)
        #                     )
        #             for col_name in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']:
        #                 if col_name in formatted_metrics_df:
        #                      formatted_metrics_df[col_name] = formatted_metrics_df[col_name].apply(
        #                         lambda x: f"{x:.2%}" if pd.notna(x) and isinstance(x, (int, float)) else ("N/A" if pd.isna(x) else x)
        #                     )
                             
        #             st.dataframe(formatted_metrics_df.set_index('symbol'))
        #         else:
        #             st.warning("Không thể tính toán hoặc không có dữ liệu giá trị nội tại/chỉ số cho các mã đã chọn.")
            
        #     except Exception as e:
        #         st.error(f"Đã xảy ra lỗi trong quá trình tính toán giá trị nội tại: {e}")
        #         st.error("Vui lòng kiểm tra lại dữ liệu đầu vào hoặc cấu hình.")
        return "n/a"

    @staticmethod
    def _display_history_table(raw_df):
        """Displays a table of the raw historical data."""

        if not raw_df.empty:
            st.dataframe(raw_df) 
            # try:
            #     if not raw_# if not raw_df.columns.empty:
            #         first_column_name = raw_df.columns[0]
            #         st.dataframe(
            #             raw_df,
            #             column_config={
            #                 first_column_name: st.column_config.Column(fixed=True)
            #             }
            #         )
            #     else:
            #         st.info("Dữ liệu không có cột nào để hiển thị trong tab chi tiết.")
            # except TypeError as e:
            #     if "got an unexpected keyword argument 'fixed'" in str(e):
            #         st.warning(
            #             "To freeze columns, please upgrade Streamlit (e.g., `pip install --upgrade streamlit`).\n\n"
            #             "Displaying table without frozen columns for now."
            #         )
            #         st.dataframe(raw_df)  # Fallback for older Streamlit versions
            #     else:
            #         st.error(f"Lỗi hiển thị bảng chi tiết: {e}") # Catch other TypeErrors
            #         raise e  # Re-raise other TypeErrors
            # except Exception as e:
            #     st.error(f"Đã xảy ra lỗi khi hiển thị chi tiết dữ liệu: {e}")
        else:
            st.info("Không có dữ liệu chi tiết để hiển thị.")

    @staticmethod
    # Consider adding @st.cache_data if raw_df_for_symbols can be hashed and this is slow
    def _calculate_combined_stock_metrics(raw_df_for_symbols, symbols_list):
        # """
        # Calculates performance metrics from raw_df and fetches intrinsic values & current price.
        # Returns a DataFrame with combined metrics.
        # Performance metrics are calculated based on the provided raw_df_for_symbols.
        # Intrinsic value and current price are fetched.
        # """
        # # Part 1: Fetch intrinsic value and current price (requires network for financial data)
        # # These values are independent of the historical range in raw_df_for_symbols
        # intrinsic_start_date, intrinsic_end_date = Helpers.get_start_end_dates(period=DEFAULT_PERIOD)
        
        # # Stock.get_multiple_stocks_metrics_df fetches its own historical data for its performance metrics.
        # # We will primarily use it for graham_intrinsic_value and potentially current_price if not easily available otherwise.
        # # The performance metrics from this call will be overridden by calculations from raw_df_for_symbols.
        # base_metrics_df = Stock.get_multiple_stocks_metrics_df(
        #     symbols=symbols_list,
        #     start_date=intrinsic_start_date, # Context for Stock obj init
        #     end_date=intrinsic_end_date      # Context for Stock obj init
        # )
        
        # # Ensure base_metrics_df has expected columns even if empty or None
        # # We are interested in 'symbol', 'graham_intrinsic_value', 'current_price' from this.
        # # Note: Stock.get_multiple_stocks_metrics_df also returns performance metrics,
        # # but we will recalculate them from raw_df_for_symbols.
        # expected_base_cols = ['symbol', 'graham_intrinsic_value', 'current_price']
        # if base_metrics_df is None:
        #     base_metrics_df = pd.DataFrame(columns=expected_base_cols)
        
        # # Ensure 'symbol' column exists if base_metrics_df was completely empty
        # if 'symbol' not in base_metrics_df.columns and symbols_list:
        #     base_metrics_df = pd.DataFrame({'symbol': symbols_list})
        
        # for col in expected_base_cols:
        #     if col not in base_metrics_df.columns:
        #          base_metrics_df[col] = pd.NA # Add missing expected columns

        # # Part 2: Calculate performance metrics from raw_df_for_symbols
        # performance_data_list = []
        
        # # Prepare raw_df_for_symbols for calculation (ensure 'time' is DatetimeIndex)
        # df_for_perf_calc = raw_df_for_symbols.copy()
        # if 'time' in df_for_perf_calc.columns:
        #     try:
        #         df_for_perf_calc['time'] = pd.to_datetime(df_for_perf_calc['time'])
        #         df_for_perf_calc = df_for_perf_calc.set_index('time')
        #     except Exception as e:
        #         st.warning(f"Could not process 'time' column in raw_df for performance calculation: {e}")
        # elif not isinstance(df_for_perf_calc.index, pd.DatetimeIndex): # If 'time' is not a column, assume index is time
        #     try:
        #         df_for_perf_calc.index = pd.to_datetime(df_for_perf_calc.index)
        #     except Exception as e:
        #         st.warning(f"Could not convert DataFrame index to DatetimeIndex for performance calculation: {e}")

        # for symbol in symbols_list:
        #     symbol_perf_metrics = {'symbol': symbol} # Start with symbol
        #     if symbol in df_for_perf_calc.columns and isinstance(df_for_perf_calc.index, pd.DatetimeIndex):
        #         # Create a DataFrame for the single stock's price series
        #         # Calculator.calculate_series_performance_metrics expects a 'close' column or specified price_column
        #         single_stock_df = pd.DataFrame(df_for_perf_calc[symbol].dropna()).rename(columns={symbol: 'close'})
                
        #         if len(single_stock_df) > 1:
        #             try:
        #                 # Reuse Calculator.calculate_series_performance_metrics
        #                 perf_metrics = Calculator.calculate_series_performance_metrics(single_stock_df, price_column='close')
        #                 symbol_perf_metrics.update(perf_metrics)
        #             except Exception as e:
        #                 st.error(f"Error calculating performance for {symbol} from raw_df: {e}")
        #     performance_data_list.append(symbol_perf_metrics)

        # performance_df_from_raw = pd.DataFrame(performance_data_list)

        # # Merge: Use performance metrics from raw_df, and intrinsic/current_price from base_metrics_df
        # # Merge performance_df_from_raw with selected columns from base_metrics_df
        # merged_df = pd.merge(performance_df_from_raw, base_metrics_df[['symbol', 'graham_intrinsic_value', 'current_price']], on='symbol', how='left')
        # return merged_df
        return "n/a"

class TAstock_st:

    @staticmethod
    def history_tab(stock_df):

        from_date, to_date = TAstock_def._display_date_slider(stock_df)
        TAstock_def._display_stock_chart(stock_df, from_date, to_date)


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
                        perf_metrics = Calculator.calculate_series_performance_metrics(single_stock_df, price_column='close')
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
        # Assuming 'raw_df' is the DataFrame you want to display
        
        st.header("Chi tiết Dữ liệu Lịch sử", divider="gray")

        TAstock_def._display_history_table(raw_df)
        
        # Display performance metrics table after history table
        TAstock_st._display_performance_metrics_table(raw_df)
        
        # Add the intrinsic value table display below the historical data table
        # if not raw_df.empty: # Only attempt if there's raw_df to extract symbols from
            # TAstock_def._display_intrinsic_values_table(raw_df)

    
