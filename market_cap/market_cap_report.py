"""
Cryptocurrency Market Cap Report Generator
Creates reports listing cryptocurrencies ordered by market cap (highest first)
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
import time


class MarketCapReportGenerator:
    """Generate market cap reports for cryptocurrencies"""
    
    def __init__(self, config_path: str = "../config/settings.json"):
        """Initialize the report generator"""
        self.config = self._load_config(config_path)
        self.crypto_supply_data = None
        
        # Load supply data from crypto_tickers.csv
        self._load_supply_data()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Use default config if file not found
            return {
                "data": {
                    "snapshots_directory": "crypto_data/daily_snapshots",
                    "data_directory": "crypto_data"
                }
            }
    
    def _load_supply_data(self):
        """Load cryptocurrency supply data from crypto_tickers.csv"""
        try:
            # Try different possible paths for the CSV file
            possible_paths = [
                "crypto_data/crypto_tickers.csv",
                "../crypto_data/crypto_tickers.csv",
                os.path.join(self.config.get("data", {}).get("data_directory", "crypto_data"), "crypto_tickers.csv")
            ]
            
            ticker_df = None
            for path in possible_paths:
                if os.path.exists(path):
                    ticker_df = pd.read_csv(path)
                    print(f"✅ Loaded supply data from: {path}")
                    break
            
            if ticker_df is None:
                print("⚠️  Warning: crypto_tickers.csv not found. Using empty supply data.")
                print("💡 Run 'python update_tickers.py' to generate ticker data first.")
                self.crypto_supply_data = {}
                return
            
            # Build supply data dictionary from the CSV
            self.crypto_supply_data = {}
            
            for _, row in ticker_df.iterrows():
                ticker = row.get('ticker', '')
                crypto_symbol = row.get('crypto_symbol', '')
                name = row.get('name', '')
                
                # Calculate supply from market cap and price if available
                # Formula: supply = market_cap / price
                market_cap = row.get('market_cap')
                current_price = row.get('current_price')
                
                supply_millions = 0
                if pd.notna(market_cap) and pd.notna(current_price) and current_price > 0:
                    # Calculate supply in millions
                    supply_millions = market_cap / (current_price * 1_000_000)
                
                if ticker:
                    self.crypto_supply_data[ticker] = {
                        'supply': supply_millions,
                        'symbol': crypto_symbol if crypto_symbol else ticker.split(':')[-1].replace('USD', ''),
                        'name': name if name else ticker
                    }
            
            print(f"📊 Loaded supply data for {len(self.crypto_supply_data)} cryptocurrencies")
            
        except Exception as e:
            print(f"⚠️  Error loading supply data: {e}")
            print("💡 Using empty supply data. Run 'python update_tickers.py' to generate ticker data.")
            self.crypto_supply_data = {}
    
    def load_latest_snapshot(self) -> Optional[pd.DataFrame]:
        """Load the most recent daily snapshot"""
        snapshots_dir = self.config["data"]["snapshots_directory"]
        
        if not os.path.exists(snapshots_dir):
            print(f"❌ Snapshots directory not found: {snapshots_dir}")
            return None
        
        # Find the most recent snapshot file
        snapshot_files = [f for f in os.listdir(snapshots_dir) if f.endswith('_snapshot.csv')]
        
        if not snapshot_files:
            print(f"❌ No snapshot files found in {snapshots_dir}")
            return None
        
        # Sort by date and get the latest
        snapshot_files.sort(reverse=True)
        latest_file = snapshot_files[0]
        
        filepath = os.path.join(snapshots_dir, latest_file)
        
        try:
            df = pd.read_csv(filepath)
            print(f"✅ Loaded snapshot data from: {latest_file}")
            return df
        except Exception as e:
            print(f"❌ Error loading snapshot file: {e}")
            return None
    
    def calculate_market_caps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate market cap for each cryptocurrency"""
        market_cap_data = []
        
        for _, row in df.iterrows():
            ticker = row['ticker']
            price = row['current_price']
            
            # Get supply data from loaded CSV
            supply_info = self.crypto_supply_data.get(ticker, {})
            supply = supply_info.get('supply', 0)
            symbol = supply_info.get('symbol', ticker.split(':')[-1].replace('USD', ''))
            name = supply_info.get('name', row.get('ticker_name', ticker))
            
            # Calculate market cap (price × supply in millions)
            market_cap = price * supply * 1_000_000 if supply > 0 else 0
            
            # If market cap is 0, check if it's available directly in the row
            if market_cap == 0 and 'market_cap' in row and pd.notna(row['market_cap']):
                market_cap = row['market_cap']
                # Recalculate supply if we have market cap and price
                if price > 0:
                    supply = market_cap / (price * 1_000_000)
            
            market_cap_data.append({
                'rank': len(market_cap_data) + 1,
                'symbol': symbol,
                'name': name,
                'ticker': ticker,
                'current_price': price,
                'circulating_supply_millions': supply,
                'market_cap_usd': market_cap,
                'volume_24h': row.get('volume', 0),
                'price_change_24h': 0,  # Would need historical data for this
                'date': row['date']
            })
        
        # Create DataFrame and sort by market cap
        result_df = pd.DataFrame(market_cap_data)
        result_df = result_df.sort_values('market_cap_usd', ascending=False).reset_index(drop=True)
        
        # Update ranks
        result_df['rank'] = range(1, len(result_df) + 1)
        
        return result_df
    
    def format_currency(self, amount: float) -> str:
        """Format currency amounts with appropriate suffixes"""
        if amount >= 1_000_000_000_000:  # Trillions
            return f"${amount/1_000_000_000_000:.2f}T"
        elif amount >= 1_000_000_000:  # Billions
            return f"${amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:  # Millions
            return f"${amount/1_000_000:.2f}M"
        elif amount >= 1_000:  # Thousands
            return f"${amount/1_000:.2f}K"
        else:
            return f"${amount:.2f}"
    
    def format_number(self, number: float) -> str:
        """Format large numbers with appropriate suffixes"""
        if number >= 1_000_000_000:  # Billions
            return f"{number/1_000_000_000:.2f}B"
        elif number >= 1_000_000:  # Millions
            return f"{number/1_000_000:.2f}M"
        elif number >= 1_000:  # Thousands
            return f"{number/1_000:.2f}K"
        else:
            return f"{number:.2f}"
    
    def generate_console_report(self, df: pd.DataFrame) -> str:
        """Generate a formatted console report"""
        report = []
        report.append("=" * 120)
        report.append("🏆 CRYPTOCURRENCY MARKET CAP REPORT")
        report.append("=" * 120)
        report.append(f"📅 Report Date: {df.iloc[0]['date']}")
        report.append(f"📊 Total Cryptocurrencies: {len(df)}")
        
        total_market_cap = df['market_cap_usd'].sum()
        report.append(f"💰 Total Market Cap: {self.format_currency(total_market_cap)}")
        report.append("")
        
        # Header
        header = f"{'Rank':<4} {'Symbol':<8} {'Name':<25} {'Price':<12} {'Market Cap':<15} {'Supply':<12} {'Volume 24h':<15}"
        report.append(header)
        report.append("-" * 120)
        
        # Top cryptocurrencies
        for _, row in df.head(30).iterrows():
            rank = f"#{row['rank']}"
            symbol = row['symbol']
            name = row['name'][:23] + "..." if len(row['name']) > 23 else row['name']
            price = f"${row['current_price']:,.2f}"
            market_cap = self.format_currency(row['market_cap_usd'])
            supply = self.format_number(row['circulating_supply_millions'] * 1_000_000)
            volume = self.format_currency(row['volume_24h'])
            
            line = f"{rank:<4} {symbol:<8} {name:<25} {price:<12} {market_cap:<15} {supply:<12} {volume:<15}"
            report.append(line)
        
        report.append("")
        report.append("=" * 120)
        
        # Top 10 summary
        report.append("🥇 TOP 10 BY MARKET CAP:")
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            report.append(f"  {i+1}. {row['symbol']} ({row['name']}) - {self.format_currency(row['market_cap_usd'])}")
        
        report.append("")
        report.append("📈 MARKET INSIGHTS:")
        
        # Bitcoin dominance
        if len(df) > 0 and df.iloc[0]['symbol'] == 'BTC':
            btc_dominance = (df.iloc[0]['market_cap_usd'] / total_market_cap) * 100
            report.append(f"  • Bitcoin Dominance: {btc_dominance:.1f}%")
        
        # Top 10 market cap percentage
        top_10_cap = df.head(10)['market_cap_usd'].sum()
        top_10_percentage = (top_10_cap / total_market_cap) * 100
        report.append(f"  • Top 10 Market Cap Share: {top_10_percentage:.1f}%")
        
        # Highest priced coin
        highest_price_coin = df.loc[df['current_price'].idxmax()]
        report.append(f"  • Highest Price: {highest_price_coin['symbol']} at ${highest_price_coin['current_price']:,.2f}")
        
        report.append("")
        report.append("💡 Note: Market cap calculated as Price × Circulating Supply")
        report.append("📊 Data source: Polygon.io API via crypto_collector.py")
        report.append("=" * 120)
        
        return "\n".join(report)
    
    def save_csv_report(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save the market cap report as CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_cap_report_{timestamp}.csv"
        
        # Prepare data for CSV with formatted columns
        csv_data = df.copy()
        csv_data['market_cap_formatted'] = csv_data['market_cap_usd'].apply(self.format_currency)
        csv_data['price_formatted'] = csv_data['current_price'].apply(lambda x: f"${x:,.2f}")
        csv_data['supply_formatted'] = csv_data['circulating_supply_millions'].apply(lambda x: self.format_number(x * 1_000_000))
        csv_data['volume_formatted'] = csv_data['volume_24h'].apply(self.format_currency)
        
        # Reorder columns for better readability
        columns_order = [
            'rank', 'symbol', 'name', 'ticker', 'current_price', 'price_formatted',
            'market_cap_usd', 'market_cap_formatted', 'circulating_supply_millions',
            'supply_formatted', 'volume_24h', 'volume_formatted', 'date'
        ]
        
        csv_data = csv_data[columns_order]
        
        # Save to file
        csv_data.to_csv(filename, index=False)
        return filename
    
    def generate_html_report(self, df: pd.DataFrame, filename: str = None) -> str:
        """Generate an HTML report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_cap_report_{timestamp}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Cryptocurrency Market Cap Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary-item {{ display: inline-block; margin-right: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #34495e; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #e8f4f8; }}
        .rank {{ font-weight: bold; color: #e74c3c; }}
        .symbol {{ font-weight: bold; color: #3498db; }}
        .price {{ color: #27ae60; font-weight: bold; }}
        .market-cap {{ color: #8e44ad; font-weight: bold; }}
        .top-crypto {{ background-color: #fff3cd; }}
        .footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Cryptocurrency Market Cap Report</h1>
        
        <div class="summary">
            <div class="summary-item"><strong>📅 Report Date:</strong> {df.iloc[0]['date']}</div>
            <div class="summary-item"><strong>📊 Total Cryptocurrencies:</strong> {len(df)}</div>
            <div class="summary-item"><strong>💰 Total Market Cap:</strong> {self.format_currency(df['market_cap_usd'].sum())}</div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Price (USD)</th>
                    <th>Market Cap</th>
                    <th>Circulating Supply</th>
                    <th>Volume (24h)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in df.head(30).iterrows():
            top_class = "top-crypto" if row['rank'] <= 10 else ""
            html_content += f"""
                <tr class="{top_class}">
                    <td class="rank">#{row['rank']}</td>
                    <td class="symbol">{row['symbol']}</td>
                    <td>{row['name']}</td>
                    <td class="price">${row['current_price']:,.2f}</td>
                    <td class="market-cap">{self.format_currency(row['market_cap_usd'])}</td>
                    <td>{self.format_number(row['circulating_supply_millions'] * 1_000_000)}</td>
                    <td>{self.format_currency(row['volume_24h'])}</td>
                </tr>
            """
        
        html_content += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>💡 Market cap calculated as Price × Circulating Supply</p>
            <p>📊 Data source: Polygon.io API via crypto_collector.py</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        return filename
    
    def generate_full_report(self):
        """Generate complete market cap report in multiple formats"""
        print("🚀 Generating Cryptocurrency Market Cap Report...")
        print("=" * 60)
        
        # Check if supply data is loaded
        if not self.crypto_supply_data:
            print("⚠️  Warning: No supply data available")
            print("💡 Market cap calculations may be limited")
            print("💡 Run 'python update_tickers.py' to generate complete ticker data")
            print()
        
        # Load data
        df = self.load_latest_snapshot()
        if df is None:
            print("❌ Cannot generate report: No snapshot data available")
            print("💡 Run 'python crypto_collector.py' or 'python crypto_collector_demo.py' first")
            return
        
        # Calculate market caps
        print("📊 Calculating market capitalizations...")
        market_cap_df = self.calculate_market_caps(df)
        
        # Check how many have valid market caps
        valid_market_caps = (market_cap_df['market_cap_usd'] > 0).sum()
        print(f"✅ Calculated market cap for {valid_market_caps}/{len(market_cap_df)} cryptocurrencies")
        
        if valid_market_caps == 0:
            print("⚠️  Warning: No valid market cap data available")
            print("💡 Ensure crypto_tickers.csv has market_cap data")
        
        # Generate console report
        console_report = self.generate_console_report(market_cap_df)
        print(console_report)
        
        # Save CSV report
        csv_filename = self.save_csv_report(market_cap_df)
        print(f"\n💾 CSV report saved: {csv_filename}")
        
        # Generate HTML report
        html_filename = self.generate_html_report(market_cap_df)
        print(f"🌐 HTML report saved: {html_filename}")
        
        print(f"\n✅ Report generation completed!")
        
        if valid_market_caps > 0:
            top_crypto = market_cap_df.iloc[0]
            print(f"📈 Top cryptocurrency by market cap: {top_crypto['symbol']} ({top_crypto['name']})")
            print(f"💰 Market cap: {self.format_currency(top_crypto['market_cap_usd'])}")
        else:
            print("💡 No market cap rankings available - please update ticker data")


def main():
    """Main function to generate market cap report"""
    try:
        generator = MarketCapReportGenerator()
        generator.generate_full_report()
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        raise


if __name__ == "__main__":
    main()