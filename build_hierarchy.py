import pandas as pd
import json
import os

# File Paths
CONSTITUENCY_FILE = 'data/raw/LGD/Constituency_Report_2025-11-27_01-47-58.xlsx'
BLOCK_MAPPING_FILE = 'data/raw/LGD/District_Village_Block_Gps_Mapping_cached.csv'
OUTPUT_FILE = 'public/chhattisgarh_hierarchy.json'

def process_data():
    print("🚀 Building Hierarchy from LGD Data...")

    # 1. Load AC Mapping
    print(f"📖 Loading {CONSTITUENCY_FILE}...")
    df_ac = pd.read_excel(CONSTITUENCY_FILE, header=1)
    df_ac = df_ac[df_ac['Entity Type'] == 'Village']
    # Map Village Code -> AC Name
    ac_map = dict(zip(df_ac['Entity Code'].astype(str), df_ac['Assembly Constituency Name']))
    print(f"✅ Loaded {len(ac_map)} AC mappings.")

    # 2. Load District/Block Mapping
    print(f"📖 Loading {BLOCK_MAPPING_FILE}...")
    df_block = pd.read_csv(BLOCK_MAPPING_FILE)
    # Ensure string codes
    df_block['Village Code'] = df_block['Village Code'].astype(str)
    
    print(f"✅ Loaded {len(df_block)} village mappings.")

    # 3. Build Hierarchy
    hierarchy = {}
    
    count = 0
    for _, row in df_block.iterrows():
        v_code = row['Village Code']
        v_name = row['Village Name (In English)']
        dist_name = row['District Name  (In English)']
        block_name = row['Development Block Name  (In English)']
        
        # Get AC from map (default to 'Unknown' if missing)
        ac_name = ac_map.get(v_code, 'Unknown AC')
        
        # Initialize District
        if dist_name not in hierarchy:
            hierarchy[dist_name] = {}
            
        # Initialize AC
        if ac_name not in hierarchy[dist_name]:
            hierarchy[dist_name][ac_name] = {}
            
        # Initialize Block
        if block_name not in hierarchy[dist_name][ac_name]:
            hierarchy[dist_name][ac_name][block_name] = []
            
        # Add Village
        hierarchy[dist_name][ac_name][block_name].append({
            'code': v_code,
            'name': v_name
        })
        count += 1
        
    print(f"✅ Processed {count} villages into hierarchy.")
    
    # 4. Save
    print(f"💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(hierarchy, f, indent=2)
        
    # Validation
    if 'Korba' in hierarchy:
        print("Korba ACs:", list(hierarchy['Korba'].keys()))

if __name__ == "__main__":
    process_data()
