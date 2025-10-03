"""
Flask Crypto Dashboard Application
Main application file for the cryptocurrency analysis dashboard
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from services.data_service import CryptoDataService
from services.chart_service import ChartService
from services.market_service import MarketService
from celery_config import celery_app
import tasks

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_path = "config/settings.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Flask configuration
    app.config['SECRET_KEY'] = config.get('flask', {}).get('secret_key', 'dev-secret-key')
    app.config['DEBUG'] = config.get('flask', {}).get('debug', True)
    
    # Enable CORS for API endpoints
    CORS(app)
    
    # Initialize services
    data_service = CryptoDataService(config_path)
    chart_service = ChartService(config_path)
    market_service = MarketService(config_path)
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        try:
            # Get summary data for the dashboard
            market_summary = market_service.get_market_summary()
            top_performers = market_service.get_top_performers(limit=5)
            
            return render_template('dashboard.html', 
                                 market_summary=market_summary,
                                 top_performers=top_performers)
        except Exception as e:
            app.logger.error(f"Error loading dashboard: {e}")
            return render_template('dashboard.html', 
                                 market_summary={},
                                 top_performers=[],
                                 error="Unable to load market data")
    
    @app.route('/market-cap')
    def market_cap():
        """Market cap rankings page"""
        return render_template('market_cap.html')
    
    @app.route('/charts')
    def charts():
        """Price charts page"""
        available_cryptos = data_service.get_available_cryptocurrencies()
        return render_template('charts.html', cryptocurrencies=available_cryptos)
    
    @app.route('/performance')
    def performance():
        """Performance analysis page"""
        return render_template('performance.html')
    
    # API Routes
    @app.route('/api/market-cap')
    def api_market_cap():
        """API endpoint for market cap data"""
        try:
            data = market_service.get_market_cap_data()
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in market cap API: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/historical/<symbol>')
    def api_historical(symbol):
        """API endpoint for historical price data"""
        try:
            period = request.args.get('period', '30d')
            data = chart_service.get_historical_data(symbol, period)
            return jsonify({
                'success': True,
                'data': data,
                'symbol': symbol,
                'period': period,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in historical data API: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/performance')
    def api_performance():
        """API endpoint for performance metrics"""
        try:
            data = market_service.get_performance_data()
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in performance API: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/chart-data/<symbol>')
    def api_chart_data(symbol):
        """API endpoint for chart data"""
        try:
            chart_type = request.args.get('type', 'line')
            period = request.args.get('period', '30d')
            data = chart_service.get_chart_data(symbol, chart_type, period)
            return jsonify({
                'success': True,
                'data': data,
                'symbol': symbol,
                'type': chart_type,
                'period': period,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in chart data API: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/summary')
    def api_summary():
        """API endpoint for dashboard summary data"""
        try:
            summary = {
                'market_summary': market_service.get_market_summary(),
                'top_performers': market_service.get_top_performers(limit=10),
                'available_cryptos': data_service.get_available_cryptocurrencies(),
                'last_updated': data_service.get_last_update_time()
            }
            return jsonify({
                'success': True,
                'data': summary,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in summary API: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Celery Background Task Routes
    @app.route('/api/run-backtest', methods=['POST'])
    def run_backtest():
        """Start a Celery background backtest task"""
        try:
            # Get optional parameters from request
            options = request.get_json() if request.is_json else {}
            
            # Start Celery task
            task = tasks.run_crypto_backtest.delay(options)
            
            return jsonify({
                'success': True,
                'task_id': task.id,
                'message': 'Backtest started successfully',
                'status_url': f'/api/task-status/{task.id}'
            })
            
        except Exception as e:
            app.logger.error(f"Error starting backtest: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/run-data-collection', methods=['POST'])
    def run_data_collection():
        """Start a Celery data collection task"""
        try:
            # Get optional parameters from request
            data = request.get_json() if request.is_json else {}
            force_update = data.get('force_update', False)
            
            # Start Celery task
            task = tasks.run_data_collection.delay(force_update)
            
            return jsonify({
                'success': True,
                'task_id': task.id,
                'message': 'Data collection started successfully',
                'status_url': f'/api/task-status/{task.id}'
            })
            
        except Exception as e:
            app.logger.error(f"Error starting data collection: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/generate-reports', methods=['POST'])
    def generate_reports():
        """Start a Celery report generation task"""
        try:
            # Get optional parameters from request
            data = request.get_json() if request.is_json else {}
            report_types = data.get('report_types', ['market_cap', 'performance'])
            
            # Start Celery task
            task = tasks.generate_reports.delay(report_types)
            
            return jsonify({
                'success': True,
                'task_id': task.id,
                'message': 'Report generation started successfully',
                'status_url': f'/api/task-status/{task.id}'
            })
            
        except Exception as e:
            app.logger.error(f"Error starting report generation: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/task-status/<task_id>')
    def get_task_status(task_id):
        """Get the status of a Celery task"""
        try:
            # Get task result from Celery
            task_result = celery_app.AsyncResult(task_id)
            
            if task_result.state == 'PENDING':
                # Task is waiting to be processed
                response = {
                    'id': task_id,
                    'status': 'pending',
                    'progress': 0,
                    'message': 'Task is pending...',
                    'start_time': None,
                    'end_time': None,
                    'results': None,
                    'error': None
                }
            elif task_result.state == 'PROGRESS':
                # Task is currently running
                response = {
                    'id': task_id,
                    'status': 'running',
                    'progress': task_result.info.get('current', 0),
                    'total': task_result.info.get('total', 100),
                    'message': task_result.info.get('status', 'Running...'),
                    'start_time': task_result.info.get('start_time'),
                    'end_time': None,
                    'results': None,
                    'error': None
                }
            elif task_result.state == 'SUCCESS':
                # Task completed successfully
                result = task_result.result
                response = {
                    'id': task_id,
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Task completed successfully',
                    'start_time': result.get('execution_time'),
                    'end_time': result.get('execution_time'),
                    'results': result,
                    'error': None
                }
            else:
                # Task failed
                response = {
                    'id': task_id,
                    'status': 'failed',
                    'progress': 100,
                    'message': 'Task failed',
                    'start_time': None,
                    'end_time': datetime.now().isoformat(),
                    'results': None,
                    'error': str(task_result.info) if task_result.info else 'Unknown error'
                }
            
            return jsonify({
                'success': True,
                'task': response
            })
                
        except Exception as e:
            app.logger.error(f"Error getting task status: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/tasks')
    def list_tasks():
        """List active Celery tasks"""
        try:
            # Get active tasks from Celery
            active_tasks = celery_app.control.inspect().active()
            scheduled_tasks = celery_app.control.inspect().scheduled()
            
            all_tasks = []
            
            # Process active tasks
            if active_tasks:
                for worker, tasks_list in active_tasks.items():
                    for task_info in tasks_list:
                        all_tasks.append({
                            'id': task_info['id'],
                            'name': task_info['name'],
                            'status': 'running',
                            'worker': worker,
                            'start_time': task_info.get('time_start'),
                            'args': task_info.get('args', []),
                            'kwargs': task_info.get('kwargs', {})
                        })
            
            # Process scheduled tasks
            if scheduled_tasks:
                for worker, tasks_list in scheduled_tasks.items():
                    for task_info in tasks_list:
                        all_tasks.append({
                            'id': task_info['request']['id'],
                            'name': task_info['request']['task'],
                            'status': 'scheduled',
                            'worker': worker,
                            'eta': task_info.get('eta'),
                            'args': task_info['request'].get('args', []),
                            'kwargs': task_info['request'].get('kwargs', {})
                        })
            
            return jsonify({
                'success': True,
                'tasks': all_tasks[-10:],  # Return last 10 tasks
                'total_active': len([t for t in all_tasks if t['status'] == 'running']),
                'total_scheduled': len([t for t in all_tasks if t['status'] == 'scheduled'])
            })
            
        except Exception as e:
            app.logger.error(f"Error listing tasks: {e}")
            return jsonify({
                'success': True,
                'tasks': [],
                'total_active': 0,
                'total_scheduled': 0,
                'error': f'Could not connect to Celery workers: {str(e)}'
            })
    
    @app.route('/api/cancel-task/<task_id>', methods=['POST'])
    def cancel_task(task_id):
        """Cancel a Celery task"""
        try:
            celery_app.control.revoke(task_id, terminate=True)
            
            return jsonify({
                'success': True,
                'message': f'Task {task_id} has been cancelled'
            })
            
        except Exception as e:
            app.logger.error(f"Error cancelling task: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def create_celery_app(app=None):
    """
    Create Celery app instance with Flask app context
    """
    app = app or create_app()
    
    class ContextTask(celery_app.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    return celery_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)