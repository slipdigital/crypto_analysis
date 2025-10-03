"""
Market Service for Flask Crypto Dashboard
Handles market analysis and summary data
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from services.data_service import CryptoDataService

class MarketService:
    """Service for market analysis and summary data"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the market service"""
        self.config_path = config_path
        self.data_service = CryptoDataService(config_path)
        self.logger = logging.getLogger(__name__)
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get overall market summary statistics"""
        try:
            market_cap_data = self.data_service.get_market_cap_data()
            if not market_cap_data:
                return {
                    'total_market_cap': 0,
                    'total_cryptocurrencies': 0,
                    'bitcoin_dominance': 0,
                    'top_10_share': 0,
                    'last_updated': None,
                    'error': 'No market data available'
                }
            
            # Calculate summary statistics
            total_market_cap = sum(crypto['market_cap_usd'] for crypto in market_cap_data)
            total_cryptocurrencies = len(market_cap_data)
            
            # Bitcoin dominance
            bitcoin_dominance = 0
            if market_cap_data and market_cap_data[0]['symbol'] == 'BTC':
                bitcoin_dominance = (market_cap_data[0]['market_cap_usd'] / total_market_cap) * 100
            
            # Top 10 market cap share
            top_10_cap = sum(crypto['market_cap_usd'] for crypto in market_cap_data[:10])
            top_10_share = (top_10_cap / total_market_cap) * 100 if total_market_cap > 0 else 0
            
            # Find highest priced cryptocurrency
            highest_price_crypto = max(market_cap_data, key=lambda x: x['current_price'])
            
            return {
                'total_market_cap': total_market_cap,
                'total_market_cap_formatted': self._format_currency(total_market_cap),
                'total_cryptocurrencies': total_cryptocurrencies,
                'bitcoin_dominance': round(bitcoin_dominance, 1),
                'top_10_share': round(top_10_share, 1),
                'highest_price_crypto': {
                    'symbol': highest_price_crypto['symbol'],
                    'name': highest_price_crypto['name'],
                    'price': highest_price_crypto['current_price'],
                    'price_formatted': f"${highest_price_crypto['current_price']:,.2f}"
                },
                'last_updated': self.data_service.get_last_update_time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return {
                'total_market_cap': 0,
                'total_cryptocurrencies': 0,
                'bitcoin_dominance': 0,
                'top_10_share': 0,
                'last_updated': None,
                'error': str(e)
            }
    
    def get_market_cap_data(self) -> List[Dict[str, Any]]:
        """Get formatted market cap data for tables"""
        try:
            market_cap_data = self.data_service.get_market_cap_data()
            
            # Add formatted fields for display
            for crypto in market_cap_data:
                crypto['price_formatted'] = f"${crypto['current_price']:,.2f}"
                crypto['market_cap_formatted'] = self._format_currency(crypto['market_cap_usd'])
                crypto['supply_formatted'] = self._format_number(crypto['circulating_supply_millions'] * 1_000_000)
                crypto['volume_formatted'] = self._format_currency(crypto.get('volume_24h', 0))
                
                # Add price change indicators (placeholder for now)
                crypto['price_change_24h'] = 0  # Would need historical data
                crypto['price_change_24h_formatted'] = "0.00%"
                crypto['price_change_class'] = 'neutral'
            
            return market_cap_data
            
        except Exception as e:
            self.logger.error(f"Error getting market cap data: {e}")
            return []
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing cryptocurrencies"""
        try:
            performance_data = self.data_service.get_performance_data()
            
            # Format performance data for display
            formatted_performers = []
            for crypto in performance_data[:limit]:
                # Get 7-day performance as main metric
                perf_7d = crypto.get('performance', {}).get('7d', {})
                change_7d = perf_7d.get('change_percent', 0)
                
                formatted_performers.append({
                    'rank': len(formatted_performers) + 1,
                    'symbol': crypto['symbol'],
                    'name': crypto['name'],
                    'current_price': crypto['current_price'],
                    'price_formatted': f"${crypto['current_price']:,.2f}",
                    'market_cap': crypto['market_cap'],
                    'market_cap_formatted': self._format_currency(crypto['market_cap']),
                    'momentum_score': round(crypto['momentum_score'], 1),
                    'change_7d': round(change_7d, 2),
                    'change_7d_formatted': f"{change_7d:+.2f}%",
                    'change_7d_class': 'positive' if change_7d > 0 else 'negative' if change_7d < 0 else 'neutral'
                })
            
            return formatted_performers
            
        except Exception as e:
            self.logger.error(f"Error getting top performers: {e}")
            return []
    
    def get_performance_data(self) -> List[Dict[str, Any]]:
        """Get detailed performance analysis data"""
        try:
            performance_data = self.data_service.get_performance_data()
            
            # Format for display
            formatted_data = []
            for crypto in performance_data:
                perf = crypto.get('performance', {})
                
                # Format all time periods
                periods = ['1d', '3d', '7d', '14d', '30d']
                period_data = {}
                
                for period in periods:
                    period_perf = perf.get(period, {})
                    change_percent = period_perf.get('change_percent', 0)
                    period_data[f'{period}_change'] = round(change_percent, 2)
                    period_data[f'{period}_change_formatted'] = f"{change_percent:+.2f}%"
                    period_data[f'{period}_change_class'] = 'positive' if change_percent > 0 else 'negative' if change_percent < 0 else 'neutral'
                    period_data[f'{period}_volatility'] = round(period_perf.get('volatility', 0), 2)
                    period_data[f'{period}_trend_strength'] = round(period_perf.get('trend_strength', 0), 1)
                
                formatted_crypto = {
                    'symbol': crypto['symbol'],
                    'name': crypto['name'],
                    'current_price': crypto['current_price'],
                    'price_formatted': f"${crypto['current_price']:,.2f}",
                    'market_cap': crypto['market_cap'],
                    'market_cap_formatted': self._format_currency(crypto['market_cap']),
                    'market_cap_rank': crypto.get('rank_by_market_cap', 0),
                    'momentum_score': round(crypto['momentum_score'], 1),
                    **period_data
                }
                
                formatted_data.append(formatted_crypto)
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Error getting performance data: {e}")
            return []
    
    def get_market_insights(self) -> Dict[str, Any]:
        """Get market insights and analysis"""
        try:
            market_cap_data = self.data_service.get_market_cap_data()
            performance_data = self.data_service.get_performance_data()
            
            if not market_cap_data or not performance_data:
                return {'error': 'Insufficient data for insights'}
            
            # Calculate insights
            total_market_cap = sum(crypto['market_cap_usd'] for crypto in market_cap_data)
            
            # Performance insights
            positive_performers = [p for p in performance_data if p.get('performance', {}).get('7d', {}).get('change_percent', 0) > 0]
            negative_performers = [p for p in performance_data if p.get('performance', {}).get('7d', {}).get('change_percent', 0) < 0]
            
            # Best and worst performers
            best_performer = max(performance_data, key=lambda x: x.get('performance', {}).get('7d', {}).get('change_percent', -999))
            worst_performer = min(performance_data, key=lambda x: x.get('performance', {}).get('7d', {}).get('change_percent', 999))
            
            # Volatility analysis
            volatilities = []
            for crypto in performance_data:
                vol_7d = crypto.get('performance', {}).get('7d', {}).get('volatility', 0)
                if vol_7d > 0:
                    volatilities.append((crypto['symbol'], vol_7d))
            
            volatilities.sort(key=lambda x: x[1], reverse=True)
            most_volatile = volatilities[0] if volatilities else None
            least_volatile = volatilities[-1] if volatilities else None
            
            return {
                'total_market_cap': total_market_cap,
                'total_market_cap_formatted': self._format_currency(total_market_cap),
                'positive_performers_count': len(positive_performers),
                'negative_performers_count': len(negative_performers),
                'total_analyzed': len(performance_data),
                'best_performer': {
                    'symbol': best_performer['symbol'],
                    'name': best_performer['name'],
                    'change_7d': round(best_performer.get('performance', {}).get('7d', {}).get('change_percent', 0), 2)
                },
                'worst_performer': {
                    'symbol': worst_performer['symbol'],
                    'name': worst_performer['name'],
                    'change_7d': round(worst_performer.get('performance', {}).get('7d', {}).get('change_percent', 0), 2)
                },
                'most_volatile': {
                    'symbol': most_volatile[0],
                    'volatility': round(most_volatile[1], 1)
                } if most_volatile else None,
                'least_volatile': {
                    'symbol': least_volatile[0],
                    'volatility': round(least_volatile[1], 1)
                } if least_volatile else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market insights: {e}")
            return {'error': str(e)}
    
    def _format_currency(self, amount: float) -> str:
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
    
    def _format_number(self, number: float) -> str:
        """Format large numbers with appropriate suffixes"""
        if number >= 1_000_000_000:  # Billions
            return f"{number/1_000_000_000:.2f}B"
        elif number >= 1_000_000:  # Millions
            return f"{number/1_000_000:.2f}M"
        elif number >= 1_000:  # Thousands
            return f"{number/1_000:.2f}K"
        else:
            return f"{number:.2f}"