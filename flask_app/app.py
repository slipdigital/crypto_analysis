"""
Flask application to display cryptocurrency tickers alphabetically.
"""
import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Ticker, TickerData, Indicator, IndicatorData, IndicatorType, Base
from datetime import datetime, timedelta

app = Flask(__name__)

def load_config(path='config/settings.json'):
    config_path = os.path.join(os.path.dirname(__file__), path)
    with open(config_path, 'r') as f:
        return json.load(f)

def get_db_session():
    config = load_config()
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    engine = create_engine(db_url)
    return sessionmaker(bind=engine)()

@app.route('/')
def index():
    """Display all tickers alphabetically."""
    session = get_db_session()
    
    # Get query parameters for filtering
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    usd_only = request.args.get('usd_only', 'true').lower() == 'true'
    has_data_only = request.args.get('has_data_only', 'true').lower() == 'true'
    favorites_only = request.args.get('favorites_only', 'false').lower() == 'true'
    search = request.args.get('search', '').strip()
    
    # Build query
    query = session.query(Ticker).order_by(Ticker.market_cap.desc().nullslast(), Ticker.ticker)
    
    if active_only:
        query = query.filter(Ticker.active == True)
    
    if usd_only:
        query = query.filter(Ticker.is_usd_pair == True)
    
    if favorites_only:
        query = query.filter(Ticker.is_favorite == True)
    
    if has_data_only:
        # Only show tickers that have data in ticker_data
        query = query.filter(
            Ticker.id.in_(
                session.query(TickerData.ticker_id).distinct()
            )
        )
    
    if search:
        query = query.filter(
            (Ticker.ticker.ilike(f'%{search}%')) | 
            (Ticker.name.ilike(f'%{search}%')) |
            (Ticker.crypto_symbol.ilike(f'%{search}%'))
        )
    
    tickers = query.all()
    
    # Get date ranges for each ticker from ticker_data
    ticker_data_ranges = {}
    for ticker in tickers:
        date_range = session.query(
            func.min(TickerData.date).label('start_date'),
            func.max(TickerData.date).label('end_date')
        ).filter(TickerData.ticker_id == ticker.id).first()
        
        if date_range and date_range.start_date:
            ticker_data_ranges[ticker.ticker] = {
                'start_date': date_range.start_date,
                'end_date': date_range.end_date
            }
    
    # Check for outdated data (data older than 2 days)
    today = datetime.now().date()
    threshold_date = today - timedelta(days=2)
    
    # Get favorite ticker symbols for filtering
    favorite_ticker_symbols = set(
        ticker.ticker for ticker in tickers if ticker.is_favorite
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
    favorites_count = session.query(Ticker).filter(Ticker.is_favorite == True).count()
    
    session.close()
    
    return render_template('tickers.html', 
                         tickers=tickers, 
                         active_only=active_only,
                         usd_only=usd_only,
                         has_data_only=has_data_only,
                         favorites_only=favorites_only,
                         search=search,
                         total_count=len(tickers),
                         favorites_count=favorites_count,
                         ticker_data_ranges=ticker_data_ranges,
                         outdated_tickers=outdated_tickers,
                         today=today)

@app.route('/ticker/<ticker_symbol>')
def ticker_detail(ticker_symbol):
    """Display detailed information for a specific ticker."""
    session = get_db_session()
    ticker = session.query(Ticker).filter_by(ticker=ticker_symbol).first()
    
    if not ticker:
        return "Ticker not found", 404
    
    return render_template('ticker_detail.html', ticker=ticker)

@app.route('/ticker/<ticker_symbol>/chart')
def ticker_chart(ticker_symbol):
    """Display stock-style chart for a specific ticker."""
    from datetime import datetime, timedelta
    
    session = get_db_session()
    ticker = session.query(Ticker).filter_by(ticker=ticker_symbol).first()
    
    if not ticker:
        return "Ticker not found", 404
    
    # Get time range from query params (default to 90 days)
    days = request.args.get('days', '90')
    try:
        days = int(days)
    except ValueError:
        days = 90
    
    # Get historical data
    start_date = datetime.now().date() - timedelta(days=days)
    
    ticker_data = session.query(TickerData).filter(
        TickerData.ticker_id == ticker.id,
        TickerData.date >= start_date
    ).order_by(TickerData.date.asc()).all()
    
    # Get all available data for date range info
    all_data_info = session.query(
        func.min(TickerData.date).label('first_date'),
        func.max(TickerData.date).label('last_date'),
        func.count(TickerData.id).label('total_records')
    ).filter(TickerData.ticker_id == ticker.id).first()
    
    return render_template('ticker_chart.html', 
                         ticker=ticker, 
                         ticker_data=ticker_data,
                         days=days,
                         all_data_info=all_data_info)

@app.route('/ticker/<ticker_symbol>/toggle_favorite', methods=['POST'])
def toggle_favorite(ticker_symbol):
    """Toggle favorite status for a ticker."""
    session = get_db_session()
    ticker = session.query(Ticker).filter_by(ticker=ticker_symbol).first()
    
    if not ticker:
        return "Ticker not found", 404
    
    # Toggle favorite status
    ticker.is_favorite = not (ticker.is_favorite or False)
    
    try:
        session.commit()
        status = "added to" if ticker.is_favorite else "removed from"
        flash(f'{ticker_symbol} {status} favorites', 'success')
    except Exception as e:
        session.rollback()
        flash(f'Error updating favorite: {str(e)}', 'danger')
    finally:
        session.close()
    
    # Redirect back to the page that made the request
    return redirect(request.referrer or url_for('index'))

@app.route('/ticker/<ticker_symbol>/edit', methods=['GET', 'POST'])
def ticker_edit(ticker_symbol):
    """Edit ticker market cap."""
    session = get_db_session()
    ticker = session.query(Ticker).filter_by(ticker=ticker_symbol).first()
    
    if not ticker:
        return "Ticker not found", 404
    
    if request.method == 'POST':
        try:
            market_cap_value = request.form.get('market_cap', '').strip()
            
            if market_cap_value:
                ticker.market_cap = float(market_cap_value)
            else:
                ticker.market_cap = None
            
            session.commit()
            flash(f'Market cap updated successfully for {ticker_symbol}', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Invalid market cap value. Please enter a valid number.', 'danger')
        except Exception as e:
            session.rollback()
            flash(f'Error updating market cap: {str(e)}', 'danger')
    
    return render_template('ticker_edit.html', ticker=ticker)

@app.route('/charts')
def charts():
    """Display charts page with links to different chart types."""
    return render_template('charts.html')

@app.route('/charts/compare')
def charts_compare():
    """Display relative strength comparison between two tickers."""
    session = get_db_session()
    
    # Get all active tickers for dropdown, ordered by market cap (descending)
    tickers = session.query(Ticker).filter(
        Ticker.active == True
    ).order_by(Ticker.market_cap.desc().nullslast(), Ticker.ticker).all()
    
    ticker1_symbol = request.args.get('ticker1')
    ticker2_symbol = request.args.get('ticker2')
    days = request.args.get('days', '90')
    
    try:
        days = int(days)
    except ValueError:
        days = 90
    
    chart_data = None
    ticker1 = None
    ticker2 = None
    
    if ticker1_symbol and ticker2_symbol:
        # Get ticker objects
        ticker1 = session.query(Ticker).filter_by(ticker=ticker1_symbol).first()
        ticker2 = session.query(Ticker).filter_by(ticker=ticker2_symbol).first()
        
        if ticker1 and ticker2:
            from datetime import timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get price data for both tickers using ticker_id
            data1 = session.query(TickerData).filter(
                TickerData.ticker_id == ticker1.id,
                TickerData.date >= start_date,
                TickerData.date <= end_date
            ).order_by(TickerData.date).all()
            
            data2 = session.query(TickerData).filter(
                TickerData.ticker_id == ticker2.id,
                TickerData.date >= start_date,
                TickerData.date <= end_date
            ).order_by(TickerData.date).all()
            
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
                    
                    chart_data = {
                        'dates': common_dates,
                        'ticker1_prices': [prices1[d] for d in common_dates],
                        'ticker2_prices': [prices2[d] for d in common_dates],
                        'ticker1_indexed': [(prices1[d] / start_price1) * 100 for d in common_dates],
                        'ticker2_indexed': [(prices2[d] / start_price2) * 100 for d in common_dates],
                        'relative_strength': [(prices1[d] / prices2[d]) for d in common_dates],
                        'rs_normalized': [((prices1[d] / prices2[d]) / (start_price1 / start_price2)) * 100 for d in common_dates]
                    }
                    
                    # Calculate statistics
                    rs_values = chart_data['relative_strength']
                    chart_data['stats'] = {
                        'ticker1_change': ((prices1[common_dates[-1]] / start_price1) - 1) * 100,
                        'ticker2_change': ((prices2[common_dates[-1]] / start_price2) - 1) * 100,
                        'rs_current': rs_values[-1],
                        'rs_start': rs_values[0],
                        'rs_change': ((rs_values[-1] / rs_values[0]) - 1) * 100,
                        'ticker1_outperforming': rs_values[-1] > rs_values[0]
                    }
    
    session.close()
    
    return render_template('charts_compare.html',
                         tickers=tickers,
                         ticker1=ticker1,
                         ticker2=ticker2,
                         chart_data=chart_data,
                         days=days)

@app.route('/charts/top_gainers')
def top_gainers():
    """Display top gainers/losers chart."""
    from datetime import datetime, timedelta
    
    session = get_db_session()
    
    # Get top 30 tickers by market cap
    top_tickers = session.query(Ticker).filter(
        Ticker.market_cap.isnot(None),
        Ticker.active == True
    ).order_by(Ticker.market_cap.desc()).limit(30).all()
    
    # Calculate gains/losses for each ticker
    gains_data = []
    today = datetime.now().date()
    
    for ticker in top_tickers:
        # Get current price (most recent) using ticker_id
        current_data = session.query(TickerData).filter(
            TickerData.ticker_id == ticker.id
        ).order_by(TickerData.date.desc()).first()
        
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
            
            # Get price from that date (or closest available) using ticker_id
            historical_data = session.query(TickerData).filter(
                TickerData.ticker_id == ticker.id,
                TickerData.date <= target_date
            ).order_by(TickerData.date.desc()).first()
            
            if historical_data and historical_data.close:
                old_price = historical_data.close
                change_percent = ((current_price - old_price) / old_price) * 100
                ticker_gains[f'gain_{days}d'] = change_percent
            else:
                ticker_gains[f'gain_{days}d'] = None
        
        gains_data.append(ticker_gains)
    
    return render_template('top_gainers.html', gains_data=gains_data, periods=periods)

# ====================
# Indicator Type Routes
# ====================

@app.route('/indicator-types')
def indicator_types():
    """Display all indicator types."""
    session = get_db_session()
    
    types = session.query(IndicatorType).order_by(IndicatorType.name).all()
    
    # Count indicators for each type
    type_counts = {}
    for ind_type in types:
        count = session.query(Indicator).filter(Indicator.indicator_type_id == ind_type.id).count()
        type_counts[ind_type.id] = count
    
    session.close()
    
    return render_template('indicator_types.html', types=types, type_counts=type_counts)

@app.route('/indicator-types/create', methods=['GET', 'POST'])
def indicator_type_create():
    """Create a new indicator type."""
    if request.method == 'POST':
        session = get_db_session()
        
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#6B7280').strip()
        
        if not name:
            flash('Name is required!', 'danger')
            return redirect(url_for('indicator_type_create'))
        
        # Check if name already exists
        existing = session.query(IndicatorType).filter_by(name=name).first()
        if existing:
            flash(f'Indicator type "{name}" already exists!', 'danger')
            session.close()
            return redirect(url_for('indicator_type_create'))
        
        # Create new indicator type
        new_type = IndicatorType(
            name=name,
            description=description,
            color=color,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        session.add(new_type)
        session.commit()
        session.close()
        
        flash(f'Indicator type "{name}" created successfully!', 'success')
        return redirect(url_for('indicator_types'))
    
    return render_template('indicator_type_form.html', type=None, action='Create')

@app.route('/indicator-types/<int:type_id>/edit', methods=['GET', 'POST'])
def indicator_type_edit(type_id):
    """Edit an existing indicator type."""
    session = get_db_session()
    
    ind_type = session.query(IndicatorType).get(type_id)
    
    if not ind_type:
        flash('Indicator type not found!', 'danger')
        session.close()
        return redirect(url_for('indicator_types'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#6B7280').strip()
        
        if not name:
            flash('Name is required!', 'danger')
            session.close()
            return redirect(url_for('indicator_type_edit', type_id=type_id))
        
        # Check if name already exists (excluding current)
        existing = session.query(IndicatorType).filter(
            IndicatorType.name == name,
            IndicatorType.id != type_id
        ).first()
        
        if existing:
            flash(f'Indicator type "{name}" already exists!', 'danger')
            session.close()
            return redirect(url_for('indicator_type_edit', type_id=type_id))
        
        # Update indicator type
        ind_type.name = name
        ind_type.description = description
        ind_type.color = color
        ind_type.updated_at = datetime.now().isoformat()
        
        session.commit()
        session.close()
        
        flash(f'Indicator type "{name}" updated successfully!', 'success')
        return redirect(url_for('indicator_types'))
    
    session.close()
    return render_template('indicator_type_form.html', type=ind_type, action='Edit')

@app.route('/indicator-types/<int:type_id>/delete', methods=['POST'])
def indicator_type_delete(type_id):
    """Delete an indicator type."""
    session = get_db_session()
    
    ind_type = session.query(IndicatorType).get(type_id)
    
    if not ind_type:
        flash('Indicator type not found!', 'danger')
        session.close()
        return redirect(url_for('indicator_types'))
    
    # Check if any indicators use this type
    indicator_count = session.query(Indicator).filter(Indicator.indicator_type_id == type_id).count()
    
    if indicator_count > 0:
        flash(f'Cannot delete "{ind_type.name}" because {indicator_count} indicator(s) are using it. Please reassign or delete those indicators first.', 'danger')
        session.close()
        return redirect(url_for('indicator_types'))
    
    name = ind_type.name
    session.delete(ind_type)
    session.commit()
    session.close()
    
    flash(f'Indicator type "{name}" deleted successfully!', 'success')
    return redirect(url_for('indicator_types'))

# ====================
# Indicator Routes
# ====================

@app.route('/indicators')
def indicators():
    """Display all indicators."""
    session = get_db_session()
    
    indicators_with_types = []
    indicators = session.query(Indicator).order_by(Indicator.created_at.desc()).all()
    
    for indicator in indicators:
        ind_type = None
        if indicator.indicator_type_id:
            ind_type = session.query(IndicatorType).get(indicator.indicator_type_id)
        indicators_with_types.append({
            'indicator': indicator,
            'type': ind_type
        })
    
    session.close()
    
    return render_template('indicators.html', indicators_with_types=indicators_with_types)

@app.route('/indicators/create', methods=['GET', 'POST'])
def indicator_create():
    """Create a new indicator."""
    session = get_db_session()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        type_id = request.form.get('indicator_type_id')
        
        if type_id:
            type_id = int(type_id)
        else:
            type_id = None
        
        if not title:
            flash('Title is required', 'danger')
            types = session.query(IndicatorType).order_by(IndicatorType.name).all()
            session.close()
            return render_template('indicator_form.html', mode='create', indicator=None, types=types)
        
        try:
            indicator = Indicator(
                title=title,
                description=description,
                url=url if url else None,
                indicator_type_id=type_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            session.add(indicator)
            session.commit()
            
            flash(f'Indicator "{title}" created successfully', 'success')
            return redirect(url_for('indicators'))
            
        except Exception as e:
            session.rollback()
            flash(f'Error creating indicator: {str(e)}', 'danger')
        finally:
            session.close()
    
    types = session.query(IndicatorType).order_by(IndicatorType.name).all()
    session.close()
    return render_template('indicator_form.html', mode='create', indicator=None, types=types)

@app.route('/indicators/<int:indicator_id>/edit', methods=['GET', 'POST'])
def indicator_edit(indicator_id):
    """Edit an existing indicator."""
    session = get_db_session()
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        session.close()
        flash('Indicator not found', 'danger')
        return redirect(url_for('indicators'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        type_id = request.form.get('indicator_type_id')
        
        if type_id:
            type_id = int(type_id)
        else:
            type_id = None
        
        if not title:
            flash('Title is required', 'danger')
            types = session.query(IndicatorType).order_by(IndicatorType.name).all()
            return render_template('indicator_form.html', mode='edit', indicator=indicator, types=types)
        
        try:
            indicator.title = title
            indicator.description = description
            indicator.url = url if url else None
            indicator.indicator_type_id = type_id
            indicator.updated_at = datetime.now().isoformat()
            
            session.commit()
            
            flash(f'Indicator "{title}" updated successfully', 'success')
            return redirect(url_for('indicators'))
            
        except Exception as e:
            session.rollback()
            flash(f'Error updating indicator: {str(e)}', 'danger')
        finally:
            session.close()
    
    types = session.query(IndicatorType).order_by(IndicatorType.name).all()
    session.close()
    return render_template('indicator_form.html', mode='edit', indicator=indicator, types=types)

@app.route('/indicators/<int:indicator_id>/delete', methods=['POST'])
def indicator_delete(indicator_id):
    """Delete an indicator."""
    session = get_db_session()
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        flash('Indicator not found', 'danger')
    else:
        try:
            title = indicator.title
            session.delete(indicator)
            session.commit()
            flash(f'Indicator "{title}" deleted successfully', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Error deleting indicator: {str(e)}', 'danger')
    
    session.close()
    return redirect(url_for('indicators'))

@app.route('/indicators/<int:indicator_id>/data')
def indicator_data_list(indicator_id):
    """View all data points for an indicator."""
    session = get_db_session()
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        flash('Indicator not found', 'danger')
        session.close()
        return redirect(url_for('indicators'))
    
    # Get all data points for this indicator, ordered by date desc
    data_points = session.query(IndicatorData).filter_by(
        indicator_id=indicator_id
    ).order_by(IndicatorData.date.desc()).all()
    
    # Get statistics
    if data_points:
        values = [d.value for d in data_points]
        stats = {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': data_points[0].value if data_points else None,
            'latest_date': data_points[0].date if data_points else None
        }
    else:
        stats = None
    
    session.close()
    
    return render_template('indicator_data.html', 
                         indicator=indicator, 
                         data_points=data_points,
                         stats=stats)

@app.route('/indicators/<int:indicator_id>/data/add', methods=['GET', 'POST'])
def indicator_data_add(indicator_id):
    """Add a new data point to an indicator."""
    session = get_db_session()
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        flash('Indicator not found', 'danger')
        session.close()
        return redirect(url_for('indicators'))
    
    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        value_str = request.form.get('value', '').strip()
        
        if not date_str or not value_str:
            flash('Date and value are required', 'danger')
            return render_template('indicator_data_form.html', 
                                 mode='add', 
                                 indicator=indicator, 
                                 data_point=None,
                                 today=datetime.now().date().isoformat())
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse and validate value
            value = float(value_str)
            if value < -1.0 or value > 1.0:
                flash('Value must be between -1.0 and 1.0', 'danger')
                return render_template('indicator_data_form.html', 
                                     mode='add', 
                                     indicator=indicator, 
                                     data_point=None,
                                     today=datetime.now().date().isoformat())
            
            # Check if data point already exists for this date
            existing = session.query(IndicatorData).filter_by(
                indicator_id=indicator_id,
                date=date_obj
            ).first()
            
            if existing:
                flash(f'Data point for {date_str} already exists. Use edit to update it.', 'warning')
                return render_template('indicator_data_form.html', 
                                     mode='add', 
                                     indicator=indicator, 
                                     data_point=None,
                                     today=datetime.now().date().isoformat())
            
            # Create new data point
            data_point = IndicatorData(
                indicator_id=indicator_id,
                date=date_obj,
                value=value,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            session.add(data_point)
            session.commit()
            
            flash(f'Data point added for {date_str}', 'success')
            return redirect(url_for('indicator_data_list', indicator_id=indicator_id))
            
        except ValueError as e:
            flash(f'Invalid date or value format: {str(e)}', 'danger')
        except Exception as e:
            session.rollback()
            flash(f'Error adding data point: {str(e)}', 'danger')
        finally:
            session.close()
    
    return render_template('indicator_data_form.html', 
                         mode='add', 
                         indicator=indicator, 
                         data_point=None,
                         today=datetime.now().date().isoformat())

@app.route('/indicators/<int:indicator_id>/data/<int:data_id>/edit', methods=['GET', 'POST'])
def indicator_data_edit(indicator_id, data_id):
    """Edit an existing data point."""
    session = get_db_session()
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        flash('Indicator not found', 'danger')
        session.close()
        return redirect(url_for('indicators'))
    
    data_point = session.query(IndicatorData).filter_by(
        id=data_id,
        indicator_id=indicator_id
    ).first()
    
    if not data_point:
        flash('Data point not found', 'danger')
        session.close()
        return redirect(url_for('indicator_data_list', indicator_id=indicator_id))
    
    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        value_str = request.form.get('value', '').strip()
        
        if not date_str or not value_str:
            flash('Date and value are required', 'danger')
            return render_template('indicator_data_form.html', 
                                 mode='edit', 
                                 indicator=indicator, 
                                 data_point=data_point,
                                 today=datetime.now().date().isoformat())
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Parse and validate value
            value = float(value_str)
            if value < -1.0 or value > 1.0:
                flash('Value must be between -1.0 and 1.0', 'danger')
                return render_template('indicator_data_form.html', 
                                     mode='edit', 
                                     indicator=indicator, 
                                     data_point=data_point,
                                     today=datetime.now().date().isoformat())
            
            # Check if another data point exists for this date (excluding current)
            existing = session.query(IndicatorData).filter(
                IndicatorData.indicator_id == indicator_id,
                IndicatorData.date == date_obj,
                IndicatorData.id != data_id
            ).first()
            
            if existing:
                flash(f'Another data point for {date_str} already exists', 'warning')
                return render_template('indicator_data_form.html', 
                                     mode='edit', 
                                     indicator=indicator, 
                                     data_point=data_point,
                                     today=datetime.now().date().isoformat())
            
            # Update data point
            data_point.date = date_obj
            data_point.value = value
            data_point.updated_at = datetime.now().isoformat()
            
            session.commit()
            
            flash(f'Data point updated for {date_str}', 'success')
            return redirect(url_for('indicator_data_list', indicator_id=indicator_id))
            
        except ValueError as e:
            flash(f'Invalid date or value format: {str(e)}', 'danger')
        except Exception as e:
            session.rollback()
            flash(f'Error updating data point: {str(e)}', 'danger')
        finally:
            session.close()
    
    return render_template('indicator_data_form.html', 
                         mode='edit', 
                         indicator=indicator, 
                         data_point=data_point,
                         today=datetime.now().date().isoformat())

@app.route('/indicators/<int:indicator_id>/data/<int:data_id>/delete', methods=['POST'])
def indicator_data_delete(indicator_id, data_id):
    """Delete a data point."""
    session = get_db_session()
    
    data_point = session.query(IndicatorData).filter_by(
        id=data_id,
        indicator_id=indicator_id
    ).first()
    
    if not data_point:
        flash('Data point not found', 'danger')
    else:
        try:
            date_str = str(data_point.date)
            session.delete(data_point)
            session.commit()
            flash(f'Data point for {date_str} deleted successfully', 'success')
        except Exception as e:
            session.rollback()
            flash(f'Error deleting data point: {str(e)}', 'danger')
    
    session.close()
    return redirect(url_for('indicator_data_list', indicator_id=indicator_id))

@app.route('/indicators/bulk-entry', methods=['GET', 'POST'])
def indicator_bulk_entry():
    """Add data points for multiple indicators at once."""
    session = get_db_session()
    
    # Get all indicators ordered by title
    indicators = session.query(Indicator).order_by(Indicator.title).all()
    
    if not indicators:
        flash('No indicators found. Create some indicators first.', 'warning')
        session.close()
        return redirect(url_for('indicators'))
    
    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        
        if not date_str:
            flash('Date is required', 'danger')
            return render_template('indicator_bulk_entry.html', 
                                 indicators=indicators,
                                 today=datetime.now().date().isoformat())
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Collect all indicator values from form
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []
            
            for indicator in indicators:
                value_str = request.form.get(f'value_{indicator.id}', '').strip()
                
                # Skip if no value provided
                if not value_str:
                    skipped_count += 1
                    continue
                
                try:
                    # Parse and validate value
                    value = float(value_str)
                    if value < -1.0 or value > 1.0:
                        errors.append(f'{indicator.title}: Value must be between -1.0 and 1.0')
                        continue
                    
                    # Check if data point already exists for this date
                    existing = session.query(IndicatorData).filter_by(
                        indicator_id=indicator.id,
                        date=date_obj
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.value = value
                        existing.updated_at = datetime.now().isoformat()
                        updated_count += 1
                    else:
                        # Create new data point
                        data_point = IndicatorData(
                            indicator_id=indicator.id,
                            date=date_obj,
                            value=value,
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat()
                        )
                        session.add(data_point)
                        saved_count += 1
                    
                except ValueError:
                    errors.append(f'{indicator.title}: Invalid value "{value_str}"')
                    continue
            
            # Commit all changes
            try:
                session.commit()
                
                # Build success message
                messages = []
                if saved_count > 0:
                    messages.append(f'{saved_count} new data point(s) added')
                if updated_count > 0:
                    messages.append(f'{updated_count} data point(s) updated')
                if skipped_count > 0:
                    messages.append(f'{skipped_count} indicator(s) skipped (no value provided)')
                
                if messages:
                    flash(f'Bulk entry for {date_str}: {", ".join(messages)}', 'success')
                
                # Show errors if any
                if errors:
                    for error in errors:
                        flash(error, 'warning')
                
                # Redirect back to form for another entry
                return redirect(url_for('indicator_bulk_entry'))
                
            except Exception as e:
                session.rollback()
                flash(f'Error saving data: {str(e)}', 'danger')
                
        except ValueError as e:
            flash(f'Invalid date format: {str(e)}', 'danger')
        finally:
            session.close()
    
    session.close()
    
    return render_template('indicator_bulk_entry.html', 
                         indicators=indicators,
                         today=datetime.now().date().isoformat())

@app.route('/indicators/<int:indicator_id>/data/range-entry', methods=['GET', 'POST'])
def indicator_data_range_entry(indicator_id):
    """Add data points for a single indicator across a date range."""
    session = get_db_session()
    
    indicator = session.query(Indicator).filter_by(id=indicator_id).first()
    
    if not indicator:
        flash('Indicator not found', 'danger')
        session.close()
        return redirect(url_for('indicators'))
    
    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        value_str = request.form.get('value', '').strip()
        overwrite_existing = request.form.get('overwrite_existing') == 'on'
        
        if not start_date_str or not end_date_str:
            flash('Both start date and end date are required', 'danger')
            session.close()
            return render_template('indicator_data_range_form.html',
                                 indicator=indicator,
                                 today=datetime.now().date().isoformat())
        
        if not value_str:
            flash('Value is required', 'danger')
            session.close()
            return render_template('indicator_data_range_form.html',
                                 indicator=indicator,
                                 today=datetime.now().date().isoformat())
        
        try:
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if end_date < start_date:
                flash('End date must be after start date', 'danger')
                session.close()
                return render_template('indicator_data_range_form.html',
                                     indicator=indicator,
                                     today=datetime.now().date().isoformat())
            
            # Parse value
            try:
                value = float(value_str)
                if value < -1.0 or value > 1.0:
                    flash('Value must be between -1.0 and 1.0', 'danger')
                    session.close()
                    return render_template('indicator_data_range_form.html',
                                         indicator=indicator,
                                         today=datetime.now().date().isoformat())
            except ValueError:
                flash('Invalid value format. Must be a number between -1.0 and 1.0', 'danger')
                session.close()
                return render_template('indicator_data_range_form.html',
                                     indicator=indicator,
                                     today=datetime.now().date().isoformat())
            
            # Generate list of dates
            from datetime import timedelta
            current_date = start_date
            dates_to_process = []
            
            while current_date <= end_date:
                dates_to_process.append(current_date)
                current_date += timedelta(days=1)
            
            if not dates_to_process:
                flash('No dates to process (all dates were filtered out)', 'warning')
                session.close()
                return render_template('indicator_data_range_form.html',
                                     indicator=indicator,
                                     today=datetime.now().date().isoformat())
            
            # Process each date
            added_count = 0
            updated_count = 0
            skipped_count = 0
            
            for date in dates_to_process:
                # Check if data already exists
                existing = session.query(IndicatorData).filter_by(
                    indicator_id=indicator_id,
                    date=date
                ).first()
                
                if existing:
                    if overwrite_existing:
                        existing.value = value
                        existing.updated_at = datetime.now().isoformat()
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Create new data point
                    data_point = IndicatorData(
                        indicator_id=indicator_id,
                        date=date,
                        value=value,
                        created_at=datetime.now().isoformat(),
                        updated_at=datetime.now().isoformat()
                    )
                    session.add(data_point)
                    added_count += 1
            
            session.commit()
            
            # Build success message
            messages = []
            if added_count > 0:
                messages.append(f'{added_count} new data point(s) added')
            if updated_count > 0:
                messages.append(f'{updated_count} data point(s) updated')
            if skipped_count > 0:
                messages.append(f'{skipped_count} existing data point(s) skipped')
            
            flash(f'Date range entry completed: {", ".join(messages)}', 'success')
            session.close()
            return redirect(url_for('indicator_data_list', indicator_id=indicator_id))
            
        except ValueError as e:
            flash(f'Invalid date format: {str(e)}', 'danger')
            session.close()
        except Exception as e:
            session.rollback()
            flash(f'Error saving data: {str(e)}', 'danger')
            session.close()
    
    session.close()
    return render_template('indicator_data_range_form.html',
                         indicator=indicator,
                         today=datetime.now().date().isoformat())

@app.route('/indicators/aggregate')
def indicator_aggregate():
    """Display aggregated indicator data by type and date."""
    session = get_db_session()
    
    # Get filter parameters
    days = request.args.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    # Calculate date range
    from datetime import timedelta
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get all indicator types
    indicator_types = session.query(IndicatorType).order_by(IndicatorType.name).all()
    
    # Get all indicators with their types
    indicators = session.query(Indicator).all()
    
    # Create a mapping of indicator_id to type
    indicator_type_map = {}
    for indicator in indicators:
        indicator_type_map[indicator.id] = indicator.indicator_type_id
    
    # Query all indicator data within date range
    data_query = session.query(
        IndicatorData.date,
        IndicatorData.indicator_id,
        IndicatorData.value
    ).filter(
        IndicatorData.date >= start_date,
        IndicatorData.date <= end_date
    ).order_by(IndicatorData.date.desc()).all()
    
    # Organize data by date
    daily_data = {}
    for data_point in data_query:
        date_str = str(data_point.date)
        if date_str not in daily_data:
            daily_data[date_str] = {
                'date': data_point.date,
                'by_type': {},
                'overall': []
            }
        
        # Get the type for this indicator
        type_id = indicator_type_map.get(data_point.indicator_id)
        
        if type_id:
            if type_id not in daily_data[date_str]['by_type']:
                daily_data[date_str]['by_type'][type_id] = []
            daily_data[date_str]['by_type'][type_id].append(data_point.value)
        
        # Add to overall
        daily_data[date_str]['overall'].append(data_point.value)
    
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
    for ind_type in indicator_types:
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
    
    session.close()
    
    return render_template('indicator_aggregate.html',
                         aggregated_data=aggregated_data,
                         indicator_types=indicator_types,
                         type_stats=type_stats,
                         days=days,
                         start_date=start_date,
                         end_date=end_date)

if __name__ == '__main__':
    config = load_config()
    flask_config = config.get('flask', {})
    
    app.config['SECRET_KEY'] = flask_config.get('secret_key', 'dev-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'
    debug = flask_config.get('debug', True)
    host = flask_config.get('host', '127.0.0.1')
    port = flask_config.get('port', 5000)
    
    app.run(debug=debug, host=host, port=port)
