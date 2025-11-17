import streamlit as st
from src.chatgpt.chatgpt_dashboard import ChatGPT_def, ChatGPT_st
from src.gdp.gdp_dashboard import GDP_def, GDP_st
from src.streamlit.streamlit_dashboard import Streamlit_def

# ============================
# Step 1: Load and preprocess data
# ============================

gdp_df = GDP_def.get_gdp_data()

# ============================
# Streamlit UI
# ============================

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(page_title='Stock dashboard', layout="wide")
st.title("📊 Statistic stocks")

with st.spinner("Đang tải dữ liệu và huấn luyện mô hình..."):
    df = Streamlit_def.load_data()
    models, latest_predictions_df = ChatGPT_def.models_prediction(df)

gdp_tab, all_tab, detail_tab, backtest_tab, report_tab = st.tabs(["GDP Dashboard","📋 Tất cả cổ phiếu", "🔍 Chi tiết cổ phiếu", "🧪 Giả lập hiệu suất chiến lược", "📈 Hiệu năng mô hình"])

with gdp_tab:
    GDP_st.gdp_tab(gdp_df)

with all_tab:
    ChatGPT_st.all_tab(latest_predictions_df)

with detail_tab:
    ChatGPT_st.detail_tab(models)

with backtest_tab:
    ChatGPT_st.backtest_tab(models)

with report_tab:
    ChatGPT_st.report_tab(models)
    