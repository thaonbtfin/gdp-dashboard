# Tastock Data Management System

This document explains the data management system for the Tastock application, which optimizes data fetching, calculation, and storage for both portfolios and symbols.

## Architecture Overview

The data management system follows an object-oriented design with clear separation of concerns:

1. **DataManager**: Coordinates between fetching, calculating, and storing data
2. **DataFetcher**: Handles fetching stock data and caching it to avoid duplicate requests
3. **DataCalculator**: Handles calculating metrics from stock data
4. **DataStorage**: Handles storing and loading stock data
5. **Cache Utilities**: Provides in-memory caching for improved performance

## Directory Structure

The data is organized in the following structure:

```
data/
├── history_data_all_symbols.csv       # Latest history data for all symbols
├── perf_all_symbols.csv               # Latest performance metrics for all symbols
├── intrinsic_value_all_symbols.csv    # Latest intrinsic values for all symbols
├── fin_all_symbols.csv                # Latest financial data for all symbols
├── 20240701/                          # Date-specific folder (created when running fetching code)
│   ├── history_data_all_symbols_20240701_1200.csv
│   ├── perf_all_symbols_20240701_1200.csv
│   ├── intrinsic_value_all_symbols_20240701_1200.csv
│   ├── fin_all_symbols_20240701_1200.csv
│   ├── VN30/                          # Portfolio-specific folder
│   │   ├── symbols/                   # Individual symbol data for this portfolio
│   │   │   ├── ACB_history_20240701.csv
│   │   │   ├── FPT_history_20240701.csv
│   │   │   └── ...
│   │   ├── history_VN30_20240701_1200.csv    # Merged history for this portfolio
│   │   └── perf_VN30_20240701_1200.csv       # Performance metrics for this portfolio
│   └── VN100/                         # Another portfolio folder
│       └── ...
└── 20240702/                          # Another date-specific folder
    └── ...
```

## Using the Data Management System

### Basic Usage

```python
from src.tastock.data_manager import DataManager
from datetime import datetime, timedelta

# Initialize the data manager
data_manager = DataManager(base_output_dir="data")

# Define date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

# Process a portfolio
portfolio_result = data_manager.process_portfolio(
    portfolio_name="VN30",
    symbols=["ACB", "FPT", "VCB"],
    start_date=start_date,
    end_date=end_date,
    save_data=True
)

# Process all symbols
all_symbols_result = data_manager.process_all_symbols(
    symbols=["ACB", "FPT", "VCB", "VNM", "HPG"],
    start_date=start_date,
    end_date=end_date,
    calculate_intrinsic=True,
    save_data=True
)

# Load latest data
latest_history = data_manager.load_latest_data('history')
latest_perf = data_manager.load_latest_data('perf')
latest_intrinsic = data_manager.load_latest_data('intrinsic')
```

### Advanced Usage

For more advanced usage, you can directly use the specialized classes:

```python
from src.tastock.data_fetcher import DataFetcher
from src.tastock.data_calculator import DataCalculator
from src.tastock.data_storage import DataStorage

# Initialize components
fetcher = DataFetcher(source="VCI")
calculator = DataCalculator()
storage = DataStorage(base_output_dir="data")

# Fetch data
stock_data = fetcher.fetch_stock_data(["ACB", "FPT"], "2024-01-01", "2024-06-30")

# Calculate metrics
metrics = calculator.calculate_performance_metrics("ACB", stock_data["ACB"])

# Save data
storage.save_performance_metrics({"ACB": metrics})
```

### Running Scheduled Updates

You can run scheduled updates using the `scheduled_data_update.py` script:

```bash
# Update data for the last 30 days for all portfolios
python -m src.tastock.scheduled_data_update --days_back 30

# Update data for the last 90 days for VN30 and VN100 portfolios
python -m src.tastock.scheduled_data_update --days_back 90 --portfolios VN30,VN100
```

To schedule regular updates, you can use cron (Linux/Mac) or Task Scheduler (Windows).

Example cron entry to run daily at 6:00 AM:

```
0 6 * * * cd /path/to/gdp-dashboard && python -m src.tastock.scheduled_data_update --days_back 7
```

## Integration with Streamlit

The data management system is integrated with the Streamlit application:

1. When you select "CSV" as the data source, the application will:
   - First try to load data from the new data structure
   - Fall back to the original file if loading from the new structure fails

2. The detail tab will:
   - Try to load performance metrics and intrinsic values from the data files
   - Calculate metrics from raw data if loading from files fails

3. In-memory caching is used to improve performance when loading data files

## Benefits

1. **Reduced API Calls**: Fetches data only once per symbol, even when used in multiple portfolios
2. **Faster Loading**: Uses cached data when available
3. **Organized Storage**: Stores data in a logical folder structure for easy access
4. **Automatic Updates**: Can be scheduled to run regularly
5. **Consistent Calculations**: Uses the same calculation methods for all metrics
6. **Improved Performance**: Uses in-memory caching to reduce disk I/O
7. **Better Code Organization**: Follows OOP design patterns with clear separation of concerns