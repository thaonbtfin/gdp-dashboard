import pandas as pd
import numpy as np
import streamlit as st
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# ============================
# Step 1: Load and preprocess data
# ============================
@st.cache_data
def load_data():
    url = "https://gist.githubusercontent.com/thaonbtfin/fcb2906734735389faa0d32c8b47d456/raw/5dcc232d24f45b95e388e334c3ceeddc874752e9/sample_history_stockData.csv"
    df = pd.read_csv(url)
    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d')
    df.sort_values('time', inplace=True)
    return df

def create_features(df, stock):
    data = df[['time', stock]].copy()
    data.rename(columns={stock: 'close'}, inplace=True)

    # Chỉ báo kỹ thuật đơn giản
    data['ma5'] = data['close'].rolling(window=5).mean()
    data['ma10'] = data['close'].rolling(window=10).mean()
    data['return_1d'] = data['close'].pct_change(1)
    data['return_5d'] = data['close'].pct_change(5)

    # Tạo nhãn hành động
    future_return = data['close'].shift(-5) / data['close'] - 1
    data['action'] = pd.cut(
        future_return,
        bins=[-np.inf, -0.05, 0.05, np.inf],
        labels=['Sell', 'Hold', 'Buy']
    )
    data.dropna(inplace=True)
    return data

# ============================
# Step 2: Train model
# ============================
def train_model(data):
    X = data[['ma5', 'ma10', 'return_1d', 'return_5d']]
    y = data['action']

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, target_names=le.classes_)
    return model, report, X_test, y_test, y_pred, le

# ============================
# Step 3: Streamlit UI
# ============================
st.set_page_config(page_title="AI Dự đoán PNJ", layout="wide")
st.title("📈 Hệ thống AI khuyến nghị giao dịch - PNJ")

with st.spinner("Đang tải dữ liệu và huấn luyện mô hình..."):
    df = load_data()
    pnj_data = create_features(df, 'PNJ')
    model, report, X_test, y_test, y_pred, le = train_model(pnj_data)  # Unpack all 6 values


st.subheader("1️⃣ Thống kê mô hình")
st.json({k: report[k] for k in ['Buy', 'Hold', 'Sell', 'accuracy']})

st.subheader("2️⃣ Dự đoán gần nhất")
pred_data = pnj_data.tail(10).copy()
pred_features = pred_data[['ma5', 'ma10', 'return_1d', 'return_5d']]
pred_data['predicted_action'] = le.inverse_transform(model.predict(pred_features))
st.dataframe(pred_data[['time', 'close', 'ma5', 'ma10', 'predicted_action']].reset_index(drop=True))

st.success("✅ Mô hình XGBoost đã hoạt động! Bạn có thể mở rộng cho nhiều cổ phiếu khác.")
