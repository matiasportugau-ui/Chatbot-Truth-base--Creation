import pandas as pd
import sys

file_path = "/Users/matias/Library/Mobile Documents/com~apple~CloudDocs/Cotización 01122023 ISOPANEL 100 - 150 - 200 - 250 mm Cubierta.ods"

try:
    # Read the ODS file. read_excel supports ODS with the 'odf' engine.
    # Load all sheets
    xls = pd.read_excel(file_path, sheet_name=None, engine="odf")

    print(f"File: {file_path}")
    print(f"Number of sheets: {len(xls)}")
    print("-" * 30)

    for sheet_name, df in xls.items():
        print(f"Sheet: {sheet_name}")
        print(f"Shape: {df.shape}")
        print("Columns:")
        print(df.columns.tolist())
        print("\nFirst 20 rows:")
        # Use a larger width to prevent wrapping if possible, or just print
        print(df.head(20).to_string())
        print("-" * 30)

except Exception as e:
    print(f"Error reading file: {e}")
