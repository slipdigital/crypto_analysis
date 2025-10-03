"""
Celery Configuration for Crypto Dashboard
Handles background task management with Redis as broker
"""

import os
from celery import Celery
from datetime import timedelta

def make_celery(app_name=__name__):
    """Create and configure Celery instance"""
    
    # Use Redis for both broker and result backend
    # Default Redis URL is redis://localhost:6379/0
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Create Celery instance
    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
        include=['tasks']
    )
    
    # Celery configuration
    celery.conf.update(
        # Task serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task routing
        task_routes={
            'tasks.run_crypto_backtest': {'queue': 'crypto_tasks'},
            'tasks.run_data_collection': {'queue': 'crypto_tasks'},
            'tasks.generate_reports': {'queue': 'crypto_tasks'},
        },
        
        # Task result expiration
        result_expires=3600,  # 1 hour
        
        # Task execution settings
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # Beat schedule for periodic tasks (optional)
        beat_schedule={
            'daily-data-collection': {
                'task': 'tasks.run_data_collection',
                'schedule': timedelta(hours=24),
            },
            'hourly-market-reports': {
                'task': 'tasks.generate_reports',
                'schedule': timedelta(hours=1),
            },
        },
        
        # Worker settings
        worker_log_level='INFO',
        worker_hijack_root_logger=False,
        
        # Task time limits
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        
        # Task retry settings
        task_default_retry_delay=60,  # 1 minute
        task_max_retries=3,
    )
    
    return celery

# Create Celery instance
celery_app = make_celery()

if __name__ == '__main__':
    celery_app.start()