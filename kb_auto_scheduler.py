#!/usr/bin/env python3
"""
Knowledge Base Auto Scheduler
==============================

Automated scheduling for KB updates and training data processing.
Runs updates on optimal schedule to minimize costs.

Usage:
    python kb_auto_scheduler.py --daemon  # Run as background service
    python kb_auto_scheduler.py --once    # Run once and exit
"""

import os
import time
import schedule
from datetime import datetime
from pathlib import Path
from loguru import logger
import sys

# Import optimizers
from kb_update_optimizer import KBUpdateOptimizer
from training_data_optimizer import TrainingDataOptimizer

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", "asst_7LdhJMasW5HHGZh0cgchTGkX")

# Logging setup
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logger.add(
    LOG_DIR / "kb_scheduler_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


class KBAutoScheduler:
    """Automated scheduler for KB updates and training"""
    
    def __init__(self):
        """Initialize scheduler"""
        if not API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.kb_optimizer = KBUpdateOptimizer(API_KEY, ASSISTANT_ID)
        self.training_optimizer = TrainingDataOptimizer()
        
        # Event-based workflow support
        self.event_handlers = {}
        self.workflow_queue = []
        
        logger.info("KB Auto Scheduler initialized")
    
    def update_level_3_daily(self):
        """Update Level 3 (dynamic) daily - incremental updates"""
        logger.info("🔄 Running daily Level 3 update...")
        try:
            result = self.kb_optimizer.update_tier("level_3_dynamic")
            logger.info(f"✅ Level 3 update complete: {result.get('uploaded_count', 0)} files uploaded")
        except Exception as e:
            logger.error(f"❌ Error in Level 3 update: {e}")
    
    def update_level_2_weekly(self):
        """Update Level 2 (validation) weekly - only if conflicts"""
        logger.info("🔄 Running weekly Level 2 update...")
        try:
            # Check for conflicts first (would need conflict detection)
            result = self.kb_optimizer.update_tier("level_2_validation")
            logger.info(f"✅ Level 2 update complete: {result.get('uploaded_count', 0)} files uploaded")
        except Exception as e:
            logger.error(f"❌ Error in Level 2 update: {e}")
    
    def update_level_1_monthly(self):
        """Update Level 1 (master) monthly - only if changed"""
        logger.info("🔄 Running monthly Level 1 update...")
        try:
            result = self.kb_optimizer.update_tier("level_1_master")
            logger.info(f"✅ Level 1 update complete: {result.get('uploaded_count', 0)} files uploaded")
        except Exception as e:
            logger.error(f"❌ Error in Level 1 update: {e}")
    
    def process_training_data_daily(self):
        """Process new training data daily"""
        logger.info("🔄 Processing new training data...")
        try:
            result = self.training_optimizer.process_new_data_only()
            logger.info(
                f"✅ Training data processed: "
                f"{result.get('total_new_interactions', 0)} new, "
                f"{result.get('total_skipped', 0)} skipped"
            )
        except Exception as e:
            logger.error(f"❌ Error processing training data: {e}")
    
    def extract_patterns_weekly(self):
        """Extract patterns weekly"""
        logger.info("🔍 Extracting patterns...")
        try:
            patterns = self.training_optimizer.extract_patterns_weekly()
            logger.info(f"✅ Patterns extracted: {patterns.get('total_interactions_analyzed', 0)} interactions")
        except Exception as e:
            logger.error(f"❌ Error extracting patterns: {e}")
    
    def register_event_handler(self, event_name: str, handler_func):
        """Register an event-based trigger"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler_func)
        logger.info(f"📌 Event handler registered for: {event_name}")
    
    def trigger_event(self, event_name: str, event_data: dict = None):
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_name, [])
        logger.info(f"🔔 Event triggered: {event_name} ({len(handlers)} handlers)")
        
        for handler in handlers:
            try:
                handler(event_data or {})
            except Exception as e:
                logger.error(f"❌ Event handler error ({event_name}): {e}")
    
    def setup_schedule(self):
        """Setup automated schedule"""
        # Level 3: Daily at 2 AM (low traffic time)
        schedule.every().day.at("02:00").do(self.update_level_3_daily)
        
        # Level 2: Weekly on Sundays at 3 AM
        schedule.every().sunday.at("03:00").do(self.update_level_2_weekly)
        
        # Level 1: Monthly on 1st at 4 AM
        schedule.every().month.do(self.update_level_1_monthly)
        
        # Training data: Daily at 4 AM
        schedule.every().day.at("04:00").do(self.process_training_data_daily)
        
        # Pattern extraction: Weekly on Sundays at 5 AM
        schedule.every().sunday.at("05:00").do(self.extract_patterns_weekly)
        
        logger.info("✅ Schedule configured:")
        logger.info("   - Level 3: Daily at 02:00")
        logger.info("   - Level 2: Weekly (Sunday) at 03:00")
        logger.info("   - Level 1: Monthly (1st) at 04:00")
        logger.info("   - Training: Daily at 04:00")
        logger.info("   - Patterns: Weekly (Sunday) at 05:00")
        logger.info("   - Event-based triggers: Enabled")
    
    def run_once(self):
        """Run all scheduled tasks once (for testing)"""
        logger.info("🚀 Running all tasks once...")
        
        # Run all tasks
        self.update_level_3_daily()
        self.process_training_data_daily()
        
        # Check if it's Sunday for weekly tasks
        if datetime.now().weekday() == 6:  # Sunday
            self.update_level_2_weekly()
            self.extract_patterns_weekly()
        
        # Check if it's 1st of month for monthly tasks
        if datetime.now().day == 1:
            self.update_level_1_monthly()
        
        logger.info("✅ All tasks completed")
    
    def run_daemon(self):
        """Run scheduler as daemon (continuous)"""
        logger.info("🚀 Starting KB Auto Scheduler daemon...")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            raise


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KB Auto Scheduler")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon (continuous)")
    parser.add_argument("--once", action="store_true",
                       help="Run all tasks once and exit")
    parser.add_argument("--test", action="store_true",
                       help="Test scheduler (dry run)")
    
    args = parser.parse_args()
    
    try:
        scheduler = KBAutoScheduler()
        
        if args.test:
            print("🧪 Test mode - showing schedule configuration")
            scheduler.setup_schedule()
            print("\n📅 Next scheduled runs:")
            for job in schedule.jobs:
                print(f"   {job}")
            return
        
        if args.once:
            scheduler.run_once()
        elif args.daemon:
            scheduler.run_daemon()
        else:
            parser.print_help()
            print("\n💡 Use --daemon to run continuously or --once to run once")
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("   Make sure OPENAI_API_KEY is set")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
