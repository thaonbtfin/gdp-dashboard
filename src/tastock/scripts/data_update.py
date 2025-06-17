"""
Scheduled Data Update Script

This script fetches and updates stock data for all configured portfolios and symbols.
It can be run manually or scheduled using cron or a similar scheduler.

Usage:
    python -m src.tastock.scripts.data_update [--days_back DAYS] [--portfolios PORTFOLIOS]

Example:
    # Update data for the last 30 days for all portfolios
    python -m src.tastock.scripts.data_update --days_back 30
    
    # Update data for the last 90 days for VN30 and VN100 portfolios
    python -m src.tastock.scripts.data_update --days_back 90 --portfolios VN30,VN100
"""

import os
import argparse
import logging
from datetime import datetime, timedelta

from src.constants import PORTFOLIOS, DATA_DIR
from src.tastock.data.manager import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(DATA_DIR, f"data_update_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("scheduled_data_update")

def get_date_range(days_back=30):
    """Get a date range from days_back days ago to yesterday."""
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def update_data(days_back=30, portfolio_names=None):
    """
    Update data for specified portfolios.
    
    Args:
        days_back (int): Number of days to fetch data for
        portfolio_names (list): List of portfolio names to update, or None for all
    """
    logger.info(f"Starting data update for the last {days_back} days")
    
    # Initialize DataManager
    data_manager = DataManager(base_output_dir=DATA_DIR)
    
    # Get date range
    start_date, end_date = get_date_range(days_back)
    logger.info(f"Date range: {start_date} to {end_date}")
    
    # Determine which portfolios to update
    if portfolio_names:
        portfolios_to_update = {name: PORTFOLIOS.get(name, []) for name in portfolio_names if name in PORTFOLIOS}
    else:
        portfolios_to_update = PORTFOLIOS
    
    if not portfolios_to_update:
        logger.warning("No valid portfolios specified for update")
        return
    
    # Collect all unique symbols across portfolios
    all_symbols = set()
    for symbols in portfolios_to_update.values():
        all_symbols.update(symbols)
    
    # Update all symbols data first
    logger.info(f"Updating data for {len(all_symbols)} unique symbols")
    try:
        data_manager.process_all_symbols(
            symbols=list(all_symbols),
            start_date=start_date,
            end_date=end_date,
            calculate_intrinsic=True,
            save_data=True
        )
        logger.info("Successfully updated all symbols data")
    except Exception as e:
        logger.error(f"Error updating all symbols data: {e}")
    
    # Update each portfolio
    for portfolio_name, symbols in portfolios_to_update.items():
        logger.info(f"Updating portfolio: {portfolio_name} with {len(symbols)} symbols")
        try:
            data_manager.process_portfolio(
                portfolio_name=portfolio_name,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                save_data=True
            )
            logger.info(f"Successfully updated portfolio: {portfolio_name}")
        except Exception as e:
            logger.error(f"Error updating portfolio {portfolio_name}: {e}")
    
    logger.info("Data update completed")

def main():
    """Main function parsing command line arguments and running the update."""
    parser = argparse.ArgumentParser(description='Update stock data for portfolios')
    parser.add_argument('--days_back', type=int, default=30,
                        help='Number of days to fetch data for (default: 30)')
    parser.add_argument('--portfolios', type=str, default=None,
                        help='Comma-separated list of portfolio names to update (default: all)')
    
    args = parser.parse_args()
    
    portfolio_names = None
    if args.portfolios:
        portfolio_names = [name.strip() for name in args.portfolios.split(',')]
    
    update_data(days_back=args.days_back, portfolio_names=portfolio_names)

if __name__ == "__main__":
    main()