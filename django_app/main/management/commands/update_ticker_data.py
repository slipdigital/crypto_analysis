"""
Django management command to collect historical daily price data for tickers from Polygon API.
Checks existing data and only fetches missing dates.

Usage:
    python manage.py update_ticker_data
    python manage.py update_ticker_data --ticker BTC-USD
    python manage.py update_ticker_data --limit 10
"""
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.conf import settings
from datetime import datetime, timedelta
import time
import requests
from main.models import Ticker, TickerData


class Command(BaseCommand):
    help = 'Update ticker historical price data from Polygon API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ticker',
            type=str,
            help='Process only a specific ticker'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of tickers to process'
        )

    def get_date_range_for_ticker(self, ticker_obj):
        """Get the date range that needs to be collected for a ticker."""
        # Get the latest date we have data for this ticker
        latest = TickerData.objects.filter(ticker=ticker_obj).aggregate(
            max_date=Max('date')
        )['max_date']
        
        # Get earliest available data date (2 years ago as a safe default for crypto)
        earliest_available = datetime.now() - timedelta(days=730)
        # Only update up to yesterday (today's data is incomplete during trading)
        yesterday = (datetime.now() - timedelta(days=1)).date()
        
        if latest:
            # We have some data, fetch from day after latest to yesterday
            start_date = latest + timedelta(days=1)
            if start_date > yesterday:
                return None, None  # Already up to date
            return start_date, yesterday
        else:
            # No data yet, fetch all available history up to yesterday
            return earliest_available.date(), yesterday

    def fetch_daily_data(self, ticker, from_date, to_date):
        """Fetch daily aggregates from Polygon API."""
        url = f"{settings.POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000,
            'apiKey': settings.POLYGON_API_KEY
        }
        
        try:
            resp = requests.get(url, params=params, timeout=settings.POLYGON_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                return data['results']
            return []
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error fetching data for {ticker}: {e}"))
            return []

    def save_ticker_data(self, ticker_obj, daily_data):
        """Save daily price data to database."""
        collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        saved_count = 0
        
        for bar in daily_data:
            # Convert timestamp (milliseconds) to date
            date = datetime.fromtimestamp(bar['t'] / 1000).date()
            
            # Use get_or_create to avoid duplicate key errors
            _, created = TickerData.objects.get_or_create(
                ticker=ticker_obj,
                date=date,
                defaults={
                    'open': bar.get('o'),
                    'high': bar.get('h'),
                    'low': bar.get('l'),
                    'close': bar.get('c'),
                    'volume': bar.get('v'),
                    'vwap': bar.get('vw'),
                    'transactions': bar.get('n'),
                    'collected_at': collected_at
                }
            )
            
            if created:
                saved_count += 1
        
        return saved_count

    def process_ticker(self, ticker_obj, rate_limit_delay):
        """Process a single ticker to collect its historical data."""
        ticker_symbol = ticker_obj.ticker
        
        # Check what date range we need
        from_date, to_date = self.get_date_range_for_ticker(ticker_obj)
        
        if not from_date or not to_date:
            self.stdout.write(f"✓ {ticker_symbol}: Already up to date")
            return 0
        
        self.stdout.write(f"→ {ticker_symbol}: Fetching data from {from_date} to {to_date}")
        
        # Fetch data from Polygon
        daily_data = self.fetch_daily_data(ticker_symbol, from_date, to_date)
        
        if not daily_data:
            # Check if ticker has no data for the last 7 days
            seven_days_ago = datetime.now().date() - timedelta(days=7)
            latest_data = TickerData.objects.filter(
                ticker=ticker_obj,
                date__gte=seven_days_ago
            ).exists()
            
            if not latest_data:
                # No data for last 7 days, mark as discontinued (inactive)
                ticker_obj.active = False
                ticker_obj.last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ticker_obj.save()
                self.stdout.write(self.style.WARNING(
                    f"  {ticker_symbol}: No data for 7+ days, marked as discontinued"
                ))
            else:
                self.stdout.write(f"  {ticker_symbol}: No new data available")
            return 0
        
        # Save to database
        saved_count = self.save_ticker_data(ticker_obj, daily_data)
        self.stdout.write(self.style.SUCCESS(f"  {ticker_symbol}: Saved {saved_count} records"))
        
        # Rate limiting for basic tier (5 requests per minute)
        time.sleep(rate_limit_delay)
        
        return saved_count

    def handle(self, *args, **options):
        # Get rate limit delay from settings
        rate_limit_delay = settings.POLYGON_RATE_LIMIT_DELAY
        
        # Get tickers to process
        query = Ticker.objects.filter(active=True)
        
        if options['ticker']:
            query = query.filter(ticker=options['ticker'])
        
        if options['limit']:
            query = query[:options['limit']]
        
        tickers = list(query)
        
        self.stdout.write(self.style.SUCCESS(f"\n=== Processing {len(tickers)} tickers ===\n"))
        
        total_saved = 0
        for i, ticker_obj in enumerate(tickers, 1):
            self.stdout.write(f"[{i}/{len(tickers)}] ", ending="")
            saved = self.process_ticker(ticker_obj, rate_limit_delay)
            total_saved += saved
        
        self.stdout.write(self.style.SUCCESS(f"\n=== Complete: Saved {total_saved} total records ===\n"))
