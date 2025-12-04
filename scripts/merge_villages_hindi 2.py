import pandas as pd
import json
import os

# File Paths
LGD_VILLAGE_FILE = 'data/raw/LGD/Villageof_Specific_State_cached.csv'
CONSTITUENCY_FILE = 'data/raw/LGD/Constituency_Report_2025-11-27_01-47-58.xlsx'
BLOCK_MAPPING_FILE = 'data/raw/LGD/District_Village_Block_Gps_Mapping_cached.csv'
FULL_VILLAGES_FILE = 'data/full_villages.json'
OUTPUT_FILE = 'public/chhattisgarh_corrected_villages.json'

# Hindi to English District Map (Manual)
DISTRICT_MAP = {
    'अम्बिकापुर': 'Surguja', # Ambikapur is HQ of Surguja
    'सरगुजा': 'Surguja',
    'उत्तर बस्तर कांकेर': 'Kanker', # Or Uttar Bastar Kanker
    'कांकेर': 'Kanker',
    'कबीरधाम': 'Kabirdham', # Or Kabeerdham
    'कोंडागांव': 'Kondagaon',
    'कोरबा': 'Korba',
    'कोरिया': 'Koriya',
    'गरियाबंद': 'Gariaband', # Or Gariyaband
    'गौरेला-पेंड्रा-मरवाही': 'Gaurela Pendra Marwahi',
    'जशपुर': 'Jashpur',
    'जांजगीर-चांपा': 'Janjgir-Champa',
    'दंतेवाड़ा': 'Dantewada', # Or Dakshin Bastar Dantewada
    'दुर्ग': 'Durg',
    'धमतरी': 'Dhamtari',
    'नारायणपुर': 'Narayanpur',
    'बलरामपुर': 'Balrampur',
    'बलरामपुर-रामानुजगंज': 'Balrampur',
    'बलौदाबाजार-भाटापारा': 'Balodabazar-Bhatapara',
    'बस्तर': 'Bastar',
    'बिलासपुर': 'Bilaspur',
    'बीजापुर': 'Bijapur',
    'मनेंद्रगढ़-चिरमिरी-भरतपुर': 'Manendragarh-Chirmiri-Bharatpur', # Check spelling
    'महासमुंद': 'Mahasamund',
    'मुंगेली': 'Mungeli',
    'राजनांदगांव': 'Rajnandgaon',
    'रायगढ़': 'Raigarh',
    'रायपुर': 'Raipur',
    'रायपुर ग्रामीण': 'Raipur',
    'सुकमा': 'Sukma',
    'सूरजपुर': 'Surajpur',
    'बालोद': 'Balod',
    'बेमेतरा': 'Bemetara',
    'सक्ती': 'Sakti',
    'मोहला-मानपुर-अंबागढ़ चौकी': 'Mohla-Manpur-Ambagarh Chowki',
    'खैरागढ़-छुईखदान-गंडई': 'Khairagarh-Chhuikhadan-Gandai',
    'सारंगढ़-बिलाईगढ़': 'Sarangarh-Bilaigarh'
}

def normalize(text):
    if not isinstance(text, str):
        return ""
    return text.strip().lower()

def process_data():
    print("🚀 Starting Hindi-based Merge...")

    # 1. Load LGD Village Data (Hindi Name -> Code)
    print(f"📖 Loading {LGD_VILLAGE_FILE}...")
    df_lgd = pd.read_csv(LGD_VILLAGE_FILE)
    
    # Create lookup: (District_English_Norm, Village_Hindi_Norm) -> Village_Code
    lgd_lookup = {}
    for _, row in df_lgd.iterrows():
        d_name = normalize(row['District Name (In English)'])
        v_name = normalize(row['Village Name (In Local)'])
        v_code = str(row['Village Code'])
        lgd_lookup[(d_name, v_name)] = v_code
        
    print(f"✅ Created lookup with {len(lgd_lookup)} entries.")

    # 2. Load Full Villages (Lat/Long)
    print(f"📖 Loading {FULL_VILLAGES_FILE}...")
    with open(FULL_VILLAGES_FILE, 'r') as f:
        villages_json = json.load(f)['villages']
        
    # 3. Match and Extract Coordinates
    village_coords = {} # Village_Code -> {lat, lon, pop}
    matches = 0
    
    for v in villages_json:
        d_hindi = v.get('district', '')
        v_hindi = v.get('hindi', '') or v.get('name', '')
        
        d_english = DISTRICT_MAP.get(d_hindi)
        if not d_english:
            # Try direct match if already English?
            d_english = d_hindi 
            
        key = (normalize(d_english), normalize(v_hindi))
        
        if key in lgd_lookup:
            v_code = lgd_lookup[key]
            village_coords[v_code] = {
                'latitude': v.get('latitude'),
                'longitude': v.get('longitude'),
                'population': v.get('population_total')
            }
            matches += 1
            
    print(f"✅ Matched {matches}/{len(villages_json)} villages ({matches/len(villages_json)*100:.1f}%)")

    # 4. Load AC Mapping
    print(f"📖 Loading {CONSTITUENCY_FILE}...")
    df_ac = pd.read_excel(CONSTITUENCY_FILE, header=1)
    df_ac = df_ac[df_ac['Entity Type'] == 'Village']
    ac_map = dict(zip(df_ac['Entity Code'].astype(str), df_ac['Assembly Constituency Name']))

    # 5. Load Block Mapping
    print(f"📖 Loading {BLOCK_MAPPING_FILE}...")
    df_block = pd.read_csv(BLOCK_MAPPING_FILE)
    block_map = dict(zip(df_block['Village Code'].astype(str), df_block['Development Block Name  (In English)']))
    district_map_final = dict(zip(df_block['Village Code'].astype(str), df_block['District Name  (In English)']))
    village_name_map = dict(zip(df_block['Village Code'].astype(str), df_block['Village Name (In English)']))

    # 6. Build Final Dataset
    print("🔄 Building final dataset...")
    final_villages = []
    
    # Iterate over all LGD villages (to ensure we have correct hierarchy)
    # But we only keep those where we found coordinates? 
    # Or keep all and let them have null coords? 
    # For "Satellite View", we NEED coords. So only keep matched ones.
    
    for v_code, coords in village_coords.items():
        if v_code in ac_map and v_code in block_map:
            final_villages.append({
                'village_code': v_code,
                'name': village_name_map.get(v_code, 'Unknown'),
                'district': district_map_final.get(v_code, 'Unknown'),
                'assembly_constituency': ac_map.get(v_code, 'Unknown'),
                'block': block_map.get(v_code, 'Unknown'),
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'population_total': coords['population']
            })
            
    print(f"✅ Final dataset has {len(final_villages)} villages with full hierarchy and coordinates.")
    
    # 7. Save
    print(f"💾 Saving to {OUTPUT_FILE}...")
    output_data = {
        'state': 'Chhattisgarh',
        'total_villages': len(final_villages),
        'villages': final_villages
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    # Validation
    korba_villages = [v for v in final_villages if v['district'] == 'Korba']
    acs = set(v['assembly_constituency'] for v in korba_villages)
    print(f"🔍 Validation: Found {len(korba_villages)} villages in Korba.")
    print("Unique ACs in Korba:", sorted(list(acs)))

if __name__ == "__main__":
    process_data()
