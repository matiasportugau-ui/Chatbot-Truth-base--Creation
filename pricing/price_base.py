#!/usr/bin/env python3
"""
Bromyros Price Base Pipeline - CLI Entrypoint

End-to-end pipeline:
1. Parse CSV/XLSX export
2. Validate data quality and IVA consistency
3. Compare with KB master (BMC_Base_Conocimiento_GPT-2.json)

Usage:
    python pricing/price_base.py path/to/export.csv [OPTIONS]
    
Options:
    --kb-path PATH          Path to KB JSON (default: BMC_Base_Conocimiento_GPT-2.json)
    --output-dir DIR        Output directory (default: pricing/out)
    --iva-rate RATE         IVA rate for validation (default: 0.22)
    --tolerance-pct PCT     Price comparison tolerance % (default: 1.0)
    --no-reverse-check      Skip reverse check (KB → sheet)
    --no-validation         Skip validation step
    --no-comparison         Skip KB comparison step
    --json-only             Save only JSON, skip CSV outputs
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Import our modules
from price_base_parser import parse_price_base, save_price_base
from price_base_validate import run_validation
from compare_with_kb_gpt2 import run_comparison


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Bromyros Price Base Pipeline - Parse, Validate, and Compare with KB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with defaults
  python pricing/price_base.py export.csv
  
  # Custom KB path and output directory
  python pricing/price_base.py export.xlsx --kb-path path/to/kb.json --output-dir out/
  
  # Parse and validate only (skip comparison)
  python pricing/price_base.py export.csv --no-comparison
  
  # Parse only (skip validation and comparison)
  python pricing/price_base.py export.csv --no-validation --no-comparison
        """
    )
    
    # Required arguments
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to CSV or XLSX export file"
    )
    
    # Optional arguments
    parser.add_argument(
        "--kb-path",
        type=str,
        default="BMC_Base_Conocimiento_GPT-2.json",
        help="Path to KB JSON file (default: BMC_Base_Conocimiento_GPT-2.json)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="pricing/out",
        help="Output directory for reports (default: pricing/out)"
    )
    
    parser.add_argument(
        "--iva-rate",
        type=float,
        default=0.22,
        help="IVA rate for validation (default: 0.22)"
    )
    
    parser.add_argument(
        "--tolerance-pct",
        type=float,
        default=1.0,
        help="Price comparison tolerance %% (default: 1.0)"
    )
    
    parser.add_argument(
        "--no-reverse-check",
        action="store_true",
        help="Skip reverse check (KB → sheet) in comparison"
    )
    
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip validation step"
    )
    
    parser.add_argument(
        "--no-comparison",
        action="store_true",
        help="Skip KB comparison step"
    )
    
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Save only JSON outputs, skip CSV files"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    
    print("=" * 70)
    print("Bromyros Price Base Pipeline")
    print("=" * 70)
    print(f"\n📄 Input: {input_path}")
    print(f"📁 Output: {output_dir}")
    print(f"💰 IVA rate: {args.iva_rate}")
    print()
    
    # Step 1: Parse
    print("=" * 70)
    print("STEP 1: PARSE")
    print("=" * 70)
    print(f"\n🔍 Parsing {input_path.name}...")
    
    try:
        price_base = parse_price_base(input_path, iva_rate=args.iva_rate)
        
        print(f"✅ Parsed successfully:")
        print(f"   - Total products: {price_base['meta']['total_products']}")
        print(f"   - Unique SKUs: {price_base['meta']['unique_skus']}")
        
        # Save price base
        print(f"\n💾 Saving canonical price base...")
        saved = save_price_base(
            price_base, 
            output_dir, 
            save_csv=not args.json_only,
            save_json=True
        )
        
        for key, path in saved.items():
            print(f"   - {key}: {path}")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 2: Validate
    if not args.no_validation:
        print("\n" + "=" * 70)
        print("STEP 2: VALIDATE")
        print("=" * 70)
        
        try:
            validation = run_validation(price_base, output_dir)
            
            # Check for critical issues
            high_issues = [i for i in validation["issues"] if i.get("severity") == "high"]
            if high_issues:
                print(f"\n⚠️  Warning: {len(high_issues)} high-severity issues found")
                print("   Review validation_issues.csv for details")
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            import traceback
            traceback.print_exc()
            # Continue anyway
    
    # Step 3: Compare with KB
    if not args.no_comparison:
        print("\n" + "=" * 70)
        print("STEP 3: COMPARE WITH KB")
        print("=" * 70)
        
        kb_path = Path(args.kb_path)
        
        if not kb_path.exists():
            print(f"⚠️  Warning: KB file not found: {kb_path}")
            print("   Skipping comparison step")
        else:
            try:
                comparison = run_comparison(
                    price_base,
                    kb_path,
                    output_dir,
                    tolerance_pct=args.tolerance_pct,
                    include_reverse_check=not args.no_reverse_check
                )
                
                # Check for mismatches
                mismatches = comparison["mismatches"]
                if mismatches:
                    high_mismatches = [m for m in mismatches if m.get("severity") == "high"]
                    print(f"\n⚠️  Warning: {len(high_mismatches)} high-severity price mismatches")
                    print("   Review compare_kb_gpt2.csv for details")
                
            except Exception as e:
                print(f"❌ Error during comparison: {e}")
                import traceback
                traceback.print_exc()
                # Continue anyway
    
    # Done
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n📊 Reports saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Review validation_summary.md for data quality issues")
    print("  2. Check compare_kb_gpt2.md for price discrepancies")
    print("  3. Spot-check known values in bromyros_price_base_v1.csv")
    print()


if __name__ == "__main__":
    main()
