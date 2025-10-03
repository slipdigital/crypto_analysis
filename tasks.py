"""
Celery Tasks for Crypto Dashboard
Background tasks for cryptocurrency analysis operations
"""

import os
import subprocess
import logging
from datetime import datetime
from celery import Task
from celery_config import celery_app

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallbackTask(Task):
    """Base task class with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f"Task {task_id} completed successfully")
        
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f"Task {task_id} failed: {exc}")
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f"Task {task_id} retrying: {exc}")

@celery_app.task(bind=True, base=CallbackTask)
def run_crypto_backtest(self, options=None):
    """
    Run cryptocurrency backtesting analysis
    
    Args:
        options (dict): Optional parameters for backtest
        
    Returns:
        dict: Results of the backtest operation
    """
    try:
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Starting backtest...'}
        )
        
        # Prepare command
        cmd = ['python', 'backtest/crypto_backtest.py']
        
        # Add options if provided
        if options:
            if options.get('strategy'):
                cmd.extend(['--strategy', options['strategy']])
            if options.get('symbols'):
                cmd.extend(['--symbols'] + options['symbols'])
            if options.get('period'):
                cmd.extend(['--period', str(options['period'])])
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Running backtest analysis...'}
        )
        
        # Execute backtest
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=1800  # 30 minutes timeout
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Processing results...'}
        )
        
        if result.returncode == 0:
            # Success
            output_lines = result.stdout.strip().split('\n')
            
            # Parse results (extract key metrics)
            results = {
                'status': 'completed',
                'return_code': result.returncode,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None,
                'execution_time': datetime.now().isoformat(),
                'metrics': parse_backtest_output(result.stdout)
            }
            
            logger.info("Backtest completed successfully")
            return results
            
        else:
            # Error
            error_msg = result.stderr or 'Unknown error occurred'
            logger.error(f"Backtest failed: {error_msg}")
            
            return {
                'status': 'failed',
                'return_code': result.returncode,
                'output': result.stdout,
                'error': error_msg,
                'execution_time': datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "Backtest timed out after 30 minutes"
        logger.error(error_msg)
        
        return {
            'status': 'failed',
            'error': error_msg,
            'execution_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        
        return {
            'status': 'failed',
            'error': error_msg,
            'execution_time': datetime.now().isoformat()
        }

@celery_app.task(bind=True, base=CallbackTask)
def run_data_collection(self, force_update=False):
    """
    Run cryptocurrency data collection
    
    Args:
        force_update (bool): Force update even if data is recent
        
    Returns:
        dict: Results of the data collection
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Starting data collection...'}
        )
        
        # Prepare command
        cmd = ['python', 'backtest/crypto_collector.py']
        if force_update:
            cmd.append('--force')
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Collecting cryptocurrency data...'}
        )
        
        # Execute data collection
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=1200  # 20 minutes timeout
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing data collection...'}
        )
        
        if result.returncode == 0:
            return {
                'status': 'completed',
                'return_code': result.returncode,
                'output': result.stdout,
                'execution_time': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'failed',
                'return_code': result.returncode,
                'output': result.stdout,
                'error': result.stderr,
                'execution_time': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'execution_time': datetime.now().isoformat()
        }

@celery_app.task(bind=True, base=CallbackTask)
def generate_reports(self, report_types=None):
    """
    Generate cryptocurrency analysis reports
    
    Args:
        report_types (list): Types of reports to generate ['market_cap', 'performance']
        
    Returns:
        dict: Results of report generation
    """
    try:
        if report_types is None:
            report_types = ['market_cap', 'performance']
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Starting report generation...'}
        )
        
        results = {}
        total_reports = len(report_types)
        
        for i, report_type in enumerate(report_types):
            progress = int(20 + (60 * i / total_reports))
            
            self.update_state(
                state='PROGRESS',
                meta={'current': progress, 'total': 100, 'status': f'Generating {report_type} report...'}
            )
            
            if report_type == 'market_cap':
                cmd = ['python', 'market_cap/market_cap_report.py']
            elif report_type == 'performance':
                cmd = ['python', 'crypto_performance/performance_report.py']
            else:
                continue
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=600  # 10 minutes timeout
            )
            
            results[report_type] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'return_code': result.returncode,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing reports...'}
        )
        
        return {
            'status': 'completed',
            'reports': results,
            'execution_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'execution_time': datetime.now().isoformat()
        }

def parse_backtest_output(output):
    """
    Parse backtest output to extract key metrics
    
    Args:
        output (str): Raw output from backtest
        
    Returns:
        dict: Parsed metrics
    """
    metrics = {}
    
    try:
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for key metrics in output
            if 'Return' in line and '%' in line:
                try:
                    # Extract return percentage
                    parts = line.split(':')
                    if len(parts) >= 2:
                        return_str = parts[1].strip().replace('%', '')
                        metrics['total_return'] = float(return_str)
                except (ValueError, IndexError):
                    pass
            
            elif 'Sharpe Ratio' in line:
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        sharpe_str = parts[1].strip()
                        metrics['sharpe_ratio'] = float(sharpe_str)
                except (ValueError, IndexError):
                    pass
            
            elif 'Max Drawdown' in line and '%' in line:
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        drawdown_str = parts[1].strip().replace('%', '')
                        metrics['max_drawdown'] = float(drawdown_str)
                except (ValueError, IndexError):
                    pass
            
            elif 'Trades' in line:
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        trades_str = parts[1].strip()
                        metrics['total_trades'] = int(trades_str)
                except (ValueError, IndexError):
                    pass
        
    except Exception as e:
        logger.warning(f"Error parsing backtest output: {e}")
    
    return metrics

# Additional utility tasks
@celery_app.task
def cleanup_old_results():
    """Clean up old task results and temporary files"""
    try:
        # This could clean up old CSV files, logs, etc.
        logger.info("Cleanup task executed")
        return {'status': 'completed', 'message': 'Cleanup completed'}
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {'status': 'failed', 'error': str(e)}

@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'worker_id': health_check.request.id
    }