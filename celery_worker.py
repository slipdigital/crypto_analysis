#!/usr/bin/env python3
"""
Celery Worker for Crypto Dashboard
Run this script to start Celery workers for processing background tasks
"""

import os
import sys
import platform
from celery_config import celery_app

def main():
    """Start Celery worker"""
    
    # Set the worker name based on hostname (Windows compatible)
    hostname = 'localhost'
    
    worker_name = f"crypto_worker@{hostname}"
    
    # Configure worker arguments (Windows compatible)
    pool_type = 'solo' if os.name == 'nt' else 'prefork'  # Use solo pool on Windows
    
    worker_args = [
        'worker',
        '--loglevel=info',
        '--concurrency=1' if os.name == 'nt' else '--concurrency=2',  # Solo pool requires concurrency=1
        '--queues=crypto_tasks',  # Queue to process
        f'--hostname={worker_name}',
        f'--pool={pool_type}',  # Use appropriate pool for OS
        '--without-gossip',  # Disable gossip for better performance
        '--without-mingle',  # Disable mingle for faster startup
        '--heartbeat-interval=30',  # Heartbeat every 30 seconds
    ]
    
    # Add any additional arguments passed to the script
    worker_args.extend(sys.argv[1:])
    
    print("Starting Celery worker for Crypto Dashboard...")
    print(f"Worker name: {worker_name}")
    print(f"Queues: crypto_tasks")
    print(f"Concurrency: 2")
    print("Available tasks:")
    print("  - tasks.run_crypto_backtest")
    print("  - tasks.run_data_collection")
    print("  - tasks.generate_reports")
    print("  - tasks.cleanup_old_results")
    print("  - tasks.health_check")
    print("\nPress Ctrl+C to stop the worker")
    print("-" * 50)
    
    try:
        celery_app.worker_main(worker_args)
    except KeyboardInterrupt:
        print("\nShutting down worker...")
        sys.exit(0)

if __name__ == '__main__':
    main()