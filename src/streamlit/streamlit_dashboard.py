import io
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


# class Streamlit_st: