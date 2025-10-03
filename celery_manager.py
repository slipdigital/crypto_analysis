#!/usr/bin/env python3
"""
Celery Management Script for Crypto Dashboard
Provides commands to manage Celery workers and monitor tasks
"""

import argparse
import subprocess
import sys
import os
import time
import signal
from celery_config import celery_app

def start_worker(concurrency=2, loglevel='info'):
    """Start a Celery worker"""
    print(f"Starting Celery worker with {concurrency} processes...")
    
    cmd = [
        'python', 'celery_worker.py',
        '--loglevel', loglevel,
        '--concurrency', str(concurrency)
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nWorker stopped by user")

def start_beat():
    """Start Celery beat scheduler"""
    print("Starting Celery beat scheduler...")
    
    cmd = [
        'celery', '-A', 'celery_config.celery_app', 'beat',
        '--loglevel=info'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nBeat scheduler stopped by user")

def monitor_tasks():
    """Monitor active tasks"""
    print("Monitoring Celery tasks...")
    print("Press Ctrl+C to stop monitoring")
    print("-" * 50)
    
    try:
        while True:
            # Get task information
            i = celery_app.control.inspect()
            
            active = i.active()
            scheduled = i.scheduled()
            reserved = i.reserved()
            
            # Clear screen (works on most terminals)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🔄 Celery Task Monitor")
            print("=" * 50)
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Show active tasks
            if active:
                print("🟢 Active Tasks:")
                for worker, tasks in active.items():
                    print(f"  Worker: {worker}")
                    for task in tasks:
                        print(f"    - {task['name']} [{task['id'][:8]}...]")
                print()
            else:
                print("🟢 Active Tasks: None")
                print()
            
            # Show scheduled tasks
            if scheduled:
                print("🟡 Scheduled Tasks:")
                for worker, tasks in scheduled.items():
                    print(f"  Worker: {worker}")
                    for task in tasks:
                        task_name = task['request']['task']
                        task_id = task['request']['id']
                        print(f"    - {task_name} [{task_id[:8]}...]")
                print()
            else:
                print("🟡 Scheduled Tasks: None")
                print()
            
            # Show reserved tasks
            if reserved:
                print("🔵 Reserved Tasks:")
                for worker, tasks in reserved.items():
                    print(f"  Worker: {worker}")
                    for task in tasks:
                        print(f"    - {task['name']} [{task['id'][:8]}...]")
                print()
            else:
                print("🔵 Reserved Tasks: None")
                print()
            
            print("Press Ctrl+C to stop monitoring")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

def purge_tasks():
    """Purge all tasks from queues"""
    print("⚠️  WARNING: This will purge ALL tasks from ALL queues!")
    confirm = input("Are you sure? (yes/no): ")
    
    if confirm.lower() == 'yes':
        celery_app.control.purge()
        print("✅ All tasks purged from queues")
    else:
        print("❌ Operation cancelled")

def worker_stats():
    """Show worker statistics"""
    print("📊 Worker Statistics")
    print("=" * 50)
    
    i = celery_app.control.inspect()
    
    # Worker stats
    stats = i.stats()
    if stats:
        for worker, worker_stats in stats.items():
            print(f"\nWorker: {worker}")
            print(f"  Status: {'🟢 Online' if worker_stats else '🔴 Offline'}")
            if worker_stats:
                pool = worker_stats.get('pool', {})
                print(f"  Pool: {pool.get('implementation', 'unknown')}")
                print(f"  Processes: {pool.get('processes', 'unknown')}")
                print(f"  Tasks completed: {worker_stats.get('total', {}).get('tasks.run_crypto_backtest', 0)}")
    else:
        print("No workers found")
    
    # Queue lengths
    print(f"\n📋 Queue Information:")
    
    active = i.active()
    if active:
        total_active = sum(len(tasks) for tasks in active.values())
        print(f"  Active tasks: {total_active}")
    else:
        print("  Active tasks: 0")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Celery Management for Crypto Dashboard')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Worker command
    worker_parser = subparsers.add_parser('worker', help='Start Celery worker')
    worker_parser.add_argument('--concurrency', '-c', type=int, default=2,
                              help='Number of concurrent processes (default: 2)')
    worker_parser.add_argument('--loglevel', '-l', default='info',
                              choices=['debug', 'info', 'warning', 'error', 'critical'],
                              help='Log level (default: info)')
    
    # Beat command
    subparsers.add_parser('beat', help='Start Celery beat scheduler')
    
    # Monitor command
    subparsers.add_parser('monitor', help='Monitor active tasks')
    
    # Stats command
    subparsers.add_parser('stats', help='Show worker statistics')
    
    # Purge command
    subparsers.add_parser('purge', help='Purge all tasks from queues')
    
    # Status command
    subparsers.add_parser('status', help='Show overall status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'worker':
            start_worker(concurrency=args.concurrency, loglevel=args.loglevel)
        elif args.command == 'beat':
            start_beat()
        elif args.command == 'monitor':
            monitor_tasks()
        elif args.command == 'stats':
            worker_stats()
        elif args.command == 'purge':
            purge_tasks()
        elif args.command == 'status':
            worker_stats()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()