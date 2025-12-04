import json
import csv
import random
import os

# Files
HIERARCHY_FILE = 'public/chhattisgarh_hierarchy_enriched.json'
LGD_VILLAGE_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
OUTPUT_FILE = 'src/data/chhattisgarhHierarchy.json'

# Hindi District Map (English -> Hindi)
# Sourced from merge_villages_hindi.py (reversed)
DISTRICT_MAP_HINDI = {
    'Surguja': 'सरगुजा',
    'Ambikapur': 'अम्बिकापुर',
    'Kanker': 'कांकेर',
    'Uttar Bastar Kanker': 'उत्तर बस्तर कांकेर',
    'Kabirdham': 'कबीरधाम',
    'Kondagaon': 'कोंडागांव',
    'Korba': 'कोरबा',
    'Koriya': 'कोरिया',
    'Gariaband': 'गरियाबंद',
    'Gaurela Pendra Marwahi': 'गौरेला-पेंड्रा-मरवाही',
    'Jashpur': 'जशपुर',
    'Janjgir-Champa': 'जांजगीर-चांपा',
    'Dantewada': 'दंतेवाड़ा',
    'Dakshin Bastar Dantewada': 'दंतेवाड़ा',
    'Durg': 'दुर्ग',
    'Dhamtari': 'धमतरी',
    'Narayanpur': 'नारायणपुर',
    'Balrampur': 'बलरामपुर',
    'Balodabazar-Bhatapara': 'बलौदाबाजार-भाटापारा',
    'Bastar': 'बस्तर',
    'Bilaspur': 'बिलासपुर',
    'Bijapur': 'बीजापुर',
    'Manendragarh-Chirmiri-Bharatpur': 'मनेंद्रगढ़-चिरमिरी-भरतपुर',
    'Mahasamund': 'महासमुंद',
    'Mungeli': 'मुंगेली',
    'Rajnandgaon': 'राजनांदगांव',
    'Raigarh': 'रायगढ़',
    'Raipur': 'रायपुर',
    'Sukma': 'सुकमा',
    'Surajpur': 'सूरजपुर',
    'Balod': 'बालोद',
    'Bemetara': 'बेमेतरा',
    'Sakti': 'सक्ती',
    'Mohla-Manpur-Ambagarh Chowki': 'मोहला-मानपुर-अंबागढ़ चौकी',
    'Khairagarh-Chhuikhadan-Gandai': 'खैरागढ़-छुईखदान-गंडई',
    'Sarangarh-Bilaigarh': 'सारंगढ़-बिलाईगढ़'
}

def normalize(text):
    return text.strip().lower() if text else ""

def load_hindi_mappings():
    print("📖 Loading Hindi mappings from LGD CSV...")
    village_code_map = {} # Code -> Hindi
    english_name_map = {} # English -> Hindi (Proxy)
    
    try:
        with open(LGD_VILLAGE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                v_code = row.get('Village Code')
                v_name_local = row.get('Village Name (In Local)')
                v_name_eng = row.get('Village Name (In English)')
                
                if v_code and v_name_local:
                    village_code_map[str(v_code)] = v_name_local
                
                if v_name_eng and v_name_local:
                    norm_eng = normalize(v_name_eng)
                    # Prefer shorter/simpler names if duplicates? Or just overwrite.
                    english_name_map[norm_eng] = v_name_local
                    
    except Exception as e:
        print(f"❌ Error loading LGD CSV: {e}")
        
    print(f"✅ Loaded {len(village_code_map)} village codes and {len(english_name_map)} name proxies.")
    return village_code_map, english_name_map

def generate_data():
    print("🚀 Generating Project Dhruv Hierarchy Data...")
    
    # 1. Load Mappings
    v_code_map, name_proxy_map = load_hindi_mappings()
    
    # 2. Load Hierarchy
    with open(HIERARCHY_FILE, 'r') as f:
        hierarchy = json.load(f)
        
    output_list = []
    
    # 3. Traverse and Subset
    # Hierarchy: District -> AC -> Block -> Village
    # Dhruv: District -> AC -> GP -> Village
    # Wait, existing hierarchy is District -> AC -> Block -> Village
    # But Dhruv wants GP level.
    # My enriched hierarchy HAS 'gp_name' and 'gp_code' in the Village object.
    # So I can group villages by GP within an AC?
    # Actually, the hierarchy is District -> AC -> Block -> Village.
    # GPs are attributes of villages.
    # I need to restructure: District -> AC -> GP -> Village.
    # I will aggregate GPs from the villages in the selected ACs.
    
    districts = list(hierarchy.keys())
    print(f"📍 Found {len(districts)} Districts.")
    
    for dist_name in districts:
        # District Node
        dist_hindi = DISTRICT_MAP_HINDI.get(dist_name, dist_name)
        # Centroid? We don't have district centroids in hierarchy.
        # We can compute from children.
        # For now, placeholder or compute later.
        # Let's compute centroid from the first few villages we find.
        
        dist_node = {
            "id": f"dist_{normalize(dist_name)}",
            "name": dist_hindi,
            "lat": 0, "lon": 0, # Compute
            "type": "district",
            "parentId": None
        }
        
        # Select 1-2 ACs
        acs = list(hierarchy[dist_name].keys())
        selected_acs = acs[:2] # Deterministic subset (first 2)
        
        ac_nodes = []
        gp_nodes = []
        village_nodes = []
        
        dist_lat_sum = 0
        dist_lon_sum = 0
        dist_count = 0
        
        for ac_name in selected_acs:
            # AC Node
            ac_hindi = name_proxy_map.get(normalize(ac_name), ac_name)
            ac_id = f"ac_{normalize(ac_name)}"
            
            ac_node = {
                "id": ac_id,
                "name": ac_hindi,
                "lat": 0, "lon": 0,
                "type": "ac",
                "parentId": dist_node["id"]
            }
            
            # Get all villages in this AC (across blocks)
            # Hierarchy: AC -> Block -> Villages
            blocks = hierarchy[dist_name][ac_name]
            all_villages_in_ac = []
            for block_name in blocks:
                all_villages_in_ac.extend(blocks[block_name])
                
            # Group by GP
            gps = {} # gp_code -> {name, villages[]}
            for v in all_villages_in_ac:
                gp_code = v.get('gp_code')
                gp_name = v.get('gp_name')
                if gp_code and gp_name:
                    if gp_code not in gps:
                        gps[gp_code] = {'name': gp_name, 'villages': []}
                    gps[gp_code]['villages'].append(v)
            
            # Select 1-2 GPs
            selected_gp_codes = list(gps.keys())[:2]
            
            ac_lat_sum = 0
            ac_lon_sum = 0
            ac_count = 0
            
            for gp_code in selected_gp_codes:
                gp_data = gps[gp_code]
                gp_name_eng = gp_data['name']
                gp_hindi = name_proxy_map.get(normalize(gp_name_eng), gp_name_eng)
                gp_id = f"gp_{gp_code}"
                
                gp_node = {
                    "id": gp_id,
                    "name": gp_hindi,
                    "lat": 0, "lon": 0,
                    "type": "gp",
                    "parentId": ac_id
                }
                
                # Select 2-3 Villages
                selected_villages = gp_data['villages'][:3]
                
                gp_lat_sum = 0
                gp_lon_sum = 0
                gp_v_count = 0
                
                for v in selected_villages:
                    v_code = v.get('code')
                    v_name_eng = v.get('name')
                    v_hindi = v_code_map.get(str(v_code), v_name_eng) # Try code first
                    if v_hindi == v_name_eng: # Fallback to proxy
                         v_hindi = name_proxy_map.get(normalize(v_name_eng), v_name_eng)
                         
                    lat = v.get('lat')
                    lng = v.get('lng')
                    
                    if lat and lng:
                        v_node = {
                            "id": f"vil_{v_code}",
                            "name": v_hindi,
                            "lat": lat,
                            "lon": lng,
                            "type": "village",
                            "parentId": gp_id
                        }
                        village_nodes.append(v_node)
                        
                        gp_lat_sum += lat
                        gp_lon_sum += lng
                        gp_v_count += 1
                
                if gp_v_count > 0:
                    gp_node['lat'] = gp_lat_sum / gp_v_count
                    gp_node['lon'] = gp_lon_sum / gp_v_count
                    gp_nodes.append(gp_node)
                    
                    ac_lat_sum += gp_node['lat']
                    ac_lon_sum += gp_node['lon']
                    ac_count += 1
            
            if ac_count > 0:
                ac_node['lat'] = ac_lat_sum / ac_count
                ac_node['lon'] = ac_lon_sum / ac_count
                ac_nodes.append(ac_node)
                
                dist_lat_sum += ac_node['lat']
                dist_lon_sum += ac_node['lon']
                dist_count += 1
        
        if dist_count > 0:
            dist_node['lat'] = dist_lat_sum / dist_count
            dist_node['lon'] = dist_lon_sum / dist_count
            output_list.append(dist_node)
            output_list.extend(ac_nodes)
            output_list.extend(gp_nodes)
            output_list.extend(village_nodes)
            
    # 4. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated {len(output_list)} items in {OUTPUT_FILE}")
    
if __name__ == "__main__":
    generate_data()
