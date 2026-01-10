from django.contrib import admin
from .models import Ticker, TickerData, GlobalLiquidity, IndicatorType, Indicator, IndicatorData


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'name', 'crypto_symbol', 'market_cap', 'active', 'is_usd_pair', 'is_favorite']
    list_filter = ['active', 'is_usd_pair', 'is_favorite', 'market']
    search_fields = ['ticker', 'name', 'crypto_symbol']
    ordering = ['-market_cap', 'ticker']


@admin.register(TickerData)
class TickerDataAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'date', 'close', 'open', 'high', 'low', 'volume']
    list_filter = ['date']
    search_fields = ['ticker__ticker']
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(GlobalLiquidity)
class GlobalLiquidityAdmin(admin.ModelAdmin):
    list_display = ['series_id', 'series_name', 'date', 'value', 'units', 'frequency']
    list_filter = ['series_id', 'frequency']
    search_fields = ['series_id', 'series_name']
    date_hierarchy = 'date'


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color']
    search_fields = ['name', 'description']


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['title', 'indicator_type', 'url']
    list_filter = ['indicator_type']
    search_fields = ['title', 'description']


@admin.register(IndicatorData)
class IndicatorDataAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'date', 'value']
    list_filter = ['indicator', 'date']
    search_fields = ['indicator__title']
    date_hierarchy = 'date'
