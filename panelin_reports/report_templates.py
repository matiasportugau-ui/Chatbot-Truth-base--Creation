#!/usr/bin/env python3
"""
Report Templates
================

Reusable report templates for various report types.
"""

from enum import Enum
from typing import Dict, Any


class TemplateType(Enum):
    """Report template types"""
    KB_HEALTH = "kb_health"
    TRAINING = "training"
    WORKFLOW = "workflow"
    PERFORMANCE = "performance"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"


class ReportTemplate:
    """Base class for report templates"""
    
    @staticmethod
    def get_template(template_type: TemplateType) -> str:
        """Get template by type"""
        templates = {
            TemplateType.KB_HEALTH: ReportTemplate.kb_health_template(),
            TemplateType.TRAINING: ReportTemplate.training_template(),
            TemplateType.WORKFLOW: ReportTemplate.workflow_template(),
            TemplateType.PERFORMANCE: ReportTemplate.performance_template(),
            TemplateType.DAILY_SUMMARY: ReportTemplate.daily_summary_template(),
            TemplateType.WEEKLY_SUMMARY: ReportTemplate.weekly_summary_template(),
            TemplateType.MONTHLY_SUMMARY: ReportTemplate.monthly_summary_template(),
        }
        return templates.get(template_type, "")
    
    @staticmethod
    def kb_health_template() -> str:
        """KB health report template"""
        return """# Knowledge Base Health Report

**Generated**: {generated_at}
**Status**: {status}

## Summary
- Healthy Levels: {levels_healthy}/{total_levels}
- Warnings: {warning_count}
- Conflicts: {conflict_count}

## Details
{details}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def training_template() -> str:
        """Training system report template"""
        return """# Training System Report

**Generated**: {generated_at}

## Summary
- Total Interactions: {total_interactions}
- Processed: {processed}
- Success Rate: {success_rate}%
- Average Quality: {avg_quality}/5.0

## Level Breakdown
{level_breakdown}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def workflow_template() -> str:
        """Workflow execution report template"""
        return """# Workflow Execution Report

**Generated**: {generated_at}

## Summary
- Total Executions: {total_executions}
- Successful: {successful}
- Failed: {failed}
- Success Rate: {success_rate}%

## Recent Executions
{recent_executions}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def performance_template() -> str:
        """Performance report template"""
        return """# System Performance Report

**Generated**: {generated_at}
**Period**: {period}

## Metrics
- Average Response Time: {avg_response_time}ms
- Total Requests: {total_requests}
- Error Rate: {error_rate}%
- Cache Hit Rate: {cache_hit_rate}%

## Trends
{trends}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def daily_summary_template() -> str:
        """Daily summary report template"""
        return """# Daily Summary Report

**Date**: {date}
**Generated**: {generated_at}

## Today's Highlights
- KB Updates: {kb_updates}
- Training Processed: {training_processed}
- Workflows Executed: {workflows_executed}
- Checkpoints Created: {checkpoints_created}

## System Health
- Overall Status: {system_status}
- Active Alerts: {active_alerts}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def weekly_summary_template() -> str:
        """Weekly summary report template"""
        return """# Weekly Summary Report

**Week**: {week_number}
**Period**: {date_range}
**Generated**: {generated_at}

## Week Highlights
- KB Updates: {kb_updates}
- Training Interactions: {training_total}
- Workflows Executed: {workflows_executed}
- System Uptime: {uptime}%

## Key Metrics
{key_metrics}

## Next Week Priorities
{priorities}

---
*Report generated automatically by Panelin Reports*
"""
    
    @staticmethod
    def monthly_summary_template() -> str:
        """Monthly summary report template"""
        return """# Monthly Summary Report

**Month**: {month_name} {year}
**Generated**: {generated_at}

## Month Highlights
- KB Updates: {kb_updates}
- Training Data Processed: {training_total}
- Workflows Executed: {workflows_total}
- New Features Deployed: {features_deployed}

## Performance Overview
{performance_overview}

## Goals for Next Month
{next_month_goals}

---
*Report generated automatically by Panelin Reports*
"""
