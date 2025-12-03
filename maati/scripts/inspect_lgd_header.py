import pandas as pd
from pathlib import Path

def inspect_excel():
    path = Path("LGD_Chhattisgarh Complete Geographical Data/District_Subdistrict_Village_Gps_2025-11-27_01-45-36.xlsx")
    
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    print("📖 Reading Excel header...")
    df = pd.read_excel(path, nrows=5)
    print("\nColumns:")
    for col in df.columns:
        print(f" - {col}")
        
    print("\nSample Data:")
    print(df.head())

if __name__ == "__main__":
    inspect_excel()
