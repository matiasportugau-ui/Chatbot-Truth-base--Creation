#!/usr/bin/env python3
"""
CSV Data Normalization Script
==============================

Cleans up normalized_full.csv to address identified data quality issues:
1. Duplicate SKUs
2. Unit inconsistencies (m2, m2 , unit, Unit, ml)
3. Thickness format issues (strings, ranges)
4. Trailing spaces in familia/category names

Usage:
    python3 data_normalizer.py

Output:
    - 04_DATA/cleaned/normalized_full_cleaned.csv
    - 05_ANALYSIS/data_normalization_report.txt
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def load_csv(filepath: Path) -> Tuple[List[str], List[Dict]]:
    """Load CSV file and return headers and rows"""
    with open(filepath, 'r', encoding='utf-8') as f:
        # Skip any empty lines at the start
        line = f.readline()
        while line.strip() == '' and line:
            line = f.readline()
        
        # This should be the header line
        headers = line.strip().split(',')
        
        # Read the rest as data
        reader = csv.DictReader(f, fieldnames=headers)
        rows = list(reader)
    
    return headers, rows

def standardize_unit(unit: str) -> str:
    """Standardize unit names"""
    unit = unit.strip()
    
    # Normalize variations
    if unit.lower() in ['m2', 'm2 ', 'm²']:
        return 'm2'
    elif unit.lower() in ['unit', 'unidad', 'unidades']:
        return 'unit'
    elif unit.lower() in ['ml', 'metro lineal', 'metros lineales', 'metro_lineal']:
        return 'metro_lineal'
    elif unit.lower() in ['n/a', 'na', '']:
        return 'N/A'
    
    return unit

def clean_thickness(thickness: str) -> str:
    """Clean thickness_mm field"""
    thickness = thickness.strip()
    
    # Handle special cases
    if thickness.lower() in ['estandar', 'estandar ', 'n/a', 'na', '']:
        return 'Estandar'
    
    # Extract first number from ranges like "30 - 40 - 50"
    if '-' in thickness or ' ' in thickness:
        match = re.search(r'\d+', thickness)
        if match:
            return match.group(0)
    
    # Remove non-numeric characters except digits
    cleaned = re.sub(r'[^\d]', '', thickness)
    return cleaned if cleaned else 'Estandar'

def strip_trailing_spaces(text: str) -> str:
    """Remove trailing and leading spaces"""
    return text.strip() if text else text

def identify_duplicates(rows: List[Dict]) -> Dict[str, List[int]]:
    """Identify duplicate SKUs and their row indices"""
    sku_positions = defaultdict(list)
    for idx, row in enumerate(rows):
        sku = row.get('sku', '').strip()
        if sku:
            sku_positions[sku].append(idx)
    
    # Return only duplicates
    return {sku: positions for sku, positions in sku_positions.items() if len(positions) > 1}

def resolve_duplicates(rows: List[Dict], duplicates: Dict[str, List[int]]) -> Tuple[List[Dict], List[str]]:
    """
    Resolve duplicate SKUs by keeping the first occurrence and marking others.
    Returns cleaned rows and report lines.
    """
    report = []
    rows_to_remove = set()
    
    for sku, positions in duplicates.items():
        report.append(f"Duplicate SKU '{sku}' found at rows: {positions}")
        # Keep first occurrence, mark others for removal
        for pos in positions[1:]:
            rows_to_remove.add(pos)
            report.append(f"  - Removing duplicate at row {pos}")
    
    # Create cleaned list (excluding duplicates)
    cleaned_rows = [row for idx, row in enumerate(rows) if idx not in rows_to_remove]
    
    return cleaned_rows, report

def normalize_data(input_path: Path, output_path: Path, report_path: Path):
    """Main normalization function"""
    print("=" * 70)
    print("CSV DATA NORMALIZATION")
    print("=" * 70)
    
    # Load data
    print(f"\n📂 Loading data from: {input_path}")
    headers, rows = load_csv(input_path)
    print(f"   - Headers: {len(headers)}")
    print(f"   - Rows: {len(rows)}")
    
    # Initialize report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("DATA NORMALIZATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"\nInput: {input_path}")
    report_lines.append(f"Output: {output_path}")
    report_lines.append(f"Rows loaded: {len(rows)}\n")
    
    # Step 1: Identify duplicates
    print("\n🔍 Step 1: Identifying duplicate SKUs...")
    duplicates = identify_duplicates(rows)
    print(f"   - Found {len(duplicates)} duplicate SKUs")
    print(f"   - Total duplicate rows: {sum(len(positions) - 1 for positions in duplicates.values())}")
    
    report_lines.append(f"\n1. DUPLICATE SKUs: {len(duplicates)}")
    
    # Step 2: Resolve duplicates
    print("\n🔧 Step 2: Resolving duplicates...")
    cleaned_rows, dup_report = resolve_duplicates(rows, duplicates)
    report_lines.extend(dup_report)
    print(f"   - Rows after deduplication: {len(cleaned_rows)}")
    
    # Step 3: Standardize units
    print("\n🔧 Step 3: Standardizing unit names...")
    unit_changes = 0
    unit_map = defaultdict(int)
    
    for row in cleaned_rows:
        original_unit = row.get('unit_base', '')
        standardized_unit = standardize_unit(original_unit)
        if original_unit != standardized_unit:
            unit_changes += 1
            unit_map[f"{original_unit} -> {standardized_unit}"] += 1
        row['unit_base'] = standardized_unit
    
    print(f"   - Unit changes: {unit_changes}")
    report_lines.append(f"\n2. UNIT STANDARDIZATION: {unit_changes} changes")
    for change, count in sorted(unit_map.items()):
        report_lines.append(f"   - {change}: {count} times")
    
    # Step 4: Clean thickness
    print("\n🔧 Step 4: Cleaning thickness_mm field...")
    thickness_changes = 0
    
    for row in cleaned_rows:
        original_thickness = row.get('thickness_mm', '')
        cleaned_thickness = clean_thickness(original_thickness)
        if original_thickness != cleaned_thickness:
            thickness_changes += 1
        row['thickness_mm'] = cleaned_thickness
    
    print(f"   - Thickness changes: {thickness_changes}")
    report_lines.append(f"\n3. THICKNESS CLEANING: {thickness_changes} changes")
    
    # Step 5: Strip trailing spaces
    print("\n🔧 Step 5: Stripping trailing spaces...")
    space_changes = 0
    fields_to_clean = ['supplier', 'family', 'category', 'sub_family', 'name']
    
    for row in cleaned_rows:
        for field in fields_to_clean:
            if field in row:
                original = row[field]
                cleaned = strip_trailing_spaces(original)
                if original != cleaned:
                    space_changes += 1
                row[field] = cleaned
    
    print(f"   - Trailing space removals: {space_changes}")
    report_lines.append(f"\n4. TRAILING SPACES REMOVED: {space_changes}")
    
    # Summary
    report_lines.append("\n" + "=" * 70)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 70)
    report_lines.append(f"Original rows: {len(rows)}")
    report_lines.append(f"Cleaned rows: {len(cleaned_rows)}")
    report_lines.append(f"Rows removed: {len(rows) - len(cleaned_rows)}")
    report_lines.append(f"Total changes: {unit_changes + thickness_changes + space_changes}")
    
    # Save cleaned CSV
    print(f"\n💾 Saving cleaned data to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Filter out None keys from rows and keep only valid headers
    valid_headers = [h for h in headers if h]  # Remove empty headers
    filtered_rows = []
    for row in cleaned_rows:
        # Only keep fields that are in valid headers
        filtered_row = {k: v for k, v in row.items() if k in valid_headers}
        filtered_rows.append(filtered_row)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=valid_headers)
        writer.writeheader()
        writer.writerows(filtered_rows)
    
    print(f"   ✅ Saved {len(filtered_rows)} rows with {len(valid_headers)} fields")
    
    # Save report
    print(f"\n📄 Saving report to: {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"   ✅ Report saved")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ NORMALIZATION COMPLETE")
    print("=" * 70)
    print(f"Original rows: {len(rows)}")
    print(f"Cleaned rows: {len(cleaned_rows)}")
    print(f"Rows removed: {len(rows) - len(cleaned_rows)} ({(len(rows) - len(cleaned_rows)) / len(rows) * 100:.1f}%)")
    print(f"Data quality improvements: {unit_changes + thickness_changes + space_changes}")
    print()

def main():
    """Main entry point"""
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_path = project_root / "04_DATA" / "raw" / "normalized_full.csv"
    output_path = project_root / "04_DATA" / "cleaned" / "normalized_full_cleaned.csv"
    report_path = project_root / "05_ANALYSIS" / "data_normalization_report.txt"
    
    # Verify input exists
    if not input_path.exists():
        print(f"❌ Error: Input file not found at {input_path}")
        return 1
    
    # Run normalization
    try:
        normalize_data(input_path, output_path, report_path)
        return 0
    except Exception as e:
        print(f"\n❌ Error during normalization: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
