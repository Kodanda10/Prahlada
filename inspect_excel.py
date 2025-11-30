
import os
import sys

try:
    import pandas as pd
    import openpyxl
    print("Libraries found.")
except ImportError as e:
    print(f"Missing library: {e}")
    sys.exit(1)

file_path = 'Chhattisgarh_District to Ward Mapping_Ward Name Mapping.xlsx'
if os.path.exists(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        print("Sheets found:", xl.sheet_names)
        for sheet in xl.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
            print("Columns found (List):", df.columns.tolist())
            print("First 5 rows:")
            print(df.head().to_string())
    except Exception as e:
        print(f"Error reading excel: {e}")
else:
    print(f"File not found: {file_path}")
