#!/usr/bin/env python3
"""
Setup Example
=============

Example script showing how to integrate P0 improvements into Panelin system.
"""

import uuid
from pathlib import Path

# Import P0 modules
from source_of_truth_validator import SourceOfTruthValidator, validate_source_of_truth
from logging_setup import setup_logging, TraceContext, log_source_decision, log_price_response
from conflict_detector import ConflictDetector


def setup_panelin_improvements():
    """Setup P0 improvements for Panelin"""
    
    # 1. Setup logging
    print("Setting up logging...")
    setup_logging(
        log_dir="logs",
        log_level="INFO",
        json_format=True
    )
    print("✅ Logging configured")
    
    # 2. Initialize validators
    print("\nInitializing validators...")
    source_validator = SourceOfTruthValidator()
    conflict_detector = ConflictDetector()
    print("✅ Validators initialized")
    
    return source_validator, conflict_detector


def example_quotation_flow():
    """Example of how to use P0 improvements in quotation flow"""
    
    # Setup
    source_validator, conflict_detector = setup_panelin_improvements()
    
    # Create trace context for this request
    trace_id = str(uuid.uuid4())
    user_id = "test_user"
    
    with TraceContext(trace_id, user_id):
        print(f"\n📋 Processing quotation request (Trace ID: {trace_id})")
        
        # Simulate quotation request
        product_id = "ISODEC_EPS_100"
        sources_consulted = ["BMC_Base_Conocimiento_GPT.json"]
        
        # Simulate response data
        response_data = {
            "product": "ISODEC EPS 100mm",
            "price": "$46.07",
            "espesor": 100,
            "autoportancia": 5.5
        }
        
        # Validate source of truth
        print("\n🔍 Validating source of truth...")
        validation_result = source_validator.validate_response(
            response_data,
            sources_consulted,
            product_id
        )
        
        if validation_result.valid:
            print("✅ Source validation passed")
        else:
            print("❌ Source validation failed:")
            for error in validation_result.errors:
                print(f"   - {error}")
        
        # Log source decision
        log_source_decision(
            source_level=validation_result.source_level or 1,
            source_file=sources_consulted[0],
            product_id=product_id,
            field="price"
        )
        
        # Log price response
        log_price_response(
            product_id=product_id,
            price=46.07,
            source_file=sources_consulted[0],
            source_level=1
        )
        
        print("\n✅ Quotation flow completed with logging")


def example_conflict_detection():
    """Example of conflict detection"""
    
    print("\n🔍 Running conflict detection...")
    
    conflict_detector = ConflictDetector()
    
    # Example data with conflict
    level_1_data = {
        "product_id": "ISODEC_EPS_100",
        "price": 46.07,
        "espesor": 100,
        "autoportancia": 5.5
    }
    
    level_2_data = {
        "product_id": "ISODEC_EPS_100",
        "price": 46.00,  # Different price - conflict!
        "espesor": 100,
        "autoportancia": 5.5
    }
    
    # Detect conflicts
    conflicts = conflict_detector.detect_conflicts(level_1_data, level_2_data)
    
    if conflicts:
        print(f"⚠️  Detected {len(conflicts)} conflicts:")
        for conflict in conflicts:
            print(f"\n   {conflict.severity.upper()}: {conflict.product_id} - {conflict.field}")
            print(f"   Level 1: {conflict.level_1_value}")
            print(f"   Level 2: {conflict.level_2_value}")
            print(f"   Recommendation: {conflict.recommendation}")
        
        # Generate report
        report = conflict_detector.generate_report(conflicts)
        print(f"\n📊 Report Summary:")
        print(f"   Total: {report['total_conflicts']}")
        print(f"   Critical: {report['critical']}")
        print(f"   Warnings: {report['warnings']}")
        
        # Save report
        output_path = Path("reports") / "conflicts_report.json"
        conflict_detector.save_report(conflicts, str(output_path))
        print(f"\n💾 Report saved to: {output_path}")
    else:
        print("✅ No conflicts detected")


if __name__ == "__main__":
    print("=" * 60)
    print("Panelin Improvements - Setup Example")
    print("=" * 60)
    
    # Run examples
    example_quotation_flow()
    example_conflict_detection()
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the code in each module")
    print("2. Integrate into your Panelin system")
    print("3. Run tests: pytest tests/ -v")
    print("4. Check logs/ directory for log output")
