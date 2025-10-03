"""
Chart Service for Flask Crypto Dashboard
Handles chart data preparation and formatting
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from services.data_service import CryptoDataService

class ChartService:
    """Service for preparing chart data"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the chart service"""
        self.config_path = config_path
        self.data_service = CryptoDataService(config_path)
        self.logger = logging.getLogger(__name__)
    
    def get_historical_data(self, symbol: str, period: str = '30d') -> Dict[str, Any]:
        """Get historical data formatted for charts"""
        try:
            # Find the ticker for this symbol
            ticker_info = self.data_service.get_ticker_info(symbol)
            if not ticker_info:
                return {'error': f'Symbol {symbol} not found'}
            
            ticker = ticker_info['ticker']
            
            # Get price data
            price_data = self.data_service.get_price_data(ticker, period)
            if not price_data:
                return {'error': f'No data available for {symbol}'}
            
            # Add metadata
            price_data['symbol'] = symbol
            price_data['name'] = ticker_info['name']
            price_data['period'] = period
            
            return price_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_chart_data(self, symbol: str, chart_type: str = 'line', period: str = '30d') -> Dict[str, Any]:
        """Get data formatted for specific chart types"""
        try:
            # Get base historical data
            data = self.get_historical_data(symbol, period)
            if 'error' in data:
                return data
            
            # Format based on chart type
            if chart_type == 'candlestick':
                return self._format_candlestick_data(data)
            elif chart_type == 'volume':
                return self._format_volume_data(data)
            elif chart_type == 'line':
                return self._format_line_data(data)
            else:
                return self._format_line_data(data)  # Default to line chart
                
        except Exception as e:
            self.logger.error(f"Error getting chart data for {symbol}: {e}")
            return {'error': str(e)}
    
    def _format_line_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for line charts"""
        return {
            'type': 'line',
            'symbol': data.get('symbol'),
            'name': data.get('name'),
            'period': data.get('period'),
            'data': [
                {
                    'x': date,
                    'y': price
                }
                for date, price in zip(data.get('dates', []), data.get('prices', []))
            ],
            'latest_price': data.get('latest_price'),
            'price_change': data.get('price_change'),
            'price_change_percent': data.get('price_change_percent'),
            'period_high': data.get('period_high'),
            'period_low': data.get('period_low')
        }
    
    def _format_candlestick_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for candlestick charts"""
        candlestick_data = []
        
        dates = data.get('dates', [])
        opens = data.get('opens', [])
        highs = data.get('highs', [])
        lows = data.get('lows', [])
        closes = data.get('prices', [])  # 'prices' contains closing prices
        
        for i in range(len(dates)):
            if i < len(opens) and i < len(highs) and i < len(lows) and i < len(closes):
                candlestick_data.append({
                    'x': dates[i],
                    'o': opens[i],  # open
                    'h': highs[i],  # high
                    'l': lows[i],   # low
                    'c': closes[i]  # close
                })
        
        return {
            'type': 'candlestick',
            'symbol': data.get('symbol'),
            'name': data.get('name'),
            'period': data.get('period'),
            'data': candlestick_data,
            'latest_price': data.get('latest_price'),
            'price_change': data.get('price_change'),
            'price_change_percent': data.get('price_change_percent'),
            'period_high': data.get('period_high'),
            'period_low': data.get('period_low')
        }
    
    def _format_volume_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for volume charts"""
        return {
            'type': 'volume',
            'symbol': data.get('symbol'),
            'name': data.get('name'),
            'period': data.get('period'),
            'data': [
                {
                    'x': date,
                    'y': volume
                }
                for date, volume in zip(data.get('dates', []), data.get('volumes', []))
            ],
            'period_volume': data.get('period_volume', 0)
        }
    
    def get_comparison_data(self, symbols: List[str], period: str = '30d') -> Dict[str, Any]:
        """Get data for comparing multiple cryptocurrencies"""
        try:
            comparison_data = {
                'period': period,
                'symbols': [],
                'datasets': []
            }
            
            for symbol in symbols:
                data = self.get_historical_data(symbol, period)
                if 'error' not in data:
                    comparison_data['symbols'].append({
                        'symbol': symbol,
                        'name': data.get('name'),
                        'latest_price': data.get('latest_price'),
                        'price_change_percent': data.get('price_change_percent')
                    })
                    
                    # Normalize prices to percentage change from first day
                    prices = data.get('prices', [])
                    if prices:
                        first_price = prices[0]
                        normalized_prices = [
                            ((price - first_price) / first_price) * 100
                            for price in prices
                        ]
                        
                        comparison_data['datasets'].append({
                            'symbol': symbol,
                            'name': data.get('name'),
                            'data': [
                                {'x': date, 'y': norm_price}
                                for date, norm_price in zip(data.get('dates', []), normalized_prices)
                            ]
                        })
            
            return comparison_data
            
        except Exception as e:
            self.logger.error(f"Error getting comparison data: {e}")
            return {'error': str(e)}
    
    def get_chart_config(self, chart_type: str = 'line') -> Dict[str, Any]:
        """Get Chart.js configuration for different chart types"""
        base_config = {
            'responsive': True,
            'maintainAspectRatio': False,
            'interaction': {
                'intersect': False,
                'mode': 'index'
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'enabled': True,
                    'mode': 'index',
                    'intersect': False
                }
            },
            'scales': {
                'x': {
                    'type': 'time',
                    'time': {
                        'displayFormats': {
                            'day': 'MMM DD',
                            'week': 'MMM DD',
                            'month': 'MMM YYYY'
                        }
                    },
                    'title': {
                        'display': True,
                        'text': 'Date'
                    }
                },
                'y': {
                    'title': {
                        'display': True,
                        'text': 'Price (USD)'
                    }
                }
            }
        }
        
        if chart_type == 'candlestick':
            base_config['scales']['y']['title']['text'] = 'Price (USD)'
        elif chart_type == 'volume':
            base_config['scales']['y']['title']['text'] = 'Volume'
        
        return base_config