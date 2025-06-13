import streamlit as st
from streamlit.streamlit_dashboard import Streamlit_def

# ============================
# Step 1: Load and preprocess data
# ============================


# ============================
# Streamlit UI
# ============================

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(page_title='Stock dashboard', layout="wide")
st.title("📊 Statistic stocks")

with st.spinner("Loading data..."):
    df = Streamlit_def.load_data()

history_tab = st.tabs["📁 History"]

with history_tab:
    