#!/usr/bin/env python3
"""
Test Report System
==================

Tests for report generator, templates, scheduler, and distributor.
"""

import sys
from pathlib import Path
import json
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from panelin_reports import (
    ReportGenerator,
    ReportTemplate,
    TemplateType,
    ReportScheduler,
    ReportDistributor
)
from panelin_reports.report_generator import ReportFormat


def test_report_generator():
    """Test report generation"""
    print("\n" + "=" * 80)
    print("Testing Report Generator")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)
        
        # Test KB health report
        test_kb_data = {
            "status": "healthy",
            "levels": {
                "level_1": {"files_found": 2, "files_valid": ["BMC_Base_Conocimiento_GPT-2.json"]},
                "level_2": {"files_found": 1, "files_valid": ["BMC_Base_Unificada_v4.json"]}
            },
            "warnings": [],
            "conflicts": []
        }
        
        # Generate JSON report
        json_filepath = generator.generate_kb_health_report(test_kb_data, ReportFormat.JSON)
        assert Path(json_filepath).exists(), "JSON report not created"
        
        with open(json_filepath, 'r') as f:
            report_data = json.load(f)
            assert report_data["report_type"] == "kb_health"
            assert report_data["summary"]["status"] == "healthy"
        
        print(f"✅ JSON report generated: {Path(json_filepath).name}")
        
        # Generate Markdown report
        md_filepath = generator.generate_kb_health_report(test_kb_data, ReportFormat.MARKDOWN)
        assert Path(md_filepath).exists(), "Markdown report not created"
        
        with open(md_filepath, 'r') as f:
            content = f.read()
            assert "# Knowledge Base Health Report" in content
            assert "healthy" in content.lower()
        
        print(f"✅ Markdown report generated: {Path(md_filepath).name}")
    
    print("\n✅ Report Generator tests passed")


def test_report_templates():
    """Test report templates"""
    print("\n" + "=" * 80)
    print("Testing Report Templates")
    print("=" * 80)
    
    # Test template retrieval
    kb_template = ReportTemplate.get_template(TemplateType.KB_HEALTH)
    assert "Knowledge Base Health Report" in kb_template
    print("✅ KB Health template loaded")
    
    training_template = ReportTemplate.get_template(TemplateType.TRAINING)
    assert "Training System Report" in training_template
    print("✅ Training template loaded")
    
    workflow_template = ReportTemplate.get_template(TemplateType.WORKFLOW)
    assert "Workflow Execution Report" in workflow_template
    print("✅ Workflow template loaded")
    
    daily_template = ReportTemplate.get_template(TemplateType.DAILY_SUMMARY)
    assert "Daily Summary Report" in daily_template
    print("✅ Daily summary template loaded")
    
    print("\n✅ Report Templates tests passed")


def test_report_distributor():
    """Test report distribution (file-only mode)"""
    print("\n" + "=" * 80)
    print("Testing Report Distributor")
    print("=" * 80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test report file
        test_report = Path(tmpdir) / "test_report.md"
        test_report.write_text("# Test Report\n\nThis is a test.")
        
        # Test distributor in file-only mode (no email config)
        distributor = ReportDistributor(config={})
        
        distributor.distribute_report(str(test_report), "test_report")
        
        # Check distribution log
        log = distributor.get_distribution_log()
        assert len(log) == 1, "Distribution not logged"
        assert log[0]["method"] == "file_only"
        assert log[0]["status"] == "completed"
        
        print("✅ Report distributed (file-only mode)")
        print(f"   Distribution log: {len(log)} entries")
    
    print("\n✅ Report Distributor tests passed")


def main():
    """Run all report system tests"""
    print("\n" + "=" * 80)
    print("REPORT SYSTEM TEST SUITE")
    print("=" * 80)
    
    try:
        test_report_generator()
        test_report_templates()
        test_report_distributor()
        
        print("\n" + "=" * 80)
        print("✅ ALL REPORT TESTS PASSED")
        print("=" * 80)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
