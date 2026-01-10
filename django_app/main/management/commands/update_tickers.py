"""
Django management command to update ticker list from Polygon API.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
import requests
from main.models import Ticker


class Command(BaseCommand):
    help = 'Update ticker list from Polygon API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all tickers regardless of last update time'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all ticker data from the database'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = self.clear_all_tickers()
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} tickers from the database.'))
        elif options['force']:
            tickers = self.fetch_polygon_tickers()
            self.save_tickers_to_db(tickers)
            self.stdout.write(self.style.SUCCESS('Updated all tickers (forced).'))
        else:
            if self.check_already_updated_today():
                self.stdout.write(self.style.WARNING('Tickers already updated today. Use --force to update anyway.'))
            else:
                tickers = self.fetch_polygon_tickers()
                self.save_tickers_to_db(tickers)
                self.stdout.write(self.style.SUCCESS('Updated all tickers.'))

    def fetch_polygon_tickers(self):
        """Fetch all crypto tickers from Polygon API."""
        url = f"{settings.POLYGON_BASE_URL}/v3/reference/tickers"
        params = {
            'market': 'crypto',
            'active': 'true',
            'limit': 1000,
            'sort': 'ticker',
            'order': 'asc',
            'apikey': settings.POLYGON_API_KEY
        }
        
        tickers = []
        page_count = 0
        
        while True:
            page_count += 1
            self.stdout.write(f'Fetching page {page_count}...')
            
            try:
                resp = requests.get(url, params=params, timeout=settings.POLYGON_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                
                results = data.get('results', [])
                tickers.extend(results)
                self.stdout.write(f'  Retrieved {len(results)} tickers (total: {len(tickers)})')
                
                next_url = data.get('next_url')
                if not next_url:
                    break
                
                url = next_url
                params = {'apikey': settings.POLYGON_API_KEY}
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Error fetching tickers: {e}'))
                raise
        
        self.stdout.write(self.style.SUCCESS(f'Total tickers fetched: {len(tickers)}'))
        return tickers

    def save_tickers_to_db(self, tickers):
        """Save or update tickers in the database."""
        updated_count = 0
        created_count = 0
        skipped_count = 0
        
        for t in tickers:
            # Skip delisted tickers
            if t.get('delisted_utc'):
                skipped_count += 1
                continue
            
            ticker = t.get('ticker', '')
            name = t.get('name', '')
            market = t.get('market', '')
            locale = t.get('locale', '')
            active = t.get('active', False)
            currency_symbol = t.get('currency_symbol', '')
            base_currency_symbol = t.get('base_currency_symbol', '')
            
            # Extract crypto symbol from ticker
            crypto_symbol = ''
            if ticker.startswith('X:') and ticker.endswith('USD'):
                crypto_symbol = ticker.replace('X:', '').replace('USD', '')
            elif '-' in ticker:
                parts = ticker.split('-')
                if len(parts) >= 2:
                    crypto_symbol = parts[0]
            
            # Prepare ticker data
            ticker_data = {
                'name': name,
                'crypto_symbol': crypto_symbol,
                'market': market,
                'locale': locale,
                'active': active,
                'is_usd_pair': ticker.endswith('USD') or base_currency_symbol == 'USD',
                'currency_symbol': currency_symbol,
                'base_currency_symbol': base_currency_symbol,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Update or create ticker
            ticker_obj, created = Ticker.objects.update_or_create(
                ticker=ticker,
                defaults=ticker_data
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database updated: {created_count} created, {updated_count} updated, {skipped_count} skipped (delisted)'
            )
        )

    def check_already_updated_today(self):
        """Check if any ticker has been updated today."""
        today = datetime.now().strftime('%Y-%m-%d')
        return Ticker.objects.filter(last_updated__startswith=today).exists()

    def clear_all_tickers(self):
        """Delete all tickers from the database."""
        count = Ticker.objects.count()
        Ticker.objects.all().delete()
        return count
