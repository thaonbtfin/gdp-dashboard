import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_GDP = PROJECT_DIR + "/data/gdp_data.csv"
DATA_HISTORY = PROJECT_DIR + "/data/history_data.csv"

API_URL = "https://api.mocki.io/v2/12345678/stockdata"  # Replace with actual API URL

GIST_URL_SAMPLE_HISTORY = "https://gist.githubusercontent.com/thaonbtfin/fcb2906734735389faa0d32c8b47d456/raw/5dcc232d24f45b95e388e334c3ceeddc874752e9/sample_history_stockData.csv"
GIST_URL_TH_HISTORY="https://gist.githubusercontent.com/thaonbtfin/702773bb825afd63553f515b61645e8b/raw/8fe2a6cfe9cb5db792eabf07bf0d61d7f525b5c0/TH_toGoogleSheet.csv"
GIST_URL_DH_HISTORY="https://gist.githubusercontent.com/thaonbtfin/4c3a7018a1058d5f1e31fcf91d2367a9/raw/6205af6e9522710c4e88c80cbe234c1592fa5d05/DH_toGoogleSheet.csv"