"""
Django management command to fetch market cap data from CoinGecko API.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from datetime import datetime
import requests
import time
from main.models import Ticker


class Command(BaseCommand):
    help = 'Update market cap data for tickers from CoinGecko API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=250,
            help='Number of top cryptocurrencies to fetch (default: 250)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay between requests in seconds (default: 1.0)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        delay = options['delay']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be made'))
        
        self.stdout.write(f'Fetching top {limit} cryptocurrencies from CoinGecko API...')
        
        # Fetch market cap data from CoinGecko API
        crypto_data = self.fetch_coingecko_api(limit, delay)
        
        if not crypto_data:
            self.stdout.write(self.style.ERROR('No data fetched from CoinGecko'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Fetched {len(crypto_data)} cryptocurrencies'))
        
        # Update matching tickers
        updated_count = self.update_tickers(crypto_data, dry_run)
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'DRY RUN: Would have updated {updated_count} tickers'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} tickers'))

    def fetch_coingecko_api(self, limit, delay):
        """
        Fetch cryptocurrency market cap data from CoinGecko API.
        
        Uses the public API endpoint which doesn't require authentication.
        Returns a list of dictionaries with crypto data.
        """
        crypto_data = []
        base_url = "https://api.coingecko.com/api/v3/coins/markets"
        
        # CoinGecko API allows up to 250 results per page
        per_page = min(250, limit)
        pages_needed = (limit // per_page) + (1 if limit % per_page > 0 else 0)
        
        for page in range(1, pages_needed + 1):
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': per_page,
                'page': page,
                'sparkline': 'false',
                'locale': 'en'
            }
            
            self.stdout.write(f'Fetching page {page}/{pages_needed}...')
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for coin in data:
                    crypto_data.append({
                        'id': coin.get('id'),
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name'),
                        'market_cap': coin.get('market_cap'),
                        'current_price': coin.get('current_price'),
                        'total_volume': coin.get('total_volume'),
                        'market_cap_rank': coin.get('market_cap_rank')
                    })
                    
                    if len(crypto_data) >= limit:
                        break
                
                if len(crypto_data) >= limit:
                    break
                
                # Be respectful with rate limits
                if page < pages_needed:
                    time.sleep(delay)
            
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Error fetching page {page}: {e}'))
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    self.stdout.write(self.style.WARNING('Rate limit exceeded. Try increasing --delay parameter.'))
                break
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Error parsing JSON response: {e}'))
                break
        
        return crypto_data

    def update_tickers(self, crypto_data, dry_run=False):
        """
        Update tickers in the database with market cap data.
        
        Matches cryptocurrencies by symbol and updates their market_cap field.
        """
        updated_count = 0
        skipped_count = 0
        
        for crypto in crypto_data:
            symbol = crypto['symbol']
            market_cap = crypto['market_cap']
            name = crypto.get('name')
            
            # Skip if market cap is None
            if market_cap is None:
                continue
            
            # Try to find matching tickers using more precise matching
            # Priority: exact crypto_symbol match > ticker pattern match > currency symbol match
            matching_tickers = []
            
            # First, try exact crypto_symbol match
            exact_matches = Ticker.objects.filter(crypto_symbol__iexact=symbol)
            if exact_matches.exists():
                matching_tickers = list(exact_matches)
            else:
                # Try ticker pattern matches (more precise than icontains)
                # Match X:BTCUSD pattern or similar with word boundaries
                ticker_patterns = [
                    f'X:{symbol}USD',  # e.g., X:BTCUSD
                    f'X:{symbol}EUR',  # e.g., X:BTCEUR
                    f'X:{symbol}GBP',  # e.g., X:BTCGBP
                    f'X:{symbol}JPY',  # e.g., X:BTCJPY
                    f'X:{symbol}AUD',  # e.g., X:BTCAUD
                ]
                
                for pattern in ticker_patterns:
                    matches = Ticker.objects.filter(ticker__iexact=pattern)
                    matching_tickers.extend(matches)
                
                # If no pattern matches, try currency_symbol (but only for exact matches)
                if not matching_tickers:
                    currency_matches = Ticker.objects.filter(
                        Q(currency_symbol__iexact=symbol) |
                        Q(base_currency_symbol__iexact=symbol)
                    )
                    # Filter out tickers that have a different crypto_symbol set
                    for ticker in currency_matches:
                        if not ticker.crypto_symbol or ticker.crypto_symbol.upper() == symbol:
                            matching_tickers.append(ticker)
            
            if matching_tickers:
                for ticker in matching_tickers:
                    if dry_run:
                        self.stdout.write(
                            f'Would update {ticker.ticker}: {symbol} ({name}) -> '
                            f'${market_cap:,.0f} (current: ${ticker.market_cap or 0:,.0f})'
                        )
                    else:
                        old_market_cap = ticker.market_cap
                        ticker.market_cap = market_cap
                        ticker.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ticker.save()
                        
                        self.stdout.write(
                            f'Updated {ticker.ticker}: {symbol} ({name}) -> '
                            f'${market_cap:,.0f} (was: ${old_market_cap or 0:,.0f})'
                        )
                    
                    updated_count += 1
            else:
                skipped_count += 1
                if dry_run or skipped_count <= 10:  # Only show first 10 skipped to reduce noise
                    self.stdout.write(
                        self.style.WARNING(f'No matching ticker found for {symbol} ({name})')
                    )
        
        if skipped_count > 10:
            self.stdout.write(
                self.style.WARNING(f'...and {skipped_count - 10} more unmatched cryptocurrencies')
            )
        
        return updated_count

