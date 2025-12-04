import pandas as pd
import json

LGD_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
FULL_VILLAGES_FILE = 'data/full_villages.json'

def check_match():
    # Load LGD
    print("Loading LGD...")
    df_lgd = pd.read_csv(LGD_FILE)
    print("LGD Columns:", df_lgd.columns.tolist())
    
    # Get Census Codes
    census_codes = set(df_lgd['Census 2011 Code'].astype(str).tolist())
    print(f"Loaded {len(census_codes)} unique Census Codes from LGD.")
    
    # Load Full Villages
    print("Loading Full Villages...")
    with open(FULL_VILLAGES_FILE, 'r') as f:
        data = json.load(f)
        villages = data['villages']
        
    # Check matches
    matches = 0
    total = 0
    
    for v in villages:
        code = v.get('village_code', '')
        # Extract numeric part
        numeric_part = ''.join(filter(str.isdigit, code))
        
        if numeric_part in census_codes:
            matches += 1
        total += 1
        
        if total < 5:
            print(f"Sample: {code} -> {numeric_part} (Match: {numeric_part in census_codes})")
            
    print(f"Total Matches: {matches}/{total} ({matches/total*100:.2f}%)")

if __name__ == "__main__":
    check_match()
