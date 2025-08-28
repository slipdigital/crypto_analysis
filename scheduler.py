"""
Cryptocurrency Data Collection Scheduler
Handles automated daily collection of cryptocurrency data
"""

import schedule
import time
import logging
import os
import sys
from datetime import datetime
from crypto_collector import CryptoDataCollector


class CryptoScheduler:
    """Scheduler for automated cryptocurrency data collection"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the scheduler"""
        self.collector = CryptoDataCollector(config_path)
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    def collect_data_job(self):
        """Job function for scheduled data collection"""
        try:
            self.logger.info("Starting scheduled data collection")
            start_time = datetime.now()
            
            self.collector.collect_all_data()
            
            end_time = datetime.now()
            duration = end_time - start_time
            self.logger.info(f"Scheduled data collection completed in {duration}")
            
        except Exception as e:
            self.logger.error(f"Error during scheduled data collection: {e}")
    
    def setup_daily_schedule(self, time_str: str = "09:00"):
        """Setup daily collection schedule"""
        schedule.clear()  # Clear any existing schedules
        schedule.every().day.at(time_str).do(self.collect_data_job)
        self.logger.info(f"Scheduled daily data collection at {time_str}")
    
    def setup_weekly_schedule(self, day: str = "monday", time_str: str = "09:00"):
        """Setup weekly collection schedule"""
        schedule.clear()
        getattr(schedule.every(), day.lower()).at(time_str).do(self.collect_data_job)
        self.logger.info(f"Scheduled weekly data collection on {day} at {time_str}")
    
    def run_once(self):
        """Run data collection once immediately"""
        self.logger.info("Running data collection once")
        self.collect_data_job()
    
    def start_scheduler(self):
        """Start the scheduler loop"""
        self.is_running = True
        self.logger.info("Starting scheduler loop")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
        finally:
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        self.logger.info("Scheduler stop requested")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run
        return None
    
    def list_scheduled_jobs(self):
        """List all scheduled jobs"""
        jobs = schedule.get_jobs()
        if jobs:
            self.logger.info("Scheduled jobs:")
            for i, job in enumerate(jobs, 1):
                self.logger.info(f"  {i}. {job}")
        else:
            self.logger.info("No scheduled jobs")


def main():
    """Main function for running the scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cryptocurrency Data Collection Scheduler")
    parser.add_argument("--mode", choices=["once", "daily", "weekly"], default="daily",
                       help="Collection mode: once, daily, or weekly")
    parser.add_argument("--time", default="09:00",
                       help="Time for scheduled collection (HH:MM format)")
    parser.add_argument("--day", default="monday",
                       help="Day for weekly collection (monday, tuesday, etc.)")
    parser.add_argument("--config", default="config/settings.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        scheduler = CryptoScheduler(args.config)
        
        if args.mode == "once":
            scheduler.run_once()
        elif args.mode == "daily":
            scheduler.setup_daily_schedule(args.time)
            print(f"Scheduled daily collection at {args.time}")
            print("Press Ctrl+C to stop the scheduler")
            scheduler.start_scheduler()
        elif args.mode == "weekly":
            scheduler.setup_weekly_schedule(args.day, args.time)
            print(f"Scheduled weekly collection on {args.day} at {args.time}")
            print("Press Ctrl+C to stop the scheduler")
            scheduler.start_scheduler()
            
    except Exception as e:
        logging.error(f"Fatal error in scheduler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()