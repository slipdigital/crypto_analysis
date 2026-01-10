"""
Django management command to create the BTC RSI indicator.

Usage:
    python manage.py create_rsi_indicator
"""
from django.core.management.base import BaseCommand
from datetime import datetime
from main.models import Indicator, IndicatorType


class Command(BaseCommand):
    help = 'Create BTC RSI indicator with dynamic calculator'

    def handle(self, *args, **options):
        # Get or create Technical indicator type
        indicator_type, created = IndicatorType.objects.get_or_create(
            name='Technical',
            defaults={
                'description': 'Technical analysis indicators based on price and volume data',
                'color': '#3B82F6',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created indicator type: {indicator_type.name}"))
        else:
            self.stdout.write(f"✓ Found existing indicator type: {indicator_type.name}")
        
        # Check if RSI indicator already exists
        existing = Indicator.objects.filter(title='BTC RSI').first()
        
        if existing:
            self.stdout.write(self.style.WARNING(f"\n⚠ Indicator 'BTC RSI' already exists (ID: {existing.id})"))
            response = input("Do you want to update it? (y/n): ")
            
            if response.lower() != 'y':
                self.stdout.write("Aborted.")
                return
            
            # Update existing
            existing.description = (
                "Relative Strength Index (RSI) for Bitcoin (BTCUSD). "
                "RSI is a momentum oscillator that measures overbought/oversold conditions. "
                "Scores: +1.0 = Oversold (bullish), 0.0 = Neutral, -1.0 = Overbought (bearish)"
            )
            existing.url = 'https://www.investopedia.com/terms/r/rsi.asp'
            existing.indicator_type = indicator_type
            existing.calculator_class = 'main.indicators.rsi.RSICalculator'
            existing.calculator_config = {
                'ticker': 'X:BTCUSD',
                'period': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70
            }
            existing.auto_update = True
            existing.updated_at = datetime.now().isoformat()
            existing.save()
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Updated indicator: {existing.title} (ID: {existing.id})"))
        else:
            # Create new indicator
            indicator = Indicator.objects.create(
                title='BTC RSI',
                description=(
                    "Relative Strength Index (RSI) for Bitcoin (BTCUSD). "
                    "RSI is a momentum oscillator that measures overbought/oversold conditions. "
                    "Scores: +1.0 = Oversold (bullish), 0.0 = Neutral, -1.0 = Overbought (bearish)"
                ),
                url='https://www.investopedia.com/terms/r/rsi.asp',
                indicator_type=indicator_type,
                calculator_class='main.indicators.rsi.RSICalculator',
                calculator_config={
                    'ticker': 'X:BTCUSD',
                    'period': 14,
                    'oversold_threshold': 30,
                    'overbought_threshold': 70
                },
                auto_update=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created indicator: {indicator.title} (ID: {indicator.id})"))
        
        # Show configuration
        indicator = Indicator.objects.get(title='BTC RSI')
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("RSI Indicator Configuration:"))
        self.stdout.write("="*60)
        self.stdout.write(f"Title: {indicator.title}")
        self.stdout.write(f"Type: {indicator.indicator_type.name}")
        self.stdout.write(f"Calculator: {indicator.calculator_class}")
        self.stdout.write(f"Auto-update: {indicator.auto_update}")
        self.stdout.write(f"\nConfiguration:")
        for key, value in indicator.calculator_config.items():
            self.stdout.write(f"  {key}: {value}")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("\nTo calculate values, run:"))
        self.stdout.write(f"  python manage.py update_indicators --indicator-id {indicator.id}")
        self.stdout.write("\nOr for all auto-update indicators:")
        self.stdout.write("  python manage.py update_indicators")
        self.stdout.write("="*60 + "\n")
