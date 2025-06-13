import io
import math
import requests
import streamlit as st
import pandas as pd
from src.constants import API_URL, DATA_HISTORY, GIST_URL_DH_HISTORY, GIST_URL_SAMPLE_HISTORY, GIST_URL_TH_HISTORY

class Streamlit_def:

    @staticmethod
    def load_data():
        source = st.sidebar.radio("Chọn nguồn dữ liệu:", ["CSV","CSV URL", "Upload CSV", "API"], index=0)

        if source == "CSV":
            # DATA_FILENAME = Path(__file__).parent/'data/history_data.csv'
            DATA_FILENAME = DATA_HISTORY
            raw_df = pd.read_csv(DATA_FILENAME)
            try:
                
                df = pd.read_csv(DATA_FILENAME)
            except Exception as e:
                st.error(f"Không thể tải file CSV: {e}")
                return pd.DataFrame()
            
        elif source == "CSV URL":
            # URL chứa dữ liệu chứng khoán mẫu
            # csv_url = GIST_URL_SAMPLE_HISTORY
            csv_url = GIST_URL_TH_HISTORY
            # csv_url = GIST_URL_DH_HISTORY
            try:
                url = csv_url
                st.info(f"Đang tải dữ liệu từ: {url}")
                response = requests.get(url)
                df = pd.read_csv(io.StringIO(response.text))
            except Exception as e:
                st.error(f"Không thể tải file CSV: {e}")
                return pd.DataFrame()

        elif source == "Upload CSV":
            uploaded_file = st.sidebar.file_uploader("Upload file CSV chứa dữ liệu chứng khoán", type=["csv"])
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                except Exception as e:
                    st.error(f"Lỗi đọc file CSV: {e}")
                    return pd.DataFrame()
            else:
                return pd.DataFrame()

        elif source == "API":
            try:
                api_url = API_URL
                response = requests.get(api_url)
                json_data = response.json()
                df = pd.DataFrame(json_data)
            except Exception as e:
                st.error(f"Không thể tải dữ liệu từ API: {e}")
                return pd.DataFrame()

        df['time'] = pd.to_datetime(df['time'], format='%Y%m%d')
        df.sort_values('time', inplace=True)
        # # Melt wide to long format: columns 'time', 'ticker', 'close'
        # value_vars = [col for col in df.columns if col not in ['time', 'VNINDEX']]
        # df = df.melt(id_vars=['time'], value_vars=value_vars, var_name='ticker', value_name='close')
        return df


class Streamlit_st:
    
    @staticmethod
    def gdp_tab(gdp_df):
        # Set the title that appears at the top of the page.
        '''
        # :earth_americas: GDP dashboard

        Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
        notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
        But it's otherwise a great (and did I mention _free_?) source of data.
        '''

        # Add some spacing
        ''
        ''

        min_value = gdp_df['Year'].min()
        max_value = gdp_df['Year'].max()

        from_year, to_year = st.slider(
            'Which years are you interested in?',
            min_value=min_value,
            max_value=max_value,
            value=[min_value, max_value])

        countries = gdp_df['Country Code'].unique()

        if not len(countries):
            st.warning("Select at least one country")

        selected_countries = st.multiselect(
            'Which countries would you like to view?',
            countries,
            ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

        ''
        ''
        ''

        # Filter the data
        filtered_gdp_df = gdp_df[
            (gdp_df['Country Code'].isin(selected_countries))
            & (gdp_df['Year'] <= to_year)
            & (from_year <= gdp_df['Year'])
        ]

        st.header('GDP over time', divider='gray')

        ''

        st.line_chart(
            filtered_gdp_df,
            x='Year',
            y='GDP',
            color='Country Code',
        )

        ''
        ''


        first_year = gdp_df[gdp_df['Year'] == from_year]
        last_year = gdp_df[gdp_df['Year'] == to_year]

        st.header(f'GDP in {to_year}', divider='gray')

        ''

        cols = st.columns(4)

        for i, country in enumerate(selected_countries):
            col = cols[i % len(cols)]

            with col:
                first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
                last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

                if math.isnan(first_gdp):
                    growth = 'n/a'
                    delta_color = 'off'
                else:
                    growth = f'{last_gdp / first_gdp:,.2f}x'
                    delta_color = 'normal'

                st.metric(
                    label=f'{country} GDP',
                    value=f'{last_gdp:,.0f}B',
                    delta=growth,
                    delta_color=delta_color
                )