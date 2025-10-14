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
from models import Ticker, TickerData, Indicator, IndicatorData, Base
from datetime import datetime

app = Flask(__name__)

def load_config(path='../config/settings.json'):
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
            Ticker.ticker.in_(
                session.query(TickerData.ticker).distinct()
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
        ).filter(TickerData.ticker == ticker.ticker).first()
        
        if date_range and date_range.start_date:
            ticker_data_ranges[ticker.ticker] = {
                'start_date': date_range.start_date,
                'end_date': date_range.end_date
            }
    
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
                         ticker_data_ranges=ticker_data_ranges)

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
        TickerData.ticker == ticker_symbol,
        TickerData.date >= start_date
    ).order_by(TickerData.date.asc()).all()
    
    # Get all available data for date range info
    all_data_info = session.query(
        func.min(TickerData.date).label('first_date'),
        func.max(TickerData.date).label('last_date'),
        func.count(TickerData.id).label('total_records')
    ).filter(TickerData.ticker == ticker_symbol).first()
    
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
        # Get current price (most recent)
        current_data = session.query(TickerData).filter(
            TickerData.ticker == ticker.ticker
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
            
            # Get price from that date (or closest available)
            historical_data = session.query(TickerData).filter(
                TickerData.ticker == ticker.ticker,
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

@app.route('/indicators')
def indicators():
    """Display all indicators."""
    session = get_db_session()
    
    indicators = session.query(Indicator).order_by(Indicator.created_at.desc()).all()
    
    session.close()
    
    return render_template('indicators.html', indicators=indicators)

@app.route('/indicators/create', methods=['GET', 'POST'])
def indicator_create():
    """Create a new indicator."""
    if request.method == 'POST':
        session = get_db_session()
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            flash('Title is required', 'danger')
            return render_template('indicator_form.html', mode='create', indicator=None)
        
        try:
            indicator = Indicator(
                title=title,
                description=description,
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
    
    return render_template('indicator_form.html', mode='create', indicator=None)

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
        
        if not title:
            flash('Title is required', 'danger')
            return render_template('indicator_form.html', mode='edit', indicator=indicator)
        
        try:
            indicator.title = title
            indicator.description = description
            indicator.updated_at = datetime.now().isoformat()
            
            session.commit()
            
            flash(f'Indicator "{title}" updated successfully', 'success')
            return redirect(url_for('indicators'))
            
        except Exception as e:
            session.rollback()
            flash(f'Error updating indicator: {str(e)}', 'danger')
        finally:
            session.close()
    
    return render_template('indicator_form.html', mode='edit', indicator=indicator)

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

if __name__ == '__main__':
    config = load_config()
    flask_config = config.get('flask', {})
    
    app.config['SECRET_KEY'] = flask_config.get('secret_key', 'dev-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'
    debug = flask_config.get('debug', True)
    host = flask_config.get('host', '127.0.0.1')
    port = flask_config.get('port', 5000)
    
    app.run(debug=debug, host=host, port=port)
