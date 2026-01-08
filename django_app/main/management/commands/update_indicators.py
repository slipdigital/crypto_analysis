"""
Django management command to automatically update indicators using their calculator classes.

Usage:
    python manage.py update_indicators
    python manage.py update_indicators --indicator-id 1
    python manage.py update_indicators --date 2026-01-08
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime, timedelta
from main.models import Indicator, IndicatorData


class Command(BaseCommand):
    help = 'Automatically update indicators using their calculator classes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--indicator-id',
            type=int,
            help='Update only a specific indicator by ID'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Date to calculate for (YYYY-MM-DD), defaults to yesterday'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data already exists for the date'
        )

    def handle(self, *args, **options):
        # Parse date
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Invalid date format: {options['date']}"))
                return
        else:
            # Default to yesterday
            target_date = (datetime.now() - timedelta(days=1)).date()
        
        # Get indicators to update
        query = Indicator.objects.filter(auto_update=True).exclude(calculator_class__isnull=True)
        
        if options['indicator_id']:
            query = query.filter(id=options['indicator_id'])
        
        indicators = list(query)
        
        if not indicators:
            self.stdout.write(self.style.WARNING('No indicators configured for auto-update'))
            return
        
        self.stdout.write(self.style.SUCCESS(f"\n=== Updating {len(indicators)} indicators for {target_date} ===\n"))
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for indicator in indicators:
            try:
                # Check if data already exists
                existing = IndicatorData.objects.filter(
                    indicator=indicator,
                    date=target_date
                ).first()
                
                if existing and not options['force']:
                    self.stdout.write(f"⊘ {indicator.title}: Data already exists (use --force to overwrite)")
                    skipped_count += 1
                    continue
                
                # Calculate value
                self.stdout.write(f"→ {indicator.title}: Calculating...", ending=' ')
                value = indicator.calculate_value(date=target_date)
                
                # Save or update
                if existing:
                    existing.value = value
                    existing.updated_at = datetime.now().isoformat()
                    existing.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated: {value:.3f}"))
                else:
                    IndicatorData.objects.create(
                        indicator=indicator,
                        date=target_date,
                        value=value,
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created: {value:.3f}"))
                
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n  Error: {str(e)}"))
                error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Complete ==="))
        self.stdout.write(f"Success: {success_count} | Errors: {error_count} | Skipped: {skipped_count}\n")
