"""
Cryptocurrency Performance Report Generator
Analyzes short-term price performance of top 10 cryptocurrencies by market cap
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from market_cap.market_cap_report import MarketCapReportGenerator


class CryptoPerformanceAnalyzer:
    """Analyze short-term performance of top cryptocurrencies"""
    
    def __init__(self, config_path: str = "../config/settings.json"):
        """Initialize the performance analyzer"""
        self.config = self._load_config(config_path)
        self.market_cap_generator = MarketCapReportGenerator(config_path)
        
        # Performance analysis periods (in days)
        self.analysis_periods = {
            '1d': 1,
            '3d': 3,
            '7d': 7,
            '14d': 14,
            '30d': 30
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "data": {
                    "historical_directory": "../crypto_data/historical",
                    "snapshots_directory": "../crypto_data/daily_snapshots"
                }
            }
    
    def check_data_freshness(self) -> Tuple[bool, str]:
        """Check if the cryptocurrency data is up-to-date"""
        # Load latest snapshot
        df = self.market_cap_generator.load_latest_snapshot()
        if df is None:
            return False, "No snapshot data available"
        
        # Get the date from the snapshot
        snapshot_date_str = df.iloc[0]['date']
        try:
            snapshot_date = datetime.strptime(snapshot_date_str, '%Y-%m-%d').date()
        except ValueError:
            return False, f"Invalid date format in snapshot: {snapshot_date_str}"
        
        # Check if data is from today or yesterday (allowing for timezone differences)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if snapshot_date >= yesterday:
            days_old = (today - snapshot_date).days
            return True, f"Data is {days_old} day(s) old"
        else:
            days_old = (today - snapshot_date).days
            return False, f"Data is {days_old} days old (too outdated)"
    
    def check_historical_data_availability(self, tickers: List[str]) -> Tuple[bool, str]:
        """Check if sufficient historical data is available for analysis"""
        missing_data = []
        insufficient_data = []
        
        for ticker in tickers:
            df = self.load_historical_data(ticker)
            if df is None:
                missing_data.append(ticker)
            elif len(df) < 31:  # Need at least 31 days for 30-day analysis
                insufficient_data.append(f"{ticker} ({len(df)} days)")
        
        if missing_data:
            return False, f"Missing historical data for: {', '.join(missing_data)}"
        
        if insufficient_data:
            return False, f"Insufficient historical data for: {', '.join(insufficient_data)}"
        
        return True, f"Historical data available for all {len(tickers)} cryptocurrencies"
    
    def get_top_10_by_market_cap(self) -> List[Dict]:
        """Get top 10 cryptocurrencies by market cap"""
        # Load latest snapshot
        df = self.market_cap_generator.load_latest_snapshot()
        if df is None:
            return []
        
        # Calculate market caps and get top 10
        market_cap_df = self.market_cap_generator.calculate_market_caps(df)
        top_10 = market_cap_df.head(10)
        
        return top_10.to_dict('records')
    
    def load_historical_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load historical data for a specific ticker"""
        historical_dir = self.config["data"]["historical_directory"]
        clean_ticker = ticker.replace(':', '_').replace('/', '_')
        filename = f"{clean_ticker}_historical.csv"
        filepath = os.path.join(historical_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  Historical data not found for {ticker}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
        except Exception as e:
            print(f"❌ Error loading historical data for {ticker}: {e}")
            return None
    
    def calculate_price_change(self, df: pd.DataFrame, days: int) -> Dict:
        """Calculate price change over specified number of days"""
        if len(df) < days + 1:
            return {
                'change_percent': 0,
                'change_absolute': 0,
                'start_price': 0,
                'end_price': 0,
                'volatility': 0,
                'trend_strength': 0
            }
        
        # Get prices for the period
        end_price = df.iloc[-1]['close']
        start_price = df.iloc[-(days + 1)]['close']
        
        # Calculate basic metrics
        change_absolute = end_price - start_price
        change_percent = (change_absolute / start_price) * 100 if start_price > 0 else 0
        
        # Calculate volatility (standard deviation of daily returns)
        period_data = df.tail(days + 1)
        daily_returns = period_data['close'].pct_change().dropna()
        volatility = daily_returns.std() * 100 if len(daily_returns) > 1 else 0
        
        # Calculate trend strength (correlation with time)
        if len(period_data) > 2:
            time_index = range(len(period_data))
            correlation = np.corrcoef(time_index, period_data['close'])[0, 1]
            trend_strength = abs(correlation) * 100 if not np.isnan(correlation) else 0
        else:
            trend_strength = 0
        
        return {
            'change_percent': change_percent,
            'change_absolute': change_absolute,
            'start_price': start_price,
            'end_price': end_price,
            'volatility': volatility,
            'trend_strength': trend_strength
        }
    
    def calculate_momentum_score(self, performance_data: Dict) -> float:
        """Calculate a momentum score based on multiple factors"""
        # Weights for different factors
        weights = {
            'short_term': 0.4,  # 1-3 day performance
            'medium_term': 0.3,  # 7-14 day performance
            'trend_strength': 0.2,  # How consistent the trend is
            'volatility_penalty': 0.1  # Penalty for high volatility
        }
        
        # Short-term momentum (1d and 3d average)
        short_term = (performance_data.get('1d', {}).get('change_percent', 0) + 
                     performance_data.get('3d', {}).get('change_percent', 0)) / 2
        
        # Medium-term momentum (7d and 14d average)
        medium_term = (performance_data.get('7d', {}).get('change_percent', 0) + 
                      performance_data.get('14d', {}).get('change_percent', 0)) / 2
        
        # Trend strength (average across periods)
        trend_strengths = [performance_data.get(period, {}).get('trend_strength', 0) 
                          for period in ['3d', '7d', '14d']]
        avg_trend_strength = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0
        
        # Volatility penalty (higher volatility reduces score)
        volatilities = [performance_data.get(period, {}).get('volatility', 0) 
                       for period in ['7d', '14d']]
        avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0
        volatility_penalty = min(avg_volatility, 50)  # Cap at 50%
        
        # Calculate weighted score
        momentum_score = (
            short_term * weights['short_term'] +
            medium_term * weights['medium_term'] +
            avg_trend_strength * weights['trend_strength'] -
            volatility_penalty * weights['volatility_penalty']
        )
        
        return momentum_score
    
    def analyze_crypto_performance(self, crypto_data: Dict) -> Dict:
        """Analyze performance for a single cryptocurrency"""
        ticker = crypto_data['ticker']
        symbol = crypto_data['symbol']
        name = crypto_data['name']
        
        print(f"📊 Analyzing {symbol} ({name})...")
        
        # Load historical data
        df = self.load_historical_data(ticker)
        if df is None:
            return {
                'ticker': ticker,
                'symbol': symbol,
                'name': name,
                'current_price': crypto_data['current_price'],
                'market_cap': crypto_data['market_cap_usd'],
                'performance': {},
                'momentum_score': 0,
                'error': 'No historical data available'
            }
        
        # Calculate performance for each period
        performance = {}
        for period_name, days in self.analysis_periods.items():
            performance[period_name] = self.calculate_price_change(df, days)
        
        # Calculate momentum score
        momentum_score = self.calculate_momentum_score(performance)
        
        return {
            'ticker': ticker,
            'symbol': symbol,
            'name': name,
            'current_price': crypto_data['current_price'],
            'market_cap': crypto_data['market_cap_usd'],
            'performance': performance,
            'momentum_score': momentum_score,
            'rank_by_market_cap': crypto_data['rank']
        }
    
    def format_percentage(self, value: float) -> str:
        """Format percentage with color indicators"""
        if value > 0:
            return f"+{value:.2f}%"
        else:
            return f"{value:.2f}%"
    
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
    
    def generate_performance_report(self, analysis_results: List[Dict]) -> str:
        """Generate a formatted performance report"""
        # Sort by momentum score (highest first)
        sorted_results = sorted(analysis_results, key=lambda x: x['momentum_score'], reverse=True)
        
        report = []
        report.append("=" * 140)
        report.append("🚀 CRYPTOCURRENCY SHORT-TERM PERFORMANCE REPORT")
        report.append("=" * 140)
        report.append(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 Cryptocurrencies Analyzed: {len(analysis_results)}")
        report.append(f"⏱️  Analysis Periods: 1d, 3d, 7d, 14d, 30d")
        report.append("")
        
        # Performance ranking header
        header = f"{'Rank':<4} {'Symbol':<8} {'Name':<20} {'Price':<12} {'1d':<8} {'3d':<8} {'7d':<8} {'14d':<8} {'30d':<8} {'Momentum':<10} {'Trend':<8}"
        report.append(header)
        report.append("-" * 140)
        
        # Top performers
        for i, result in enumerate(sorted_results, 1):
            if 'error' in result:
                continue
                
            symbol = result['symbol']
            name = result['name'][:18] + "..." if len(result['name']) > 18 else result['name']
            price = f"${result['current_price']:,.2f}"
            
            perf = result['performance']
            change_1d = self.format_percentage(perf.get('1d', {}).get('change_percent', 0))
            change_3d = self.format_percentage(perf.get('3d', {}).get('change_percent', 0))
            change_7d = self.format_percentage(perf.get('7d', {}).get('change_percent', 0))
            change_14d = self.format_percentage(perf.get('14d', {}).get('change_percent', 0))
            change_30d = self.format_percentage(perf.get('30d', {}).get('change_percent', 0))
            
            momentum = f"{result['momentum_score']:.1f}"
            
            # Calculate average trend strength
            trend_strengths = [perf.get(period, {}).get('trend_strength', 0) for period in ['3d', '7d', '14d']]
            avg_trend = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0
            trend = f"{avg_trend:.1f}%"
            
            line = f"#{i:<3} {symbol:<8} {name:<20} {price:<12} {change_1d:<8} {change_3d:<8} {change_7d:<8} {change_14d:<8} {change_30d:<8} {momentum:<10} {trend:<8}"
            report.append(line)
        
        report.append("")
        report.append("=" * 140)
        
        # Top 3 fastest growing
        report.append("🏆 TOP 3 FASTEST GROWING (Short-term):")
        for i in range(min(3, len(sorted_results))):
            result = sorted_results[i]
            if 'error' not in result:
                short_term_avg = (result['performance'].get('1d', {}).get('change_percent', 0) + 
                                result['performance'].get('3d', {}).get('change_percent', 0)) / 2
                report.append(f"  {i+1}. {result['symbol']} ({result['name']}) - {self.format_percentage(short_term_avg)} avg (1-3d)")
        
        report.append("")
        report.append("📈 PERFORMANCE INSIGHTS:")
        
        # Calculate insights
        positive_performers = [r for r in sorted_results if 'error' not in r and 
                             r['performance'].get('7d', {}).get('change_percent', 0) > 0]
        negative_performers = [r for r in sorted_results if 'error' not in r and 
                             r['performance'].get('7d', {}).get('change_percent', 0) < 0]
        
        report.append(f"  • Positive 7-day performers: {len(positive_performers)}/{len(sorted_results)}")
        report.append(f"  • Negative 7-day performers: {len(negative_performers)}/{len(sorted_results)}")
        
        if sorted_results and 'error' not in sorted_results[0]:
            best_performer = sorted_results[0]
            best_7d = best_performer['performance'].get('7d', {}).get('change_percent', 0)
            report.append(f"  • Best 7-day performer: {best_performer['symbol']} ({self.format_percentage(best_7d)})")
        
        if len(sorted_results) > 1 and 'error' not in sorted_results[-1]:
            worst_performer = sorted_results[-1]
            worst_7d = worst_performer['performance'].get('7d', {}).get('change_percent', 0)
            report.append(f"  • Worst 7-day performer: {worst_performer['symbol']} ({self.format_percentage(worst_7d)})")
        
        # Volatility analysis
        volatilities = []
        for result in sorted_results:
            if 'error' not in result:
                vol_7d = result['performance'].get('7d', {}).get('volatility', 0)
                if vol_7d > 0:
                    volatilities.append((result['symbol'], vol_7d))
        
        if volatilities:
            volatilities.sort(key=lambda x: x[1], reverse=True)
            most_volatile = volatilities[0]
            least_volatile = volatilities[-1]
            report.append(f"  • Most volatile (7d): {most_volatile[0]} ({most_volatile[1]:.1f}% daily volatility)")
            report.append(f"  • Least volatile (7d): {least_volatile[0]} ({least_volatile[1]:.1f}% daily volatility)")
        
        report.append("")
        report.append("💡 Momentum Score: Weighted combination of short-term gains, trend strength, and volatility")
        report.append("📊 Trend Strength: Measures consistency of price direction (0-100%)")
        report.append("⚡ Higher momentum scores indicate stronger short-term growth potential")
        report.append("=" * 140)
        
        return "\n".join(report)
    
    def save_performance_csv(self, analysis_results: List[Dict], filename: str = None) -> str:
        """Save performance analysis to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.csv"
        
        # Prepare data for CSV
        csv_data = []
        for result in analysis_results:
            if 'error' in result:
                continue
                
            row = {
                'symbol': result['symbol'],
                'name': result['name'],
                'ticker': result['ticker'],
                'current_price': result['current_price'],
                'market_cap': result['market_cap'],
                'market_cap_rank': result['rank_by_market_cap'],
                'momentum_score': result['momentum_score']
            }
            
            # Add performance data for each period
            for period in self.analysis_periods.keys():
                perf = result['performance'].get(period, {})
                row[f'{period}_change_percent'] = perf.get('change_percent', 0)
                row[f'{period}_volatility'] = perf.get('volatility', 0)
                row[f'{period}_trend_strength'] = perf.get('trend_strength', 0)
            
            csv_data.append(row)
        
        # Sort by momentum score
        csv_data.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        # Save to CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        return filename
    
    def generate_full_performance_report(self):
        """Generate complete performance analysis report"""
        print("🚀 Generating Cryptocurrency Performance Report...")
        print("=" * 60)
        
        # Check data freshness first
        print("🔍 Checking data freshness...")
        is_fresh, freshness_msg = self.check_data_freshness()
        print(f"📅 {freshness_msg}")
        
        if not is_fresh:
            print("❌ Cannot generate report: Data is too outdated for reliable performance analysis")
            print("💡 Please run 'python crypto_collector.py' to collect fresh data")
            print("⚠️  Performance analysis requires recent data (within 1-2 days)")
            return
        
        # Get top 10 cryptocurrencies by market cap
        print("📊 Loading top 10 cryptocurrencies by market cap...")
        top_10_cryptos = self.get_top_10_by_market_cap()
        
        if not top_10_cryptos:
            print("❌ Cannot generate report: No market cap data available")
            print("💡 Run 'python crypto_collector.py' or 'python market_cap_report.py' first")
            return
        
        print(f"✅ Found {len(top_10_cryptos)} cryptocurrencies to analyze")
        
        # Check historical data availability
        print("📈 Checking historical data availability...")
        tickers = [crypto['ticker'] for crypto in top_10_cryptos]
        has_sufficient_data, data_msg = self.check_historical_data_availability(tickers)
        print(f"📊 {data_msg}")
        
        if not has_sufficient_data:
            print("❌ Cannot generate report: Insufficient historical data for performance analysis")
            print("💡 Please run 'python crypto_collector.py' to collect historical data")
            print("⚠️  Performance analysis requires at least 31 days of historical data")
            return
        
        # Analyze performance for each cryptocurrency
        print("\n📈 Analyzing short-term performance...")
        analysis_results = []
        
        for crypto in top_10_cryptos:
            result = self.analyze_crypto_performance(crypto)
            analysis_results.append(result)
        
        # Generate and display report
        print("\n" + "=" * 60)
        performance_report = self.generate_performance_report(analysis_results)
        print(performance_report)
        
        # Save CSV report
        csv_filename = self.save_performance_csv(analysis_results)
        print(f"\n💾 Performance data saved: {csv_filename}")
        
        # Summary
        valid_results = [r for r in analysis_results if 'error' not in r]
        if valid_results:
            best_performer = max(valid_results, key=lambda x: x['momentum_score'])
            print(f"\n🏆 Best short-term performer: {best_performer['symbol']} ({best_performer['name']})")
            print(f"💫 Momentum Score: {best_performer['momentum_score']:.1f}")
            
            # Show recent performance
            recent_7d = best_performer['performance'].get('7d', {}).get('change_percent', 0)
            recent_3d = best_performer['performance'].get('3d', {}).get('change_percent', 0)
            recent_1d = best_performer['performance'].get('1d', {}).get('change_percent', 0)
            
            print(f"📈 Recent performance: 1d: {recent_1d:+.2f}%, 3d: {recent_3d:+.2f}%, 7d: {recent_7d:+.2f}%")
        
        print("\n✅ Performance analysis completed!")


def main():
    """Main function to generate performance report"""
    try:
        analyzer = CryptoPerformanceAnalyzer()
        analyzer.generate_full_performance_report()
    except Exception as e:
        print(f"❌ Error generating performance report: {e}")
        raise


if __name__ == "__main__":
    main()