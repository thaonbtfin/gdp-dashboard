import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ----- Huấn luyện mô hình AI đơn giản -----
def train_model():
    np.random.seed(42)
    n_samples = 200
    data = {
        "giá_p1": np.random.uniform(20, 100, n_samples),
        "giá_p2": np.random.uniform(20, 100, n_samples),
        "giá_p3": np.random.uniform(20, 100, n_samples),
        "giá_p4": np.random.uniform(20, 100, n_samples),
        "giá_p5": np.random.uniform(20, 100, n_samples),
        "lãi_lỗ_%": np.random.uniform(-20, 40, n_samples),
        "loại_danh_mục": np.random.choice(["Dài hạn", "Trung hạn", "Ngắn hạn"], n_samples),
    }
    df = pd.DataFrame(data)
    df["nhãn_xu_hướng"] = np.where(df["giá_p5"] > df["giá_p4"], "Tăng", "Giảm")
    le = LabelEncoder()
    df["loại_encoded"] = le.fit_transform(df["loại_danh_mục"])
    X = df[["giá_p1", "giá_p2", "giá_p3", "giá_p4", "giá_p5", "lãi_lỗ_%", "loại_encoded"]]
    y = df["nhãn_xu_hướng"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model, le

model, label_encoder = train_model()

# ----- Giao diện Web -----
st.title("🌎 Hệ thống AI hỗ trợ đầu tư chứng khoán")

st.markdown("""
**Nhập thông tin dữ liệu cổ phiếu:**
""")

ma_cp = st.text_input("Mã cổ phiếu", "FPT")
loai_dm = st.selectbox("Loại danh mục", ["Dài hạn", "Trung hạn", "Ngắn hạn"])
giá_p1 = st.number_input("Giá đóng cửa phiên 1", 0.0, 1000.0, 90.0)
giá_p2 = st.number_input("Giá đóng cửa phiên 2", 0.0, 1000.0, 92.0)
giá_p3 = st.number_input("Giá đóng cửa phiên 3", 0.0, 1000.0, 91.5)
giá_p4 = st.number_input("Giá đóng cửa phiên 4", 0.0, 1000.0, 94.0)
giá_p5 = st.number_input("Giá đóng cửa phiên 5", 0.0, 1000.0, 95.0)
lai_lo = st.number_input("Lãi/Lỗ (%)", -100.0, 100.0, 5.0)

if st.button("✨ Phân tích và khuyến nghị"):
    loai_encoded = label_encoder.transform([loai_dm])[0]
    X_input = [[giá_p1, giá_p2, giá_p3, giá_p4, giá_p5, lai_lo, loai_encoded]]
    xu_huong = model.predict(X_input)[0]

    # Logic khuyến nghị
    if xu_huong == "Tăng" and lai_lo < 20:
        khuyen_nghi = "GIữ hoặc MUA THÊM"
    elif xu_huong == "Giảm" and lai_lo > 15:
        khuyen_nghi = "BÁN CHỐT LỜi"
    elif xu_huong == "Giảm" and lai_lo < -10:
        khuyen_nghi = "BÁN CẮt Lỗ"
    elif xu_huong == "Giảm" and -10 <= lai_lo <= 15:
        khuyen_nghi = "GIữ chờ thêm"
    else:
        khuyen_nghi = "KHÔNG RÕ - CẦN XEM XÉT THÎm"

    st.success(f"**Xu hướng dự đoán:** {xu_huong}")
    st.info(f"**Khuyến nghị:** {khuyen_nghi}")
