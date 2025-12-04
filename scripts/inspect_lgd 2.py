import pandas as pd
import os

file_path = 'data/raw/LGD/District_Subdistrict_Village_Gps_2025-11-27_01-45-36.xlsx'

try:
    df = pd.read_excel(file_path, header=0, nrows=5) # Try header=0 first, read few rows
    print("Columns:", df.columns.tolist())
except Exception as e:
    print(f"Error reading file: {e}")
