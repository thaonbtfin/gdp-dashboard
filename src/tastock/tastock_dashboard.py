import streamlit as st
import streamlit as st
import pandas as pd
import math

class TAstock_def:

    @staticmethod
    def get_stock_data(df):
        """Grab stock history data from a CSV file and melt it."""

        # DATA_FILENAME = Path(__file__).parent / 'data/history_data.csv'
        # DATA_FILENAME = DATA_HISTORY
        # raw_stock_df = pd.read_csv(DATA_FILENAME)

        raw_stock_df = df

        # Identify symbol columns (all columns except 'time')
        symbol_columns = [col for col in raw_stock_df.columns if col != 'time']

        # Melt the DataFrame
        # 'time' column remains as is.
        # Other columns (stock symbols) are unpivoted into two new columns: 'Symbol' and 'Price'.
        stock_df = raw_stock_df.melt(
            id_vars=['time'],
            value_vars=symbol_columns,
            var_name='Symbol',
            value_name='Price',
        )

        # Convert 'time' from YYYYMMDD integer to datetime objects
        stock_df['time'] = pd.to_datetime(stock_df['time'], format='%Y%m%d')
        
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


class TAstock_st:

    @staticmethod
    def history_tab(stock_df):
        '''
        # :chart_with_upwards_trend: Stock History Dashboard

        Browse stock price data.
        '''

        from_date, to_date = TAstock_def._display_date_slider(stock_df)
        TAstock_def._display_stock_chart(stock_df, from_date, to_date)

        # The metrics display is now part of _display_stock_chart, which calls _display_stock_metric

    @staticmethod
    def detail_tab(stock_df):
        # Assuming 'stock_df' is the DataFrame you want to display
        if not stock_df.empty:
            try:
                first_column_name = stock_df.columns[0]
                st.dataframe(
                    stock_df,
                    column_config={
                        # This will freeze the first column (e.g., 'time')
                        first_column_name: st.column_config.Column(fixed=True)
                    }
                )
            except TypeError as e:
                if "got an unexpected keyword argument 'fixed'" in str(e):
                    st.warning(
                        "To freeze columns, please upgrade Streamlit (e.g., `pip install --upgrade streamlit`).\n\n"
                        "Displaying table without frozen columns for now."
                    )
                    st.dataframe(stock_df)  # Fallback for older Streamlit versions
                else:
                    raise e  # Re-raise other TypeErrors
        else:
            st.write("DataFrame is empty.")

    
