"""
Data Utilities for Cryptocurrency Analysis
Provides data processing, backup, and analysis functions
"""

import pandas as pd
import os
import shutil
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import glob


class CryptoDataUtils:
    """Utility class for cryptocurrency data management and analysis"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize data utilities"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.data_dir = self.config["data"]["data_directory"]
        self.historical_dir = self.config["data"]["historical_directory"]
        self.snapshots_dir = self.config["data"]["snapshots_directory"]
        self.logs_dir = self.config["data"]["logs_directory"]
        
        self.logger = logging.getLogger(__name__)
    
    def backup_data(self, backup_dir: str = None) -> str:
        """Create a backup of all cryptocurrency data"""
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_{timestamp}"
        
        backup_path = os.path.join(self.data_dir, backup_dir)
        
        try:
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup historical data
            historical_backup = os.path.join(backup_path, "historical")
            if os.path.exists(self.historical_dir):
                shutil.copytree(self.historical_dir, historical_backup, dirs_exist_ok=True)
            
            # Backup snapshots
            snapshots_backup = os.path.join(backup_path, "daily_snapshots")
            if os.path.exists(self.snapshots_dir):
                shutil.copytree(self.snapshots_dir, snapshots_backup, dirs_exist_ok=True)
            
            # Backup logs
            logs_backup = os.path.join(backup_path, "logs")
            if os.path.exists(self.logs_dir):
                shutil.copytree(self.logs_dir, logs_backup, dirs_exist_ok=True)
            
            self.logger.info(f"Data backup created successfully at: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_data(self, backup_path: str):
        """Restore data from backup"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup directory not found: {backup_path}")
            
            # Restore historical data
            historical_backup = os.path.join(backup_path, "historical")
            if os.path.exists(historical_backup):
                if os.path.exists(self.historical_dir):
                    shutil.rmtree(self.historical_dir)
                shutil.copytree(historical_backup, self.historical_dir)
            
            # Restore snapshots
            snapshots_backup = os.path.join(backup_path, "daily_snapshots")
            if os.path.exists(snapshots_backup):
                if os.path.exists(self.snapshots_dir):
                    shutil.rmtree(self.snapshots_dir)
                shutil.copytree(snapshots_backup, self.snapshots_dir)
            
            self.logger.info(f"Data restored successfully from: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore data: {e}")
            raise
    
    def get_available_cryptocurrencies(self) -> List[str]:
        """Get list of cryptocurrency tickers with historical data"""
        if not os.path.exists(self.historical_dir):
            return []
        
        files = glob.glob(os.path.join(self.historical_dir, "*_historical.csv"))
        tickers = [os.path.basename(f).replace("_historical.csv", "") for f in files]
        return sorted(tickers)
    
    def load_historical_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load historical data for a specific cryptocurrency ticker"""
        # Handle both original and cleaned ticker names
        clean_ticker = ticker.replace(':', '_').replace('/', '_')
        filename = f"{clean_ticker}_historical.csv"
        filepath = os.path.join(self.historical_dir, filename)
        
        if not os.path.exists(filepath):
            self.logger.warning(f"Historical data file not found: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
        except Exception as e:
            self.logger.error(f"Failed to load historical data for {ticker}: {e}")
            return None
    
    def load_daily_snapshot(self, date: str = None) -> Optional[pd.DataFrame]:
        """Load daily snapshot data for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        filename = f"{date}_snapshot.csv"
        filepath = os.path.join(self.snapshots_dir, filename)
        
        if not os.path.exists(filepath):
            self.logger.warning(f"Snapshot file not found: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            self.logger.error(f"Failed to load snapshot for {date}: {e}")
            return None
    
    def get_available_snapshots(self) -> List[str]:
        """Get list of available daily snapshots"""
        if not os.path.exists(self.snapshots_dir):
            return []
        
        files = glob.glob(os.path.join(self.snapshots_dir, "*_snapshot.csv"))
        dates = [os.path.basename(f).replace("_snapshot.csv", "") for f in files]
        return sorted(dates)
    
    def calculate_portfolio_metrics(self, tickers: List[str], weights: List[float] = None) -> Dict:
        """Calculate portfolio metrics for selected cryptocurrency tickers"""
        if weights is None:
            weights = [1.0 / len(tickers)] * len(tickers)
        
        if len(tickers) != len(weights):
            raise ValueError("Number of tickers must match number of weights")
        
        portfolio_data = []
        
        for ticker, weight in zip(tickers, weights):
            df = self.load_historical_data(ticker)
            if df is not None:
                # Use 'close' price for Polygon.io data
                price_column = 'close' if 'close' in df.columns else 'current_price'
                df['weighted_price'] = df[price_column] * weight
                portfolio_data.append(df[['date', 'weighted_price']])
        
        if not portfolio_data:
            return {}
        
        # Combine all weighted prices
        portfolio_df = portfolio_data[0]
        for df in portfolio_data[1:]:
            portfolio_df = portfolio_df.merge(df, on='date', how='outer', suffixes=('', '_temp'))
            portfolio_df['weighted_price'] = portfolio_df['weighted_price'].fillna(0) + portfolio_df['weighted_price_temp'].fillna(0)
            portfolio_df = portfolio_df.drop('weighted_price_temp', axis=1)
        
        portfolio_df = portfolio_df.sort_values('date')
        portfolio_df['daily_return'] = portfolio_df['weighted_price'].pct_change()
        
        # Calculate metrics
        total_return = (portfolio_df['weighted_price'].iloc[-1] / portfolio_df['weighted_price'].iloc[0] - 1) * 100
        volatility = portfolio_df['daily_return'].std() * (365 ** 0.5) * 100
        sharpe_ratio = portfolio_df['daily_return'].mean() / portfolio_df['daily_return'].std() * (365 ** 0.5)
        
        max_drawdown = 0
        peak = portfolio_df['weighted_price'].iloc[0]
        for price in portfolio_df['weighted_price']:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_return_percent': total_return,
            'annualized_volatility_percent': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_percent': max_drawdown,
            'start_date': portfolio_df['date'].iloc[0].strftime('%Y-%m-%d'),
            'end_date': portfolio_df['date'].iloc[-1].strftime('%Y-%m-%d'),
            'total_days': len(portfolio_df)
        }
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary report of all collected data"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'cryptocurrencies': {},
            'snapshots': {},
            'data_quality': {}
        }
        
        # Cryptocurrency summary
        available_cryptos = self.get_available_cryptocurrencies()
        report['cryptocurrencies']['total_count'] = len(available_cryptos)
        report['cryptocurrencies']['list'] = available_cryptos
        
        # Snapshot summary
        available_snapshots = self.get_available_snapshots()
        report['snapshots']['total_count'] = len(available_snapshots)
        report['snapshots']['date_range'] = {
            'earliest': available_snapshots[0] if available_snapshots else None,
            'latest': available_snapshots[-1] if available_snapshots else None
        }
        
        # Data quality check
        missing_data = []
        for crypto in available_cryptos:
            df = self.load_historical_data(crypto)
            if df is not None:
                null_count = df.isnull().sum().sum()
                if null_count > 0:
                    missing_data.append({'crypto': crypto, 'null_values': int(null_count)})
        
        report['data_quality']['cryptocurrencies_with_missing_data'] = missing_data
        
        return report
    
    def export_combined_data(self, output_file: str = "combined_crypto_data.csv"):
        """Export all data into a single combined CSV file"""
        combined_data = []
        
        # Add historical data
        for crypto in self.get_available_cryptocurrencies():
            df = self.load_historical_data(crypto)
            if df is not None:
                df['data_type'] = 'historical'
                combined_data.append(df)
        
        # Add snapshot data
        for date in self.get_available_snapshots():
            df = self.load_daily_snapshot(date)
            if df is not None:
                # Rename columns to match historical data format
                df = df.rename(columns={
                    'current_price_usd': 'price_usd',
                    'volume_24h_usd': 'volume_24h_usd'
                })
                df['data_type'] = 'snapshot'
                combined_data.append(df)
        
        if combined_data:
            final_df = pd.concat(combined_data, ignore_index=True, sort=False)
            output_path = os.path.join(self.data_dir, output_file)
            final_df.to_csv(output_path, index=False)
            self.logger.info(f"Combined data exported to: {output_path}")
            return output_path
        else:
            self.logger.warning("No data available to export")
            return None


def main():
    """Main function for data utilities"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cryptocurrency Data Utilities")
    parser.add_argument("--action", choices=["backup", "restore", "summary", "export"], 
                       required=True, help="Action to perform")
    parser.add_argument("--backup-path", help="Path for backup/restore operations")
    parser.add_argument("--output", help="Output file for export operations")
    
    args = parser.parse_args()
    
    utils = CryptoDataUtils()
    
    if args.action == "backup":
        backup_path = utils.backup_data(args.backup_path)
        print(f"Backup created at: {backup_path}")
    
    elif args.action == "restore":
        if not args.backup_path:
            print("Error: --backup-path required for restore operation")
            return
        utils.restore_data(args.backup_path)
        print(f"Data restored from: {args.backup_path}")
    
    elif args.action == "summary":
        report = utils.generate_summary_report()
        print(json.dumps(report, indent=2))
    
    elif args.action == "export":
        output_file = args.output or "combined_crypto_data.csv"
        export_path = utils.export_combined_data(output_file)
        if export_path:
            print(f"Data exported to: {export_path}")


if __name__ == "__main__":
    main()