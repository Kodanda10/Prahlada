import json
import csv
import os
from collections import defaultdict

# File Paths
HIERARCHY_FILE = 'public/chhattisgarh_hierarchy.json'
LGD_MAPPING_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
GP_MAPPING_FILE = 'data/raw/LGD/Village_Gram_Panchayat_Mapping_cached.csv'
SHRUG_NAMES_FILE = 'shrug-shrid-keys-csv/shrid_loc_names.csv'
SHRUG_STATS_FILE = 'shrug-shrid-keys-csv/shrid2_spatial_stats.csv'
AC_NAME_KEY_FILE = 'shrug-PC and AC/ac08_name_key.csv'
SHRID_AC_KEY_FILE = 'shrug-PC and AC/shrid_frag_con08_key.csv'
OUTPUT_FILE = 'public/chhattisgarh_hierarchy_enriched.json'

def load_lgd_mapping():
    print(f"📖 Loading {LGD_MAPPING_FILE}...")
    mapping = {}
    try:
        with open(LGD_MAPPING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                v_code = row.get('Village Code', '').strip()
                c_code = row.get('Census 2011 Code', '').strip()
                if v_code and c_code and c_code != '0':
                    if '.' in c_code:
                        c_code = c_code.split('.')[0]
                    mapping[v_code] = c_code
    except Exception as e:
        print(f"Error loading LGD mapping: {e}")
    return mapping

def load_gp_mapping():
    print(f"📖 Loading {GP_MAPPING_FILE}...")
    mapping = {}
    try:
        with open(GP_MAPPING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                v_code = row.get('Village Code', '').strip()
                gp_code = row.get('Local Body Code', '').strip()
                gp_name = row.get('Local Body Name (In English)', '').strip()
                
                if v_code and gp_name:
                    mapping[v_code] = {
                        'gp_code': gp_code,
                        'gp_name': gp_name
                    }
    except Exception as e:
        print(f"Error loading GP mapping: {e}")
    print(f"   Found GP data for {len(mapping)} villages.")
    return mapping

def load_shrug_data():
    print(f"📖 Loading {SHRUG_NAMES_FILE}...")
    census_to_shrid = {}
    relevant_shrids = set()
    
    try:
        with open(SHRUG_NAMES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row.get('state_name', '').lower().strip()
                if state == 'chhattisgarh':
                    shrid = row.get('shrid2', '')
                    if shrid:
                        parts = shrid.split('-')
                        if len(parts) > 0:
                            census_code = parts[-1]
                            census_to_shrid[census_code] = shrid
                            relevant_shrids.add(shrid)
    except Exception as e:
        print(f"Error loading SHRUG names: {e}")

    print(f"   Found {len(relevant_shrids)} locations in Chhattisgarh.")

    print(f"📖 Loading {SHRUG_STATS_FILE}...")
    shrid_to_coords = {}
    try:
        with open(SHRUG_STATS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                shrid = row.get('shrid2', '')
                if shrid in relevant_shrids:
                    try:
                        lat = float(row.get('latitude', 0))
                        lng = float(row.get('longitude', 0))
                        if lat != 0 and lng != 0:
                            shrid_to_coords[shrid] = {'latitude': lat, 'longitude': lng}
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Error loading SHRUG stats: {e}")
        
    print(f"   Found coordinates for {len(shrid_to_coords)} locations.")
    
    return census_to_shrid, shrid_to_coords

def load_ac_data():
    ac_names = {}
    print(f"📖 Loading {AC_NAME_KEY_FILE}...")
    try:
        with open(AC_NAME_KEY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('pc01_state_name', '').lower().strip() == 'chhattisgarh':
                    ac_names[row['ac08_id']] = row['ac08_name']
    except Exception as e:
        print(f"Error loading AC names: {e}")
    
    shrid_to_ac = {}
    print(f"📖 Loading {SHRID_AC_KEY_FILE}...")
    try:
        with open(SHRID_AC_KEY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                shrid = row.get('shrid2')
                ac_id = row.get('ac08_id')
                if shrid and ac_id:
                    shrid_to_ac[shrid] = ac_id
    except Exception as e:
        print(f"Error loading SHRID AC key: {e}")
            
    return ac_names, shrid_to_ac

def enrich_and_rebuild():
    print("🚀 Starting Full Enrichment Process (with GP Data)...")
    
    # Load all data
    print(f"📖 Loading {HIERARCHY_FILE}...")
    with open(HIERARCHY_FILE, 'r', encoding='utf-8') as f:
        old_hierarchy = json.load(f)
        
    lgd_to_census = load_lgd_mapping()
    gp_mapping = load_gp_mapping()
    census_to_shrid, shrid_to_coords = load_shrug_data()
    ac_names, shrid_to_ac = load_ac_data()
    
    # New Hierarchy
    new_hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    stats = {
        'total': 0,
        'coords_found': 0,
        'ac_found': 0,
        'gp_found': 0,
        'moved': 0
    }
    
    print("🔄 Processing Hierarchy...")
    for district_name, ac_dict in old_hierarchy.items():
        for old_ac_name, block_dict in ac_dict.items():
            for block_name, village_list in block_dict.items():
                for village in village_list:
                    stats['total'] += 1
                    lgd_code = str(village.get('code'))
                    
                    # 2. Get Census Code
                    census_code = lgd_to_census.get(lgd_code)
                    
                    target_ac_name = old_ac_name
                    
                    if census_code:
                        # 1. Get GP Data (using census_code for new gp_map)
                        if census_code in gp_mapping:
                            gp_data = gp_mapping[census_code]
                            village['gp_name'] = gp_data['gp_name']
                            village['gp_code'] = gp_data['gp_code']
                            stats['gp_found'] += 1

                        # 3. Get SHRID
                        shrid = census_to_shrid.get(census_code)
                        
                        if shrid:
                            village['shrid2'] = shrid
                            
                            # 4. Get Coords
                            coords = shrid_to_coords.get(shrid)
                            if coords:
                                village['lat'] = coords['latitude']
                                village['lng'] = coords['longitude']
                                stats['coords_found'] += 1
                            
                            # 5. Get AC
                            ac_id = shrid_to_ac.get(shrid)
                            if ac_id and ac_id in ac_names:
                                shrug_ac_name = ac_names[ac_id]
                                village['shrug_ac_id'] = ac_id
                                village['shrug_ac_name'] = shrug_ac_name
                                
                                # Normalize for comparison
                                if shrug_ac_name.lower().strip() != old_ac_name.lower().strip():
                                    stats['moved'] += 1
                                
                                target_ac_name = shrug_ac_name
                                stats['ac_found'] += 1
                    
                    # Clean up AC name (Title Case)
                    target_ac_name = target_ac_name.title()
                    
                    # Insert into new hierarchy
                    new_hierarchy[district_name][target_ac_name][block_name].append(village)

    print(f"📊 Stats:")
    print(f"   Total Villages: {stats['total']}")
    print(f"   GP Data Found: {stats['gp_found']} ({stats['gp_found']/stats['total']*100:.1f}%)")
    print(f"   Coords Found: {stats['coords_found']} ({stats['coords_found']/stats['total']*100:.1f}%)")
    print(f"   AC Data Found: {stats['ac_found']} ({stats['ac_found']/stats['total']*100:.1f}%)")
    print(f"   Villages Moved to Correct AC: {stats['moved']}")
    
    # Convert to regular dict
    final_hierarchy = {
        d: {
            a: {
                b: v_list 
                for b, v_list in b_dict.items()
            }
            for a, b_dict in a_dict.items()
        }
        for d, a_dict in new_hierarchy.items()
    }
    
    print(f"💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_hierarchy, f, indent=2, ensure_ascii=False)
    print("✅ Done.")

if __name__ == "__main__":
    enrich_and_rebuild()
