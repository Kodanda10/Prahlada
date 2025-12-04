import pandas as pd
import json

LGD_VILLAGE_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
FULL_VILLAGES_FILE = 'data/full_villages.json'

def debug():
    # LGD
    df = pd.read_csv(LGD_VILLAGE_FILE)
    korba_lgd = df[df['District Name (In English)'] == 'Raipur']['Village Name (In Local)'].head(20).tolist()
    print("LGD Raipur Samples:", korba_lgd)
    
    # Full Villages
    with open(FULL_VILLAGES_FILE, 'r') as f:
        data = json.load(f)['villages']
        
    korba_json = [v.get('hindi') for v in data if v.get('district') == 'रायपुर'][:20]
    print("JSON Raipur Samples:", korba_json)

if __name__ == "__main__":
    debug()
