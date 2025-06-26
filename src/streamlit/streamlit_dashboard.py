import io
import os
import requests
import streamlit as st
import pandas as pd
from src.constants import API_URL, DATA_HISTORY, GIST_URL_DH_HISTORY, GIST_URL_SAMPLE_HISTORY, GIST_URL_TH_HISTORY, DATA_DIR
from src.tastock.data.data_manager import DataManager

class Streamlit_def:

    @staticmethod
    def load_data():
        source = st.sidebar.radio("Chọn nguồn dữ liệu:", ["CSV","CSV URL", "Upload CSV", "API"], index=0)

        if source == "CSV":
            # Try to load from the new data structure first
            try:
                data_manager = DataManager(base_output_dir=DATA_DIR)
                df = data_manager.load_latest_data('history')
                if not df.empty:
                    return df
            except Exception as e:
                # If loading from data manager fails, fall back to the original file
                pass
                
            # Fall back to original file if data manager loading fails
            DATA_FILENAME = DATA_HISTORY
            try:
                df = pd.read_csv(DATA_FILENAME)
            except Exception as e:
                st.error(f"Không thể tải file CSV: {e}")
                return pd.DataFrame()
            
        elif source == "CSV URL":
            # URL chứa dữ liệu chứng khoán mẫu
            # Để chọn URL khác, bỏ comment dòng tương ứng và comment dòng hiện tại
            
            # url_name_to_display = "GIST_URL_SAMPLE_HISTORY"
            # csv_url = GIST_URL_SAMPLE_HISTORY
            
            url_name_to_display = "GIST_URL_TH_HISTORY"
            csv_url = GIST_URL_TH_HISTORY
            
            # url_name_to_display = "GIST_URL_DH_HISTORY"
            # csv_url = GIST_URL_DH_HISTORY
            try:
                url = csv_url
                # st.info(f"Đang tải dữ liệu từ: {url}")
                st.info(f"Đang tải dữ liệu từ: {url_name_to_display}")
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

        # Perform time conversion and sorting only if df is not empty and 'time' column exists
        if not df.empty:
            if 'time' in df.columns:
                try:
                    # Try to convert 'time' to datetime, handling different formats
                    try:
                        df['time'] = pd.to_datetime(df['time'], format='%Y%m%d')
                    except:
                        df['time'] = pd.to_datetime(df['time'])
                    
                    df.sort_values('time', inplace=True)
                except Exception as e:
                    st.error(f"Lỗi khi xử lý cột 'time': {e}. Đảm bảo cột 'time' có định dạng hợp lệ.")
                    return pd.DataFrame() # Return empty on error
            else:
                # If 'time' column is crucial for all downstream processes,
                # you might want to return pd.DataFrame() here as well.
                # For now, a warning allows detail_tab to still attempt display.
                st.warning("Cột 'time' không được tìm thấy trong dữ liệu tải lên. Một số tính năng có thể không hoạt động đúng.")
        
        return df


# class Streamlit_st: