from django.db import models
from django.utils import timezone


class Ticker(models.Model):
    """Cryptocurrency ticker information."""
    ticker = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    crypto_symbol = models.CharField(max_length=50, null=True, blank=True)
    market = models.CharField(max_length=100, null=True, blank=True)
    locale = models.CharField(max_length=10, null=True, blank=True)
    active = models.BooleanField(default=True)
    is_usd_pair = models.BooleanField(default=False)
    currency_symbol = models.CharField(max_length=10, null=True, blank=True)
    currency_name = models.CharField(max_length=100, null=True, blank=True)
    base_currency_symbol = models.CharField(max_length=10, null=True, blank=True)
    base_currency_name = models.CharField(max_length=100, null=True, blank=True)
    market_cap = models.FloatField(null=True, blank=True)
    last_trade_timestamp = models.FloatField(null=True, blank=True)
    last_updated = models.CharField(max_length=100, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        db_table = 'tickers'
        ordering = ['-market_cap', 'ticker']

    def __str__(self):
        return self.ticker


class TickerData(models.Model):
    """Historical price data for tickers."""
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='ticker_data')
    date = models.DateField(db_index=True)
    open = models.FloatField(null=True, blank=True)
    high = models.FloatField(null=True, blank=True)
    low = models.FloatField(null=True, blank=True)
    close = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    vwap = models.FloatField(null=True, blank=True)  # Volume weighted average price
    transactions = models.IntegerField(null=True, blank=True)
    collected_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'ticker_data'
        unique_together = [['ticker', 'date']]
        ordering = ['date']
        indexes = [
            models.Index(fields=['ticker', 'date']),
        ]

    def __str__(self):
        return f"{self.ticker.ticker} - {self.date}"


class GlobalLiquidity(models.Model):
    """Global liquidity data from FRED."""
    series_id = models.CharField(max_length=50, db_index=True)  # FRED series ID
    series_name = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(db_index=True)
    value = models.FloatField(null=True, blank=True)  # Value in billions
    units = models.CharField(max_length=100, null=True, blank=True)
    frequency = models.CharField(max_length=50, null=True, blank=True)
    collected_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'global_liquidity'
        unique_together = [['series_id', 'date']]
        ordering = ['date']

    def __str__(self):
        return f"{self.series_id} - {self.date}"


class IndicatorType(models.Model):
    """Types/categories for indicators."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=7, null=True, blank=True)  # Hex color code
    created_at = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'indicator_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Indicator(models.Model):
    """Market indicators."""
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True)
    indicator_type = models.ForeignKey(IndicatorType, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'indicators'
        ordering = ['title']

    def __str__(self):
        return self.title


class IndicatorData(models.Model):
    """Time series data for indicators."""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='indicator_data')
    date = models.DateField(db_index=True)
    value = models.FloatField()  # Between -1.0 and 1.0
    created_at = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'indicator_data'
        unique_together = [['indicator', 'date']]
        ordering = ['date']
        indexes = [
            models.Index(fields=['indicator', 'date']),
        ]

    def __str__(self):
        return f"{self.indicator.title} - {self.date}"
