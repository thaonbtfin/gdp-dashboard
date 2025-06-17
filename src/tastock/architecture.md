# Tastock Architecture

## Module Structure

```
src/tastock/
├── __init__.py             # Exports key classes
├── core/                   # Core domain models
│   ├── __init__.py
│   ├── stock.py            # Stock class
│   └── portfolio.py        # Portfolio class
├── data/                   # Data management
│   ├── __init__.py
│   ├── calculator.py       # Financial calculations
│   ├── data_calculator.py  # Calculation with caching
│   ├── data_fetcher.py     # Fetching with caching
│   ├── data_storage.py     # Data storage operations
│   ├── fetcher.py          # Raw data fetching
│   └── manager.py          # Coordinates data operations
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── cache_utils.py      # Caching utilities
│   └── helpers.py          # Helper functions
├── ui/                     # User interface
│   ├── __init__.py
│   └── dashboard.py        # Streamlit dashboard components
└── scripts/                # Executable scripts
    ├── __init__.py
    ├── data_update.py      # Scheduled data updates
    └── examples.py         # Usage examples
```

## Class Diagram

```
┌─────────────────┐     uses     ┌─────────────────┐
│   DataManager   │─────────────▶│   DataFetcher   │
└─────────────────┘              └─────────────────┘
         │                                │
         │                                │
         │ uses                           │ uses
         │                                │
         ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│ DataCalculator  │              │     Stock       │
└─────────────────┘              └─────────────────┘
         │                                ▲
         │                                │
         │ uses                           │ uses
         │                                │
         ▼                                │
┌─────────────────┐     uses     ┌─────────────────┐
│  DataStorage    │─────────────▶│   Portfolio     │
└─────────────────┘              └─────────────────┘
         │                                ▲
         │                                │
         │ uses                           │ uses
         │                                │
         ▼                                │
┌─────────────────┐              ┌─────────────────┐
│  cache_utils    │              │   Calculator    │
└─────────────────┘              └─────────────────┘
```

## Component Responsibilities

### Core Module
- **Stock**: Represents a stock and its data
- **Portfolio**: Represents a portfolio of stocks

### Data Module
- **DataManager**: Coordinates between fetching, calculating, and storing data
- **DataFetcher**: Handles fetching stock data with caching
- **DataCalculator**: Handles calculating metrics with caching
- **DataStorage**: Handles storing and loading stock data
- **Calculator**: Provides calculation methods for financial metrics
- **Fetcher**: Handles raw data fetching

### Utils Module
- **cache_utils**: Provides utilities for in-memory caching
- **helpers**: Provides helper functions for data processing and file management

### UI Module
- **dashboard**: Provides Streamlit UI components for the dashboard

### Scripts Module
- **data_update**: Script for scheduled data updates
- **examples**: Example scripts demonstrating how to use the DataManager

## Data Flow

1. **Data Fetching**:
   - DataManager requests data from DataFetcher
   - DataFetcher checks its cache and fetches only what's needed
   - Fetched data is returned to DataManager

2. **Data Calculation**:
   - DataManager sends data to DataCalculator
   - DataCalculator performs calculations and caches results
   - Calculation results are returned to DataManager

3. **Data Storage**:
   - DataManager sends data to DataStorage
   - DataStorage saves data in the appropriate format and location
   - File paths are returned to DataManager

4. **Data Loading**:
   - Application requests data from DataManager
   - DataManager requests data from DataStorage
   - DataStorage loads data from files using cache_utils
   - Loaded data is returned to the application

5. **UI Display**:
   - Streamlit app loads data using DataManager
   - UI components in dashboard.py display the data
   - User interacts with the dashboard