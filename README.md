# 📈 TAstock - Vietnamese Stock Analysis Dashboard

A comprehensive Streamlit application for Vietnamese stock market analysis with multiple investment methodologies and automated data pipelines.

## ✨ Features

### 📊 Multi-Portfolio Analysis
- **VN30/VN100**: Market indices from TradingView
- **User Portfolios**: LongTerm, MidTerm from Google Sheets
- **BizUni Portfolio**: Value investing analysis
- **Real-time Updates**: Automated data refresh

### 💼 Investment Analysis
- **Value Investing**: P/E, ROE, intrinsic value calculations
- **CANSLIM**: Growth and momentum analysis
- **Technical Analysis**: 15+ indicators with CafeF-style interface
- **Investment Signals**: BUY/SELL recommendations with confidence scores

### 📈 Advanced Features
- **Performance Metrics**: Historical analysis and projections
- **Risk Assessment**: Portfolio diversification analysis
- **Market Insights**: Sector analysis and trends
- **Notification System**: Priority-based investment alerts

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/thaonbtfin/gdp-dashboard.git
cd gdp-dashboard

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application

**Option 1: Desktop Launcher (Recommended)**
- **macOS**: Copy `launch_tastock_mac.command` to Desktop → Double-click
- **Windows**: Copy `launch_tastock_win.bat` to Desktop → Double-click
- Browser opens automatically at `http://localhost:8501`
- **To Stop**: Press `Ctrl+C` in terminal window

**Option 2: Command Line**
```bash
# Direct command
streamlit run streamlit_app_tastock.py
```

### 3. Update Data (Optional)
```bash
# Complete data pipeline (recommended first run)
python src/tastock/workflows/wf_stock_data_updater.py

# Or use the in-app update button in Streamlit sidebar
```

## 📁 Project Structure

```
gdp-dashboard/
├── 📊 streamlit_app_tastock.py    # Main application
├── 📋 requirements.txt            # Dependencies
├── 🔧 run_tastock.sh             # Launch script
├── 📂 src/
│   ├── tastock/                   # Core analysis engine
│   │   ├── analysis/              # Investment methodologies
│   │   ├── crawlers/              # Data collection
│   │   ├── data/                  # Data management
│   │   ├── ui/                    # Streamlit components
│   │   └── workflows/             # Automation scripts
│   └── portfolio_*.py             # Portfolio management
├── 📂 data/                       # Stock data storage
├── 📂 doc/                        # Documentation
└── 📂 test/                       # Unit tests
```

## 🔄 Data Pipeline

The application uses a sophisticated data pipeline:

1. **Data Collection**: CafeF crawler for stock prices
2. **Portfolio Loading**: Multi-source portfolio management
3. **Analysis Engine**: Investment signal generation
4. **Storage**: Organized date-based data structure
5. **Caching**: Performance optimization

```bash
# Manual pipeline execution
python src/tastock/workflows/wf_stock_data_updater.py

# Individual components
python src/tastock/scripts/crawl_cafef_data_and_save_portfolios_to_root_data_folder.py
python src/tastock/scripts/generate_investment_signals.py
python src/tastock/crawlers/bizuni_crawler.py
```

### 📅 Automated Scheduling

**Setup daily updates at 6 PM (weekdays only):**

See [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md) for detailed instructions.

## 📚 Documentation

- **[User Guide](doc/USER_GUIDE.md)**: Complete usage instructions
- **[Portfolio Architecture](doc/PORTFOLIO_ARCHITECTURE.md)**: System design
- **[Data Management](src/tastock/README.md)**: Technical details
- **[Technical Analysis](doc/readme_technical_analysis.md)**: Analysis methods
- **[Investment Principles](doc/references/INVESTMENT_PRINCIPLES.md)**: Strategy guide

## 🎯 Key Benefits

- **⚡ Fast**: Cached data, optimized performance
- **🔄 Automated**: Complete data pipeline
- **📊 Comprehensive**: Multiple analysis methods
- **🎨 User-friendly**: Intuitive Streamlit interface
- **📱 Responsive**: Works on desktop and mobile
- **🔒 Reliable**: Robust error handling and fallbacks

## 🛠️ Advanced Usage

### Desktop Shortcuts
- **Create Desktop Icon**: Copy launcher files to Desktop for one-click access
- **Resource Management**: Press `Ctrl+C` to stop server and free port 8501
- **Auto Browser**: Launcher automatically opens browser to dashboard

### Portfolio Management
```bash
# CLI tools
python portfolio_cli.py show      # View all portfolios
python portfolio_cli.py refresh   # Force refresh
```

### Custom Analysis
```python
from src.tastock.analysis.investment_analyzer import InvestmentAnalyzer

analyzer = InvestmentAnalyzer()
signals = analyzer.analyze_portfolio(['ACB', 'FPT', 'VCB'])
```

## 📈 Performance

- **Startup Time**: ~1 second (cached data)
- **Portfolio Loading**: 0.01 seconds
- **Data Pipeline**: ~5 minutes (complete update)
- **Memory Usage**: Optimized with caching

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CafeF**: Stock data provider
- **BizUni**: Value analysis data
- **TradingView**: Market indices
- **Streamlit**: Web framework