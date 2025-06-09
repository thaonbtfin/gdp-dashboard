import streamlit as st
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# ----- Huấn luyện mô hình AI XGBoost -----
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

    le_type = LabelEncoder()
    le_label = LabelEncoder()

    df["loại_encoded"] = le_type.fit_transform(df["loại_danh_mục"])
    df["label_encoded"] = le_label.fit_transform(df["nhãn_xu_hướng"])

    X = df[["giá_p1", "giá_p2", "giá_p3", "giá_p4", "giá_p5", "lãi_lỗ_%", "loại_encoded"]]
    y = df["label_encoded"]

    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model.fit(X, y)

    return model, le_type, le_label

model, label_encoder_type, label_encoder_y = train_model()

# ----- Giao diện Streamlit -----
st.title("🌐 Hệ thống AI hỗ trợ đầu tư chứng khoán (XGBoost)")

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
    loai_encoded = label_encoder_type.transform([loai_dm])[0]
    X_input = [[giá_p1, giá_p2, giá_p3, giá_p4, giá_p5, lai_lo, loai_encoded]]

    xu_huong_encoded = model.predict(X_input)[0]
    xu_huong = label_encoder_y.inverse_transform([xu_huong_encoded])[0]

    # Logic khuyến nghị
    if xu_huong == "Tăng" and lai_lo < 20:
        khuyen_nghi = "GIỮ HOẶC MUA THÊM"
    elif xu_huong == "Giảm" and lai_lo > 15:
        khuyen_nghi = "BÁN CHỐT LỜI"
    elif xu_huong == "Giảm" and lai_lo < -10:
        khuyen_nghi = "BÁN CẮT LỖ"
    elif xu_huong == "Giảm" and -10 <= lai_lo <= 15:
        khuyen_nghi = "GIỮ CHỜ THÊM"
    else:
        khuyen_nghi = "KHÔNG RÕ - CẦN XEM XÉT THÊM"

    st.success(f"**Xu hướng dự đoán:** {xu_huong}")
    st.info(f"**Khuyến nghị:** {khuyen_nghi}")
