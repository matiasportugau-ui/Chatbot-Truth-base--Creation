#!/usr/bin/env python3
"""
Report Scheduler
================

Schedules automatic report generation at specified intervals.
"""

import schedule
import time
from datetime import datetime
from typing import Dict, Optional, Any, Callable
from pathlib import Path
from loguru import logger

from .report_generator import ReportGenerator, ReportFormat
from .report_distributor import ReportDistributor


class ReportScheduler:
    """Schedules automatic report generation"""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        distribute: bool = False,
        email_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize report scheduler
        
        Args:
            output_dir: Directory for report output
            distribute: Enable email distribution
            email_config: Email configuration
        """
        self.generator = ReportGenerator(output_dir)
        self.distributor = ReportDistributor(email_config) if distribute else None
        self.data_collectors: Dict[str, Callable] = {}
        
        # Logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.add(
            log_dir / "report_scheduler_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days"
        )
    
    def register_data_collector(self, report_type: str, collector_func: Callable):
        """Register a data collector function for a report type"""
        self.data_collectors[report_type] = collector_func
        logger.info(f"📊 Data collector registered for: {report_type}")
    
    def generate_daily_report(self):
        """Generate daily summary report"""
        logger.info("📊 Generating daily report...")
        
        try:
            # Collect data
            data = {}
            for report_type, collector in self.data_collectors.items():
                try:
                    data[report_type] = collector()
                except Exception as e:
                    logger.error(f"Error collecting {report_type} data: {e}")
            
            # Generate report
            filepath = self.generator.generate_kb_health_report(
                data.get("kb_health", {}),
                format=ReportFormat.MARKDOWN
            )
            
            logger.info(f"✅ Daily report generated: {filepath}")
            
            # Distribute if enabled
            if self.distributor:
                self.distributor.distribute_report(filepath, "daily_report")
        
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {e}")
    
    def generate_weekly_report(self):
        """Generate weekly summary report"""
        logger.info("📊 Generating weekly report...")
        
        try:
            # Collect weekly data
            data = {}
            for report_type, collector in self.data_collectors.items():
                try:
                    data[report_type] = collector()
                except Exception as e:
                    logger.error(f"Error collecting {report_type} data: {e}")
            
            # Generate report
            filepath = self.generator.generate_kb_health_report(
                data.get("kb_health", {}),
                format=ReportFormat.MARKDOWN
            )
            
            logger.info(f"✅ Weekly report generated: {filepath}")
            
            # Distribute if enabled
            if self.distributor:
                self.distributor.distribute_report(filepath, "weekly_report")
        
        except Exception as e:
            logger.error(f"❌ Error generating weekly report: {e}")
    
    def generate_monthly_report(self):
        """Generate monthly summary report"""
        logger.info("📊 Generating monthly report...")
        
        try:
            # Collect monthly data
            data = {}
            for report_type, collector in self.data_collectors.items():
                try:
                    data[report_type] = collector()
                except Exception as e:
                    logger.error(f"Error collecting {report_type} data: {e}")
            
            # Generate report
            filepath = self.generator.generate_kb_health_report(
                data.get("kb_health", {}),
                format=ReportFormat.MARKDOWN
            )
            
            logger.info(f"✅ Monthly report generated: {filepath}")
            
            # Distribute if enabled
            if self.distributor:
                self.distributor.distribute_report(filepath, "monthly_report")
        
        except Exception as e:
            logger.error(f"❌ Error generating monthly report: {e}")
    
    def setup_schedule(self):
        """Setup automated report schedule"""
        # Daily reports at 6 AM
        schedule.every().day.at("06:00").do(self.generate_daily_report)
        
        # Weekly reports on Mondays at 7 AM
        schedule.every().monday.at("07:00").do(self.generate_weekly_report)
        
        # Monthly reports on 1st at 8 AM
        schedule.every().month.do(self.generate_monthly_report)
        
        logger.info("✅ Report schedule configured:")
        logger.info("   - Daily: Every day at 06:00")
        logger.info("   - Weekly: Mondays at 07:00")
        logger.info("   - Monthly: 1st of month at 08:00")
    
    def run_daemon(self):
        """Run scheduler as daemon"""
        logger.info("🚀 Starting Report Scheduler daemon...")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Report Scheduler stopped")
