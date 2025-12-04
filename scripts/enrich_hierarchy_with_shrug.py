import pandas as pd
import json
import os
import re

# File Paths
HIERARCHY_FILE = 'public/chhattisgarh_hierarchy.json'
LGD_MAPPING_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
SHRUG_NAMES_FILE = 'shrug-shrid-keys-csv/shrid_loc_names.csv'
SHRUG_STATS_FILE = 'shrug-shrid-keys-csv/shrid2_spatial_stats.csv'
OUTPUT_FILE = 'public/chhattisgarh_hierarchy_enriched.json'

def enrich_hierarchy():
    print("🚀 Starting Hierarchy Enrichment with SHRUG Data...")

    # 1. Load Existing Hierarchy
    print(f"📖 Loading {HIERARCHY_FILE}...")
    with open(HIERARCHY_FILE, 'r') as f:
        hierarchy = json.load(f)

    # 2. Load LGD Mapping (LGD Code -> Census Code)
    print(f"📖 Loading {LGD_MAPPING_FILE}...")
    df_lgd = pd.read_csv(LGD_MAPPING_FILE)
    # Create map: LGD Village Code (str) -> Census 2011 Code (str)
    # Ensure codes are strings and handle NaNs
    df_lgd['Village Code'] = df_lgd['Village Code'].astype(str)
    df_lgd['Census 2011 Code'] = df_lgd['Census 2011 Code'].fillna(0).astype(int).astype(str)
    
    lgd_to_census = dict(zip(df_lgd['Village Code'], df_lgd['Census 2011 Code']))
    print(f"✅ Loaded {len(lgd_to_census)} LGD->Census mappings.")

    # 3. Load SHRUG Data (Census Code -> Lat/Lon)
    # We need to join names and stats.
    # Strategy: 
    # a. Read names, filter for Chhattisgarh, extract Census Code -> SHRID
    # b. Read stats, filter for those SHRIDs -> Lat/Lon
    
    print(f"📖 Loading {SHRUG_NAMES_FILE}...")
    # Read in chunks or just read all if memory permits. 44MB is fine.
    df_names = pd.read_csv(SHRUG_NAMES_FILE)
    
    # Filter for Chhattisgarh
    # Note: State name might be 'chhattisgarh' or 'Chhattisgarh'
    df_cg_names = df_names[df_names['state_name'].str.lower() == 'chhattisgarh'].copy()
    print(f"   Found {len(df_cg_names)} locations in Chhattisgarh.")
    
    # Extract Census Code from shrid2
    # Format: 11-22-400-03231-431192 -> 431192
    def extract_census_code(shrid):
        parts = shrid.split('-')
        if len(parts) > 0:
            return parts[-1]
        return None

    df_cg_names['census_code'] = df_cg_names['shrid2'].apply(extract_census_code)
    
    # Map SHRID -> Census Code (for joining with stats)
    # Actually we want Census Code -> SHRID to look up stats
    census_to_shrid = dict(zip(df_cg_names['census_code'], df_cg_names['shrid2']))
    
    # Get list of relevant SHRIDs to filter stats
    relevant_shrids = set(df_cg_names['shrid2'])
    
    print(f"📖 Loading {SHRUG_STATS_FILE}...")
    # This file is 167MB, might take a moment.
    df_stats = pd.read_csv(SHRUG_STATS_FILE, usecols=['shrid2', 'latitude', 'longitude'])
    
    # Filter for our SHRIDs
    df_stats_cg = df_stats[df_stats['shrid2'].isin(relevant_shrids)]
    print(f"   Found coordinates for {len(df_stats_cg)} locations.")
    
    # Create Map: SHRID -> (Lat, Lon)
    shrid_to_coords = df_stats_cg.set_index('shrid2')[['latitude', 'longitude']].to_dict('index')
    
    # 4. Traverse and Update Hierarchy
    print("🔄 Updating Hierarchy with Coordinates...")
    
    updated_count = 0
    total_villages = 0
    
    for district, acs in hierarchy.items():
        for ac, blocks in acs.items():
            for block, villages in blocks.items():
                for village in villages:
                    total_villages += 1
                    lgd_code = str(village.get('code'))
                    
                    # Get Census Code
                    census_code = lgd_to_census.get(lgd_code)
                    
                    if census_code and census_code != '0':
                        # Get SHRID
                        shrid = census_to_shrid.get(census_code)
                        
                        if shrid:
                            # Get Coords
                            coords = shrid_to_coords.get(shrid)
                            
                            if coords:
                                village['lat'] = coords['latitude']
                                village['lng'] = coords['longitude']
                                updated_count += 1
    
    print(f"✅ Updated {updated_count} out of {total_villages} villages ({updated_count/total_villages*100:.1f}%)")
    
    # 5. Save Enriched Hierarchy
    print(f"💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(hierarchy, f, indent=2)

if __name__ == "__main__":
    enrich_hierarchy()
