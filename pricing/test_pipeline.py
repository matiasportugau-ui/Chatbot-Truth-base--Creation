#!/usr/bin/env python3
"""
Test script for Bromyros Price Base pipeline.

Tests the pipeline on the actual MATRIZ CSV file.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from price_base_parser import parse_price_base, save_price_base
from price_base_validate import run_validation
from compare_with_kb_gpt2 import run_comparison


def test_pipeline():
    """Run a quick test of the pipeline."""
    
    print("=" * 70)
    print("Bromyros Price Base - Pipeline Test")
    print("=" * 70)
    
    # Paths
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "MATRIZ de COSTOS y VENTAS 2026.xlsx - BROMYROS.csv"
    kb_path = project_root / "BMC_Base_Conocimiento_GPT-2.json"
    output_dir = Path(__file__).parent / "out"
    
    # Check files exist
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        return False
    
    if not kb_path.exists():
        print(f"⚠️  KB not found: {kb_path}")
        print("   Will skip comparison step")
        kb_path = None
    
    print(f"\n📄 CSV: {csv_path.name}")
    print(f"📄 KB: {kb_path.name if kb_path else 'N/A'}")
    print(f"📁 Output: {output_dir}")
    
    # Step 1: Parse
    print("\n" + "-" * 70)
    print("Step 1: Parse CSV")
    print("-" * 70)
    
    try:
        price_base = parse_price_base(csv_path, iva_rate=0.22)
        
        print(f"\n✅ Parsing successful!")
        print(f"   Total products: {price_base['meta']['total_products']}")
        print(f"   Unique SKUs: {price_base['meta']['unique_skus']}")
        
        # Show sample products
        print("\n   Sample products (first 5):")
        for i, p in enumerate(price_base['products'][:5], 1):
            print(f"   {i}. {p['sku']} - {p['name'][:50]}")
            print(f"      Category: {p['category']['familia']} ({p['category']['unit_base']})")
            if p.get('thickness_mm'):
                print(f"      Thickness: {p['thickness_mm']}mm")
            if p.get('length_m'):
                print(f"      Length: {p['length_m']}m")
        
        # Save
        saved = save_price_base(price_base, output_dir)
        print(f"\n   Saved to:")
        for key, path in saved.items():
            print(f"   - {path}")
        
    except Exception as e:
        print(f"\n❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Validate
    print("\n" + "-" * 70)
    print("Step 2: Validate")
    print("-" * 70)
    
    try:
        validation = run_validation(price_base, output_dir)
        
        print("\n✅ Validation complete!")
        
        # Show key metrics
        summary = validation['summary']
        print(f"   IVA pass rate (sale): {summary['iva_consistency']['sale_pass_rate_pct']:.1f}%")
        print(f"   IVA pass rate (web): {summary['iva_consistency']['web_pass_rate_pct']:.1f}%")
        print(f"   Length extraction hit rate: {summary['length_extraction']['hit_rate_pct']:.1f}%")
        print(f"   Total issues: {len(validation['issues'])}")
        
        # Show issues by severity
        high = [i for i in validation['issues'] if i.get('severity') == 'high']
        medium = [i for i in validation['issues'] if i.get('severity') == 'medium']
        low = [i for i in validation['issues'] if i.get('severity') == 'low']
        
        print(f"   - High: {len(high)}")
        print(f"   - Medium: {len(medium)}")
        print(f"   - Low: {len(low)}")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Compare with KB
    if kb_path:
        print("\n" + "-" * 70)
        print("Step 3: Compare with KB")
        print("-" * 70)
        
        try:
            comparison = run_comparison(
                price_base,
                kb_path,
                output_dir,
                tolerance_pct=1.0,
                include_reverse_check=True
            )
            
            print("\n✅ Comparison complete!")
            
            # Show key metrics
            stats = comparison['stats']
            print(f"   Total comparisons: {stats['total_comparisons']}")
            print(f"   Matches: {stats['matches']}")
            print(f"   Mismatches: {stats['mismatches']}")
            print(f"   Missing in KB: {stats['missing_in_kb']}")
            
            # Show sample match
            if comparison['matches']:
                print("\n   Sample match:")
                m = comparison['matches'][0]
                print(f"   {m['sku']} - {m['name'][:50]}")
                print(f"   Sheet: ${m['sheet_price']}, KB: ${m['kb_price']}, Delta: {m['delta_pct']:.2f}%")
            
            # Show sample mismatch
            if comparison['mismatches']:
                print("\n   Sample mismatch:")
                m = comparison['mismatches'][0]
                print(f"   {m['sku']} - {m['name'][:50]}")
                print(f"   Sheet: ${m['sheet_price']}, KB: ${m['kb_price']}, Delta: {m['delta_pct']:.2f}%")
            
        except Exception as e:
            print(f"\n❌ Comparison failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Pipeline test completed successfully!")
    print("=" * 70)
    print(f"\n📊 All reports saved to: {output_dir}")
    print("\nFiles created:")
    print("  - bromyros_price_base_v1.json")
    print("  - bromyros_price_base_v1.csv")
    print("  - validation_issues.csv")
    print("  - validation_summary.md")
    if kb_path:
        print("  - compare_kb_gpt2.csv")
        print("  - compare_kb_gpt2.md")
    
    return True


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
