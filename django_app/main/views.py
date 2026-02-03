from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Min, Max, Count, Q
from django.core.management import call_command
from django.core.cache import cache
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import subprocess
import sys
import os
import threading
import uuid
from io import StringIO
from .models import Ticker, TickerData, GlobalLiquidity, IndicatorType, Indicator, IndicatorData


# ====================
# Home View (redirects to tickers)
# ====================

def home(request):
    """Home page view - redirect to tickers list."""
    return redirect('index')


# ====================
# Ticker Views
# ====================

def index(request):
    """Display all tickers alphabetically."""
    # Get query parameters for filtering
    active_only = request.GET.get('active_only', 'true').lower() == 'true'
    usd_only = request.GET.get('usd_only', 'true').lower() == 'true'
    has_data_only = request.GET.get('has_data_only', 'true').lower() == 'true'
    favorites_only = request.GET.get('favorites_only', 'false').lower() == 'true'
    search = request.GET.get('search', '').strip()
    
    # Build query
    tickers = Ticker.objects.all().order_by('-market_cap', 'ticker')
    
    if active_only:
        tickers = tickers.filter(active=True)
    
    if usd_only:
        tickers = tickers.filter(is_usd_pair=True)
    
    if favorites_only:
        tickers = tickers.filter(is_favorite=True)
    
    if has_data_only:
        # Only show tickers that have data in ticker_data
        tickers = tickers.filter(ticker_data__isnull=False).distinct()
    
    if search:
        tickers = tickers.filter(
            Q(ticker__icontains=search) | 
            Q(name__icontains=search) |
            Q(crypto_symbol__icontains=search)
        )
    
    # Get date ranges for each ticker from ticker_data
    ticker_data_ranges = {}
    today = datetime.now().date()
    
    # Convert to list to allow modification
    tickers_list = list(tickers)
    
    for ticker in tickers_list:
        date_range = TickerData.objects.filter(ticker=ticker).aggregate(
            start_date=Min('date'),
            end_date=Max('date')
        )
        
        if date_range['start_date']:
            end_date = date_range['end_date']
            days_old = (today - end_date).days if end_date else None
            ticker_data_ranges[ticker.ticker] = {
                'start_date': date_range['start_date'],
                'end_date': end_date,
                'days_old': days_old
            }
            # Attach computed data directly to ticker object for easy template access
            ticker.data_start_date = date_range['start_date']
            ticker.data_end_date = end_date
            ticker.data_days_old = days_old
        else:
            ticker.data_start_date = None
            ticker.data_end_date = None
            ticker.data_days_old = None
    
    # Check for outdated data (data older than 2 days)
    threshold_date = today - timedelta(days=2)
    
    # Get favorite ticker symbols for filtering
    favorite_ticker_symbols = set(
        t.ticker for t in tickers if t.is_favorite
    )
    
    # Find FAVORITED tickers with outdated data
    outdated_tickers = []
    for ticker_symbol, date_info in ticker_data_ranges.items():
        # Only check favorited tickers
        if ticker_symbol in favorite_ticker_symbols and date_info['end_date'] < threshold_date:
            days_old = (today - date_info['end_date']).days
            outdated_tickers.append({
                'ticker': ticker_symbol,
                'last_date': date_info['end_date'],
                'days_old': days_old
            })
    
    # Sort by most outdated first
    outdated_tickers.sort(key=lambda x: x['days_old'], reverse=True)
    
    # Get total favorites count
    favorites_count = Ticker.objects.filter(is_favorite=True).count()
    
    return render(request, 'tickers.html', {
        'tickers': tickers_list,
        'active_only': active_only,
        'usd_only': usd_only,
        'has_data_only': has_data_only,
        'favorites_only': favorites_only,
        'search': search,
        'total_count': len(tickers_list),
        'favorites_count': favorites_count,
        'ticker_data_ranges': ticker_data_ranges,
        'outdated_tickers': outdated_tickers,
        'today': today
    })


def ticker_detail(request, ticker_symbol):
    """Display detailed information for a specific ticker."""
    ticker = get_object_or_404(Ticker, ticker=ticker_symbol)
    return render(request, 'ticker_detail.html', {'ticker': ticker})


def ticker_chart(request, ticker_symbol):
    """Display stock-style chart for a specific ticker."""
    ticker = get_object_or_404(Ticker, ticker=ticker_symbol)
    
    # Get time range from query params (default to 90 days)
    days = request.GET.get('days', '90')
    try:
        days = int(days)
    except ValueError:
        days = 90
    
    # Get historical data
    start_date = datetime.now().date() - timedelta(days=days)
    
    ticker_data = TickerData.objects.filter(
        ticker=ticker,
        date__gte=start_date
    ).order_by('date')
    
    # Get all available data for date range info
    all_data_info = TickerData.objects.filter(ticker=ticker).aggregate(
        first_date=Min('date'),
        last_date=Max('date'),
        total_records=Count('id')
    )
    
    return render(request, 'ticker_chart.html', {
        'ticker': ticker,
        'ticker_data': ticker_data,
        'days': days,
        'all_data_info': all_data_info
    })


def toggle_favorite(request, ticker_symbol):
    """Toggle favorite status for a ticker."""
    if request.method != 'POST':
        return redirect('index')
    
    ticker = get_object_or_404(Ticker, ticker=ticker_symbol)
    
    # Toggle favorite status
    ticker.is_favorite = not ticker.is_favorite
    ticker.save()
    
    status = "added to" if ticker.is_favorite else "removed from"
    messages.success(request, f'{ticker_symbol} {status} favorites')
    
    # Redirect back to the page that made the request
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def ticker_edit(request, ticker_symbol):
    """Edit ticker market cap."""
    ticker = get_object_or_404(Ticker, ticker=ticker_symbol)
    
    if request.method == 'POST':
        try:
            market_cap_value = request.POST.get('market_cap', '').strip()
            
            if market_cap_value:
                ticker.market_cap = float(market_cap_value)
            else:
                ticker.market_cap = None
            
            ticker.save()
            messages.success(request, f'Market cap updated successfully for {ticker_symbol}')
            return redirect('index')
        except ValueError:
            messages.error(request, 'Invalid market cap value. Please enter a valid number.')
        except Exception as e:
            messages.error(request, f'Error updating market cap: {str(e)}')
    
    return render(request, 'ticker_edit.html', {'ticker': ticker})


# ====================
# Chart Views
# ====================

def charts(request):
    """Display charts page with links to different chart types."""
    return render(request, 'charts.html')


def charts_compare(request):
    """Display relative strength comparison between two tickers."""
    # Get all active tickers for dropdown, ordered by market cap (descending)
    tickers = Ticker.objects.filter(active=True).order_by('-market_cap', 'ticker')
    
    ticker1_symbol = request.GET.get('ticker1')
    ticker2_symbol = request.GET.get('ticker2')
    days = request.GET.get('days', '90')
    
    try:
        days = int(days)
    except ValueError:
        days = 90
    
    chart_data = None
    ticker1 = None
    ticker2 = None
    
    if ticker1_symbol and ticker2_symbol:
        # Get ticker objects
        ticker1 = Ticker.objects.filter(ticker=ticker1_symbol).first()
        ticker2 = Ticker.objects.filter(ticker=ticker2_symbol).first()
        
        if ticker1 and ticker2:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get price data for both tickers
            data1 = TickerData.objects.filter(
                ticker=ticker1,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            data2 = TickerData.objects.filter(
                ticker=ticker2,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if data1 and data2:
                # Create date-indexed dictionaries
                prices1 = {str(d.date): d.close for d in data1}
                prices2 = {str(d.date): d.close for d in data2}
                
                # Find common dates
                common_dates = sorted(set(prices1.keys()) & set(prices2.keys()))
                
                if common_dates:
                    # Normalize to starting prices (index to 100)
                    start_price1 = prices1[common_dates[0]]
                    start_price2 = prices2[common_dates[0]]
                    
                    dates_list = common_dates
                    ticker1_prices_list = [prices1[d] for d in common_dates]
                    ticker2_prices_list = [prices2[d] for d in common_dates]
                    ticker1_indexed_list = [(prices1[d] / start_price1) * 100 for d in common_dates]
                    ticker2_indexed_list = [(prices2[d] / start_price2) * 100 for d in common_dates]
                    relative_strength_list = [(prices1[d] / prices2[d]) for d in common_dates]
                    rs_normalized_list = [((prices1[d] / prices2[d]) / (start_price1 / start_price2)) * 100 for d in common_dates]
                    
                    chart_data = {
                        'dates': json.dumps(dates_list),
                        'ticker1_prices': json.dumps(ticker1_prices_list),
                        'ticker2_prices': json.dumps(ticker2_prices_list),
                        'ticker1_indexed': json.dumps(ticker1_indexed_list),
                        'ticker2_indexed': json.dumps(ticker2_indexed_list),
                        'relative_strength': json.dumps(relative_strength_list),
                        'rs_normalized': json.dumps(rs_normalized_list)
                    }
                    
                    # Calculate statistics
                    rs_values = relative_strength_list
                    chart_data['stats'] = {
                        'ticker1_change': ((prices1[common_dates[-1]] / start_price1) - 1) * 100,
                        'ticker2_change': ((prices2[common_dates[-1]] / start_price2) - 1) * 100,
                        'rs_current': rs_values[-1],
                        'rs_start': rs_values[0],
                        'rs_change': ((rs_values[-1] / rs_values[0]) - 1) * 100,
                        'ticker1_outperforming': rs_values[-1] > rs_values[0]
                    }
    
    return render(request, 'charts_compare.html', {
        'tickers': tickers,
        'ticker1': ticker1,
        'ticker2': ticker2,
        'chart_data': chart_data,
        'days': days
    })


def top_gainers(request):
    """Display top gainers/losers chart."""
    # Get top 30 tickers by market cap
    top_tickers = Ticker.objects.filter(
        market_cap__isnull=False,
        active=True
    ).order_by('-market_cap')[:30]
    
    # Calculate gains/losses for each ticker
    gains_data = []
    today = datetime.now().date()
    
    for ticker in top_tickers:
        # Get current price (most recent)
        current_data = TickerData.objects.filter(ticker=ticker).order_by('-date').first()
        
        if not current_data:
            continue
        
        current_price = current_data.close
        ticker_gains = {
            'ticker': ticker.ticker,
            'name': ticker.name,
            'crypto_symbol': ticker.crypto_symbol,
            'market_cap': ticker.market_cap,
            'current_price': current_price
        }
        
        # Calculate gains for different periods
        periods = [1, 3, 5, 7, 10, 20, 40, 100]
        for days in periods:
            target_date = today - timedelta(days=days)
            
            # Get price from that date (or closest available)
            historical_data = TickerData.objects.filter(
                ticker=ticker,
                date__lte=target_date
            ).order_by('-date').first()
            
            if historical_data and historical_data.close:
                old_price = historical_data.close
                change_percent = ((current_price - old_price) / old_price) * 100
                ticker_gains[f'gain_{days}d'] = change_percent
            else:
                ticker_gains[f'gain_{days}d'] = None
        
        gains_data.append(ticker_gains)
    
    return render(request, 'top_gainers.html', {
        'gains_data': gains_data,
        'periods': [1, 3, 5, 7, 10, 20, 40, 100]
    })


# ====================
# Indicator Type Views
# ====================

def indicator_types(request):
    """Display all indicator types."""
    types = IndicatorType.objects.all().order_by('name')
    
    # Count indicators for each type
    type_counts = {}
    for ind_type in types:
        count = Indicator.objects.filter(indicator_type=ind_type).count()
        type_counts[ind_type.id] = count
    
    return render(request, 'indicator_types.html', {
        'types': types,
        'type_counts': type_counts
    })


def indicator_type_create(request):
    """Create a new indicator type."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#6B7280').strip()
        
        if not name:
            messages.error(request, 'Name is required!')
            return redirect('indicator_type_create')
        
        # Check if name already exists
        if IndicatorType.objects.filter(name=name).exists():
            messages.error(request, f'Indicator type "{name}" already exists!')
            return redirect('indicator_type_create')
        
        # Create new indicator type
        IndicatorType.objects.create(
            name=name,
            description=description,
            color=color,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        messages.success(request, f'Indicator type "{name}" created successfully!')
        return redirect('indicator_types')
    
    return render(request, 'indicator_type_form.html', {
        'type': None,
        'action': 'Create'
    })


def indicator_type_edit(request, type_id):
    """Edit an existing indicator type."""
    ind_type = get_object_or_404(IndicatorType, id=type_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#6B7280').strip()
        
        if not name:
            messages.error(request, 'Name is required!')
            return redirect('indicator_type_edit', type_id=type_id)
        
        # Check if name already exists (excluding current)
        if IndicatorType.objects.filter(name=name).exclude(id=type_id).exists():
            messages.error(request, f'Indicator type "{name}" already exists!')
            return redirect('indicator_type_edit', type_id=type_id)
        
        # Update indicator type
        ind_type.name = name
        ind_type.description = description
        ind_type.color = color
        ind_type.updated_at = datetime.now().isoformat()
        ind_type.save()
        
        messages.success(request, f'Indicator type "{name}" updated successfully!')
        return redirect('indicator_types')
    
    return render(request, 'indicator_type_form.html', {
        'type': ind_type,
        'action': 'Update'
    })


def indicator_type_delete(request, type_id):
    """Delete an indicator type."""
    if request.method != 'POST':
        return redirect('indicator_types')
    
    ind_type = get_object_or_404(IndicatorType, id=type_id)
    
    # Check if any indicators use this type
    indicator_count = Indicator.objects.filter(indicator_type=ind_type).count()
    
    if indicator_count > 0:
        messages.error(request, f'Cannot delete "{ind_type.name}" because {indicator_count} indicator(s) are using it. Please reassign or delete those indicators first.')
        return redirect('indicator_types')
    
    name = ind_type.name
    ind_type.delete()
    
    messages.success(request, f'Indicator type "{name}" deleted successfully!')
    return redirect('indicator_types')


# ====================
# Indicator Views
# ====================

def indicators(request):
    """Display all indicators."""
    indicators_with_types = []
    indicators_list = Indicator.objects.all().order_by('-created_at')
    
    for indicator in indicators_list:
        indicators_with_types.append({
            'indicator': indicator,
            'type': indicator.indicator_type
        })
    
    return render(request, 'indicators.html', {
        'indicators_with_types': indicators_with_types
    })


def indicator_create(request):
    """Create a new indicator."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        url = request.POST.get('url', '').strip()
        type_id = request.POST.get('indicator_type_id')
        auto_update = request.POST.get('auto_update') == 'on'
        calculator_class = request.POST.get('calculator_class', '').strip()
        calculator_config = request.POST.get('calculator_config', '').strip()
        
        if not title:
            messages.error(request, 'Title is required')
            types = IndicatorType.objects.all().order_by('name')
            return render(request, 'indicator_form.html', {
                'mode': 'create',
                'indicator': None,
                'types': types
            })
        
        # Parse calculator_config JSON if provided
        calculator_config_json = None
        if calculator_config:
            try:
                calculator_config_json = json.loads(calculator_config)
            except json.JSONDecodeError as e:
                messages.error(request, f'Invalid JSON in calculator config: {str(e)}')
                types = IndicatorType.objects.all().order_by('name')
                indicator_obj = type('obj', (object,), {
                    'title': title,
                    'description': description,
                    'url': url,
                    'indicator_type_id': type_id,
                    'auto_update': auto_update,
                    'calculator_class': calculator_class,
                    'calculator_config_json': calculator_config
                })
                return render(request, 'indicator_form.html', {
                    'mode': 'create',
                    'indicator': indicator_obj,
                    'types': types
                })
        
        try:
            indicator = Indicator.objects.create(
                title=title,
                description=description,
                url=url if url else None,
                indicator_type_id=type_id if type_id else None,
                auto_update=auto_update,
                calculator_class=calculator_class if calculator_class else None,
                calculator_config=calculator_config_json,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            messages.success(request, f'Indicator "{title}" created successfully')
            return redirect('indicators')
            
        except Exception as e:
            messages.error(request, f'Error creating indicator: {str(e)}')
    
    types = IndicatorType.objects.all().order_by('name')
    return render(request, 'indicator_form.html', {
        'mode': 'create',
        'indicator': None,
        'types': types
    })


def indicator_edit(request, indicator_id):
    """Edit an existing indicator."""
    indicator = get_object_or_404(Indicator, id=indicator_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        url = request.POST.get('url', '').strip()
        type_id = request.POST.get('indicator_type_id')
        auto_update = request.POST.get('auto_update') == 'on'
        calculator_class = request.POST.get('calculator_class', '').strip()
        calculator_config = request.POST.get('calculator_config', '').strip()
        
        if not title:
            messages.error(request, 'Title is required')
            types = IndicatorType.objects.all().order_by('name')
            return render(request, 'indicator_form.html', {
                'mode': 'edit',
                'indicator': indicator,
                'types': types
            })
        
        # Parse calculator_config JSON if provided
        calculator_config_json = None
        if calculator_config:
            try:
                calculator_config_json = json.loads(calculator_config)
            except json.JSONDecodeError as e:
                messages.error(request, f'Invalid JSON in calculator config: {str(e)}')
                types = IndicatorType.objects.all().order_by('name')
                # Keep the invalid JSON so user can fix it
                indicator.calculator_config_json = calculator_config
                return render(request, 'indicator_form.html', {
                    'mode': 'edit',
                    'indicator': indicator,
                    'types': types
                })
        
        try:
            indicator.title = title
            indicator.description = description
            indicator.url = url if url else None
            indicator.indicator_type_id = type_id if type_id else None
            indicator.auto_update = auto_update
            indicator.calculator_class = calculator_class if calculator_class else None
            indicator.calculator_config = calculator_config_json
            indicator.updated_at = datetime.now().isoformat()
            indicator.save()
            
            messages.success(request, f'Indicator "{title}" updated successfully')
            return redirect('indicators')
            
        except Exception as e:
            messages.error(request, f'Error updating indicator: {str(e)}')
    
    types = IndicatorType.objects.all().order_by('name')
    return render(request, 'indicator_form.html', {
        'mode': 'edit',
        'indicator': indicator,
        'types': types
    })


def indicator_delete(request, indicator_id):
    """Delete an indicator."""
    if request.method != 'POST':
        return redirect('indicators')
    
    indicator = get_object_or_404(Indicator, id=indicator_id)
    
    try:
        title = indicator.title
        indicator.delete()
        messages.success(request, f'Indicator "{title}" deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting indicator: {str(e)}')
    
    return redirect('indicators')


def indicator_data_list(request, indicator_id):
    """View all data points for an indicator."""
    from datetime import timedelta
    import json
    
    indicator = get_object_or_404(Indicator, id=indicator_id)
    
    # Get all data points for this indicator, ordered by date desc
    data_points = IndicatorData.objects.filter(indicator=indicator).order_by('-date')
    
    # Add position_percent to each data point for visual representation
    data_points_with_position = []
    for dp in data_points:
        data_points_with_position.append({
            'id': dp.id,
            'date': dp.date,
            'value': dp.value,
            'position_percent': round((dp.value + 1.0) / 2.0 * 100, 2),
            'created_at': dp.created_at,
            'updated_at': dp.updated_at
        })
    
    # Get statistics
    stats = None
    if data_points.exists():
        values = [d.value for d in data_points]
        stats = {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'latest': data_points[0].value,
            'latest_date': data_points[0].date
        }
    
    # Get chart data for last 4 weeks
    from django.utils import timezone
    four_weeks_ago = timezone.now().date() - timedelta(days=28)
    chart_data_points = IndicatorData.objects.filter(
        indicator=indicator,
        date__gte=four_weeks_ago
    ).order_by('date')
    
    chart_data = {
        'labels': [dp.date.strftime('%Y-%m-%d') for dp in chart_data_points],
        'values': [float(dp.value) for dp in chart_data_points]
    }
    chart_data_json = json.dumps(chart_data)
    
    return render(request, 'indicator_data.html', {
        'indicator': indicator,
        'data_points': data_points_with_position,
        'stats': stats,
        'chart_data': chart_data_json
    })


def indicator_data_add(request, indicator_id):
    """Add a new data point to an indicator."""
    indicator = get_object_or_404(Indicator, id=indicator_id)
    
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        value_str = request.POST.get('value', '').strip()
        
        if not date_str or not value_str:
            messages.error(request, 'Date and value are required')
            return render(request, 'indicator_data_form.html', {
                'mode': 'add',
                'indicator': indicator,
                'data_point': None,
                'today': datetime.now().date().isoformat()
            })
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse and validate value
            value = float(value_str)
            if value < -1.0 or value > 1.0:
                messages.error(request, 'Value must be between -1.0 and 1.0')
                return render(request, 'indicator_data_form.html', {
                    'mode': 'add',
                    'indicator': indicator,
                    'data_point': None,
                    'today': datetime.now().date().isoformat()
                })
            
            # Check if data point already exists for this date
            if IndicatorData.objects.filter(indicator=indicator, date=date_obj).exists():
                messages.warning(request, f'Data point for {date_str} already exists. Use edit to update it.')
                return render(request, 'indicator_data_form.html', {
                    'mode': 'add',
                    'indicator': indicator,
                    'data_point': None,
                    'today': datetime.now().date().isoformat()
                })
            
            # Create new data point
            IndicatorData.objects.create(
                indicator=indicator,
                date=date_obj,
                value=value,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            messages.success(request, f'Data point added for {date_str}')
            return redirect('indicator_data_list', indicator_id=indicator_id)
            
        except ValueError as e:
            messages.error(request, f'Invalid date or value format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error adding data point: {str(e)}')
    
    return render(request, 'indicator_data_form.html', {
        'mode': 'add',
        'indicator': indicator,
        'data_point': None,
        'today': datetime.now().date().isoformat()
    })


def indicator_data_edit(request, indicator_id, data_id):
    """Edit an existing data point."""
    indicator = get_object_or_404(Indicator, id=indicator_id)
    data_point = get_object_or_404(IndicatorData, id=data_id, indicator=indicator)
    
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        value_str = request.POST.get('value', '').strip()
        
        if not date_str or not value_str:
            messages.error(request, 'Date and value are required')
            return render(request, 'indicator_data_form.html', {
                'mode': 'edit',
                'indicator': indicator,
                'data_point': data_point,
                'today': datetime.now().date().isoformat()
            })
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse and validate value
            value = float(value_str)
            if value < -1.0 or value > 1.0:
                messages.error(request, 'Value must be between -1.0 and 1.0')
                return render(request, 'indicator_data_form.html', {
                    'mode': 'edit',
                    'indicator': indicator,
                    'data_point': data_point,
                    'today': datetime.now().date().isoformat()
                })
            
            # Check if another data point exists for this date (excluding current)
            if IndicatorData.objects.filter(
                indicator=indicator,
                date=date_obj
            ).exclude(id=data_id).exists():
                messages.warning(request, f'Another data point for {date_str} already exists')
                return render(request, 'indicator_data_form.html', {
                    'mode': 'edit',
                    'indicator': indicator,
                    'data_point': data_point,
                    'today': datetime.now().date().isoformat()
                })
            
            # Update data point
            data_point.date = date_obj
            data_point.value = value
            data_point.updated_at = datetime.now().isoformat()
            data_point.save()
            
            messages.success(request, f'Data point updated for {date_str}')
            return redirect('indicator_data_list', indicator_id=indicator_id)
            
        except ValueError as e:
            messages.error(request, f'Invalid date or value format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error updating data point: {str(e)}')
    
    return render(request, 'indicator_data_form.html', {
        'mode': 'edit',
        'indicator': indicator,
        'data_point': data_point,
        'today': datetime.now().date().isoformat()
    })


def indicator_data_delete(request, indicator_id, data_id):
    """Delete a data point."""
    if request.method != 'POST':
        return redirect('indicator_data_list', indicator_id=indicator_id)
    
    indicator = get_object_or_404(Indicator, id=indicator_id)
    data_point = get_object_or_404(IndicatorData, id=data_id, indicator=indicator)
    
    try:
        date_str = str(data_point.date)
        data_point.delete()
        messages.success(request, f'Data point for {date_str} deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting data point: {str(e)}')
    
    return redirect('indicator_data_list', indicator_id=indicator_id)


def indicator_bulk_entry(request):
    """Add data points for multiple indicators at once."""
    # Get all indicators with their types
    indicators_list = Indicator.objects.select_related('indicator_type').all().order_by(
        'indicator_type__name', 'title'
    )
    
    if not indicators_list.exists():
        messages.warning(request, 'No indicators found. Create some indicators first.')
        return redirect('indicators')
    
    # Group indicators by type
    grouped_indicators = {}
    for indicator in indicators_list:
        type_name = indicator.indicator_type.name if indicator.indicator_type else 'Uncategorized'
        if type_name not in grouped_indicators:
            grouped_indicators[type_name] = []
        grouped_indicators[type_name].append(indicator)
    
    # Check if we should load existing data for a specific date (from GET parameter)
    selected_date = request.GET.get('date', '').strip()
    existing_values = {}
    
    # Default to today if no date is provided
    if not selected_date:
        selected_date = datetime.now().date().isoformat()
    
    # Load existing data for the selected date
    try:
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
        # Fetch existing data for this date
        existing_data = IndicatorData.objects.filter(date=date_obj).select_related('indicator')
        for data in existing_data:
            existing_values[data.indicator.id] = data.value
    except ValueError:
        selected_date = datetime.now().date().isoformat()  # Fall back to today on invalid date
    
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        
        if not date_str:
            messages.error(request, 'Date is required')
            return render(request, 'indicator_bulk_entry.html', {
                'indicators': indicators_list,
                'grouped_indicators': grouped_indicators,
                'today': datetime.now().date().isoformat()
            })
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Collect all indicator values from form
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []
            
            for indicator in indicators_list:
                value_str = request.POST.get(f'value_{indicator.id}', '').strip()
                
                # Skip if no value provided (empty string only, not zero)
                if value_str == '':
                    skipped_count += 1
                    continue
                
                try:
                    # Parse and validate value
                    value = float(value_str)
                    if value < -1.0 or value > 1.0:
                        errors.append(f'{indicator.title}: Value must be between -1.0 and 1.0')
                        continue
                    
                    # Check if data point already exists for this date
                    existing = IndicatorData.objects.filter(
                        indicator=indicator,
                        date=date_obj
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.value = value
                        existing.updated_at = datetime.now().isoformat()
                        existing.save()
                        updated_count += 1
                    else:
                        # Create new data point
                        IndicatorData.objects.create(
                            indicator=indicator,
                            date=date_obj,
                            value=value,
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat()
                        )
                        saved_count += 1
                    
                except ValueError:
                    errors.append(f'{indicator.title}: Invalid value "{value_str}"')
                    continue
            
            # Build success message
            messages_list = []
            if saved_count > 0:
                messages_list.append(f'{saved_count} new data point(s) added')
            if updated_count > 0:
                messages_list.append(f'{updated_count} data point(s) updated')
            if skipped_count > 0:
                messages_list.append(f'{skipped_count} indicator(s) skipped (no value provided)')
            
            if messages_list:
                messages.success(request, f'Bulk entry for {date_str}: {", ".join(messages_list)}')
            
            # Show errors if any
            for error in errors:
                messages.warning(request, error)
            
            # Redirect back to form for another entry
            return redirect('indicator_bulk_entry')
                
        except ValueError as e:
            messages.error(request, f'Invalid date format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
    
    return render(request, 'indicator_bulk_entry.html', {
        'indicators': indicators_list,
        'grouped_indicators': grouped_indicators,
        'today': datetime.now().date().isoformat(),
        'selected_date': selected_date,
        'existing_values': existing_values
    })


def indicator_data_range_entry(request, indicator_id):
    """Add data points for a single indicator across a date range."""
    indicator = get_object_or_404(Indicator, id=indicator_id)
    
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date', '').strip()
        end_date_str = request.POST.get('end_date', '').strip()
        value_str = request.POST.get('value', '').strip()
        overwrite_existing = request.POST.get('overwrite_existing') == 'on'
        
        if not start_date_str or not end_date_str:
            messages.error(request, 'Both start date and end date are required')
            return render(request, 'indicator_data_range_form.html', {
                'indicator': indicator,
                'today': datetime.now().date().isoformat()
            })
        
        if not value_str:
            messages.error(request, 'Value is required')
            return render(request, 'indicator_data_range_form.html', {
                'indicator': indicator,
                'today': datetime.now().date().isoformat()
            })
        
        try:
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if end_date < start_date:
                messages.error(request, 'End date must be after start date')
                return render(request, 'indicator_data_range_form.html', {
                    'indicator': indicator,
                    'today': datetime.now().date().isoformat()
                })
            
            # Parse value
            try:
                value = float(value_str)
                if value < -1.0 or value > 1.0:
                    messages.error(request, 'Value must be between -1.0 and 1.0')
                    return render(request, 'indicator_data_range_form.html', {
                        'indicator': indicator,
                        'today': datetime.now().date().isoformat()
                    })
            except ValueError:
                messages.error(request, 'Invalid value format. Must be a number between -1.0 and 1.0')
                return render(request, 'indicator_data_range_form.html', {
                    'indicator': indicator,
                    'today': datetime.now().date().isoformat()
                })
            
            # Generate list of dates
            current_date = start_date
            dates_to_process = []
            
            while current_date <= end_date:
                dates_to_process.append(current_date)
                current_date += timedelta(days=1)
            
            if not dates_to_process:
                messages.warning(request, 'No dates to process (all dates were filtered out)')
                return render(request, 'indicator_data_range_form.html', {
                    'indicator': indicator,
                    'today': datetime.now().date().isoformat()
                })
            
            # Process each date
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for date in dates_to_process:
                # Check if data already exists
                existing = IndicatorData.objects.filter(
                    indicator=indicator,
                    date=date
                ).first()
                
                if existing:
                    if overwrite_existing:
                        existing.value = value
                        existing.updated_at = datetime.now().isoformat()
                        existing.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Create new data point
                    IndicatorData.objects.create(
                        indicator=indicator,
                        date=date,
                        value=value,
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    added_count += 1
            
            # Build success message
            messages_list = []
            if added_count > 0:
                messages_list.append(f'{added_count} new data point(s) added')
            if updated_count > 0:
                messages_list.append(f'{updated_count} data point(s) updated')
            if skipped_count > 0:
                messages_list.append(f'{skipped_count} existing data point(s) skipped')
            
            messages.success(request, f'Date range entry completed: {", ".join(messages_list)}')
            return redirect('indicator_data_list', indicator_id=indicator_id)
            
        except ValueError as e:
            messages.error(request, f'Invalid date format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
    
    return render(request, 'indicator_data_range_form.html', {
        'indicator': indicator,
        'today': datetime.now().date().isoformat()
    })


def indicator_aggregate(request):
    """Display aggregated indicator data by type and date."""
    # Get filter parameters
    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get all indicator types
    indicator_types_list = IndicatorType.objects.all().order_by('name')
    
    # Get all indicators with their types
    indicators_list = Indicator.objects.all()
    
    # Create a mapping of indicator_id to type
    indicator_type_map = {}
    for indicator in indicators_list:
        indicator_type_map[indicator.id] = indicator.indicator_type_id
    
    # Query all indicator data within date range
    data_query = IndicatorData.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date').values('date', 'indicator_id', 'value')
    
    # Organize data by date
    daily_data = {}
    for data_point in data_query:
        date_str = str(data_point['date'])
        if date_str not in daily_data:
            daily_data[date_str] = {
                'date': data_point['date'],
                'by_type': {},
                'overall': []
            }
        
        # Get the type for this indicator
        type_id = indicator_type_map.get(data_point['indicator_id'])
        
        if type_id:
            if type_id not in daily_data[date_str]['by_type']:
                daily_data[date_str]['by_type'][type_id] = []
            daily_data[date_str]['by_type'][type_id].append(data_point['value'])
        
        # Add to overall
        daily_data[date_str]['overall'].append(data_point['value'])
    
    # Calculate averages for each date
    aggregated_data = []
    for date_str, data in sorted(daily_data.items(), reverse=True):
        date_info = {
            'date': data['date'],
            'type_averages': {},
            'overall_average': None,
            'data_points_count': len(data['overall'])
        }
        
        # Calculate type averages
        for type_id, values in data['by_type'].items():
            if values:
                date_info['type_averages'][type_id] = {
                    'average': sum(values) / len(values),
                    'count': len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        # Calculate overall average
        if data['overall']:
            date_info['overall_average'] = sum(data['overall']) / len(data['overall'])
        
        aggregated_data.append(date_info)
    
    # Get statistics for each type
    type_stats = {}
    for ind_type in indicator_types_list:
        type_values = []
        for date_data in aggregated_data:
            if ind_type.id in date_data['type_averages']:
                type_values.append(date_data['type_averages'][ind_type.id]['average'])
        
        if type_values:
            type_stats[ind_type.id] = {
                'avg': sum(type_values) / len(type_values),
                'min': min(type_values),
                'max': max(type_values),
                'count': len(type_values)
            }
    
    return render(request, 'indicator_aggregate.html', {
        'aggregated_data': aggregated_data,
        'indicator_types': indicator_types_list,
        'type_stats': type_stats,
        'days': days,
        'start_date': start_date,
        'end_date': end_date
    })


# ====================
# Data Updates Views
# ====================

class CachedOutput(StringIO):
    """Custom output stream that writes to cache for real-time progress updates."""
    def __init__(self, cache_key):
        super().__init__()
        self.cache_key = cache_key
        cache.set(cache_key, {'output': '', 'status': 'running', 'progress': 0}, timeout=3600)
    
    def write(self, s):
        super().write(s)
        # Update cache with new output
        data = cache.get(self.cache_key, {})
        data['output'] = self.getvalue()
        cache.set(self.cache_key, data, timeout=3600)
        return len(s)


def run_command_in_background(command_name, task_id):
    """Run a Django management command in the background."""
    try:
        output = CachedOutput(f'update_task_{task_id}')
        call_command(command_name, stdout=output, stderr=output)
        
        # Mark as complete
        data = cache.get(f'update_task_{task_id}', {})
        data['status'] = 'completed'
        data['progress'] = 100
        cache.set(f'update_task_{task_id}', data, timeout=3600)
    except Exception as e:
        # Mark as failed
        data = cache.get(f'update_task_{task_id}', {})
        data['status'] = 'failed'
        data['error'] = str(e)
        cache.set(f'update_task_{task_id}', data, timeout=3600)


def data_updates(request):
    """Display data updates page with options to run update scripts."""
    return render(request, 'data_updates.html')


def run_update(request, update_type):
    """Run data update scripts or management commands."""
    if request.method != 'POST':
        return redirect('data_updates')
    
    # Get the project root directory for legacy scripts
    django_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(django_app_dir)
    
    # Map update types to either Django management commands or legacy scripts
    update_config = {
        'ticker_data': {'type': 'command', 'name': 'update_ticker_data', 'display': 'Ticker Data Update'},
        'tickers': {'type': 'command', 'name': 'update_tickers', 'display': 'Ticker List Update'},
        'coingecko': {'type': 'command', 'name': 'update_market_cap', 'display': 'CoinGecko Market Caps Update'}
    }
    
    if update_type not in update_config:
        messages.error(request, f'Invalid update type: {update_type}')
        return redirect('data_updates')
    
    config = update_config[update_type]
    
    try:
        if config['type'] == 'command':
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            
            # Start command in background thread
            thread = threading.Thread(
                target=run_command_in_background,
                args=(config['name'], task_id)
            )
            thread.daemon = True
            thread.start()
            
            # Redirect to progress page
            return redirect('update_progress', task_id=task_id, update_name=config['display'])
        else:
            # Run as legacy script (synchronous for now)
            script_name = config['name']
            script_path = os.path.join(project_root, script_name)
            
            if not os.path.exists(script_path):
                error_msg = f'Update script not found: {script_name}'
                messages.error(request, error_msg)
                raise FileNotFoundError(error_msg)
            
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=600,
                check=True
            )
            
            messages.success(request, f'Successfully ran {script_name}!')
            if result.stdout:
                # Show full output, not truncated
                for line in result.stdout.split('\n')[:50]:  # Show first 50 lines
                    if line.strip():
                        messages.info(request, line)
            return redirect('data_updates')
    
    except subprocess.TimeoutExpired as e:
        error_msg = f'Update script timed out after 10 minutes'
        messages.error(request, error_msg)
        raise subprocess.TimeoutExpired(e.cmd, e.timeout, output=e.output, stderr=e.stderr) from e
    
    except subprocess.CalledProcessError as e:
        error_msg = f'Update script failed with exit code {e.returncode}'
        messages.error(request, error_msg)
        if e.stderr:
            messages.error(request, f'Error output: {e.stderr[:500]}')
        raise subprocess.CalledProcessError(e.returncode, e.cmd, output=e.output, stderr=e.stderr) from e
    
    except Exception as e:
        error_msg = f'Unexpected error running update: {str(e)}'
        messages.error(request, error_msg)
        raise RuntimeError(error_msg) from e


def update_progress(request, task_id, update_name):
    """Display progress page for running update task."""
    return render(request, 'update_progress.html', {
        'task_id': task_id,
        'update_name': update_name
    })


def update_status(request, task_id):
    """API endpoint to check update task status."""
    data = cache.get(f'update_task_{task_id}')
    
    if not data:
        return JsonResponse({
            'status': 'not_found',
            'output': 'Task not found',
            'progress': 0
        })
    
    return JsonResponse(data)
