# 📈 TAstock - Vietnamese Stock Analysis Dashboard

A comprehensive Streamlit application for Vietnamese stock market analysis with multiple investment methodologies.

## Features

- **📊 Multi-Portfolio Analysis**: VN30, VN100, DH, TH portfolios
- **💼 Investment Analysis**: Value Investing, CANSLIM, Technical Analysis
- **📈 Technical Indicators**: 15+ indicators with CafeF-style interface
- **🔍 Stock Details**: Performance metrics, intrinsic values
- **📁 BizUni Integration**: Automated data crawling

## Quick Start

1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run TAstock dashboard**
   ```bash
   streamlit run streamlit_app_tastock.py
   ```
   
   Or use the one-click script:
   ```bash
   ./run_tastock.sh
   ```

## Data Pipeline

```bash
# Run complete data pipeline
python src/tastock/workflows/wf_stock_data_updater.py
```

## Documentation

- [Data Management](src/tastock/README.md)
- [Technical Analysis Guide](doc/readme_technical_analysis.md)
- [Investment Principles](doc/references/INVESTMENT_PRINCIPLES.md)