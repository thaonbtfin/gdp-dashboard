# 📈 TAstock User Guide

## 🚀 Quick Start

### VIEW STREAMLIT SITE
```bash
streamlit run streamlit_app_tastock.py
```
- Data will be automatically loaded from the latest `data/YYYYMMDD/` folder
- Portfolio symbols are read directly from CSV file headers
- No external API calls needed during dashboard usage

## 🔄 Update Data

You have **3 options** to update data:

### Option 1: Complete Data Update (In Streamlit)
- Click **📊 Complete Data Update** button in Streamlit sidebar
- Runs full data pipeline automatically (takes ~5 minutes)
- Page refreshes automatically when complete
- **Most convenient option**

### Option 2: Complete Data Pipeline (Command Line)
```bash
python src/tastock/workflows/wf_stock_data_updater.py
```
- Same as Option 1 but run manually
- **Then**: Refresh browser to see updated data

### Option 3: Refresh Portfolios Only
- Click **🔄 Refresh Portfolios** button in Streamlit sidebar
- Only refreshes portfolio symbol lists (if composition changed)
- Does **not** update stock prices or analysis data

## 📁 Data Structure

After running the workflow, data is organized as:
```
data/
├── 20251118/                    # Latest date folder
│   ├── VN30/
│   │   └── history_data_all_symbols.csv    # VN30 stock data
│   ├── VN100/
│   │   └── history_data_all_symbols.csv    # VN100 stock data
│   ├── LongTerm/
│   │   └── history_data_all_symbols.csv    # User portfolio data
│   └── BizUni/
│       └── history_data_all_symbols.csv    # BizUni portfolio data
├── investment_signals_complete.csv         # Investment analysis
└── bizuni_cpgt.csv                         # BizUni intrinsic values
```

## 🎯 Portfolio Sources

- **VN30/VN100**: From TradingView (market indices)
- **LongTerm/MidTerm**: From Google Sheets (user portfolios)  
- **BizUni**: From bizuni_crawler (value analysis)

## ⚡ Performance

- **Portfolio loading**: 0.01s (reads from CSV headers)
- **Dashboard startup**: ~1s (all data from local CSV files)
- **No external dependencies**: Works offline after data pipeline runs