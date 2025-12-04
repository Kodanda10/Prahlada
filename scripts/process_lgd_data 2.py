import pandas as pd
import json
import os

# File Paths
CONSTITUENCY_FILE = 'data/raw/LGD/Constituency_Report_2025-11-27_01-47-58.xlsx'
MAPPING_FILE = 'data/raw/LGD/District_Village_Block_Gps_Mapping_cached.csv'
FULL_VILLAGES_FILE = 'data/full_villages.json'
OUTPUT_FILE = 'public/chhattisgarh_corrected_villages.json'

def process_data():
    print("🚀 Starting LGD Data Processing...")

    # 1. Load Constituency Data (AC Mapping)
    print(f"📖 Loading {CONSTITUENCY_FILE}...")
    try:
        df_ac = pd.read_excel(CONSTITUENCY_FILE, header=1)
        # Filter for Villages
        df_ac = df_ac[df_ac['Entity Type'] == 'Village'].copy()
        # Rename columns
        df_ac = df_ac.rename(columns={
            'Entity Code': 'village_code',
            'Assembly Constituency Name': 'assembly_constituency',
            'Parliament Constituency Name': 'parliamentary_constituency'
        })
        # Keep only relevant columns
        df_ac = df_ac[['village_code', 'assembly_constituency', 'parliamentary_constituency']]
        # Ensure village_code is string
        df_ac['village_code'] = df_ac['village_code'].astype(str)
        print(f"✅ Loaded {len(df_ac)} village-AC mappings.")
    except Exception as e:
        print(f"❌ Error loading Constituency file: {e}")
        return

    # 2. Load District/Block Mapping
    print(f"📖 Loading {MAPPING_FILE}...")
    try:
        df_map = pd.read_csv(MAPPING_FILE)
        # Rename columns
        df_map = df_map.rename(columns={
            'Village Code': 'village_code',
            'District Name  (In English)': 'district',
            'Development Block Name  (In English)': 'block'
        })
        # Keep relevant columns
        df_map = df_map[['village_code', 'district', 'block']]
        # Ensure village_code is string
        df_map['village_code'] = df_map['village_code'].astype(str)
        print(f"✅ Loaded {len(df_map)} village-District/Block mappings.")
    except Exception as e:
        print(f"❌ Error loading Mapping file: {e}")
        return

    # 3. Load Full Villages (Lat/Long)
    print(f"📖 Loading {FULL_VILLAGES_FILE}...")
    try:
        with open(FULL_VILLAGES_FILE, 'r') as f:
            data = json.load(f)
            villages = data['villages']
        
        df_villages = pd.DataFrame(villages)
        # Ensure village_code is string
        df_villages['village_code'] = df_villages['village_code'].astype(str)
        print(f"✅ Loaded {len(df_villages)} villages with coordinates.")
    except Exception as e:
        print(f"❌ Error loading Full Villages file: {e}")
        return

    # 4. Merge Data
    print("🔄 Merging datasets...")
    
    # Merge AC data
    # We use 'left' merge on df_villages to keep all villages, but update their AC info
    merged = pd.merge(df_villages, df_ac, on='village_code', how='left', suffixes=('', '_lgd'))
    
    # Update AC if LGD data exists
    merged['assembly_constituency'] = merged['assembly_constituency_lgd'].combine_first(merged['assembly_constituency'])
    merged['parliamentary_constituency'] = merged['parliamentary_constituency_lgd'].combine_first(merged['parliamentary_constituency'])
    
    # Merge District/Block data
    merged = pd.merge(merged, df_map, on='village_code', how='left', suffixes=('', '_lgd'))
    
    # Update District/Block if LGD data exists
    merged['district'] = merged['district_lgd'].combine_first(merged['district'])
    merged['block'] = merged['block_lgd'].combine_first(merged['block'])
    
    # Drop temporary columns
    cols_to_drop = [c for c in merged.columns if c.endswith('_lgd')]
    merged = merged.drop(columns=cols_to_drop)
    
    # Fill NaN with empty string or sensible defaults
    merged = merged.fillna('')

    print("✅ Merge complete.")
    
    print("Unique Districts in Merged Data:", sorted(merged['district'].unique().astype(str).tolist()))
    
    # 5. Save Output
    print(f"💾 Saving to {OUTPUT_FILE}...")
    output_data = {
        'state': 'Chhattisgarh',
        'total_villages': len(merged),
        'villages': merged.to_dict(orient='records')
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"🎉 Successfully saved corrected village data to {OUTPUT_FILE}")
    
    # Validation
    korba_villages = merged[merged['district'] == 'Korba']
    print(f"🔍 Validation: Found {len(korba_villages)} villages in Korba.")
    print("Unique ACs in Korba:", korba_villages['assembly_constituency'].unique().tolist())

if __name__ == "__main__":
    process_data()
