
import pandas as pd
import json
import re
import os
from pathlib import Path

# --- Helper Functions (from parse_v5.py) ---

NUKTA_MAP = str.maketrans({
  'क़':'क','ख़':'ख','ग़':'ग','ज़':'ज','फ़':'फ','ड़':'ड','ढ़':'ढ','ऱ':'र','य़':'य'
})

COMBINING = re.compile(r"[\u093C\u094D\u200C\u200D\uFE00-\uFE0F]")
MATRA_MAP = {
  'ा': 'aa', 'ि': 'i', 'ी': 'ii', 'ु': 'u', 'ू': 'uu',
  'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ृ': 'ri',
  'ॉ': 'o', 'ॅ': 'ae'
}

def fold_nukta(s: str) -> str:
  if not isinstance(s, str): return ""
  return COMBINING.sub('', s.translate(NUKTA_MAP))

def translit_basic(dev: str) -> str:
  if not isinstance(dev, str): return ""
  # Minimal conservative transliteration
  m = {
    'अ':'a','आ':'aa','इ':'i','ई':'ii','उ':'u','ऊ':'uu','ए':'e','ऐ':'ai','ओ':'o','औ':'au',
    'क':'k','ख':'kh','ग':'g','घ':'gh','च':'ch','छ':'chh','ज':'j','झ':'jh','ट':'t','ठ':'th','ड':'d','ढ':'dh','ण':'n',
    'त':'t','थ':'th','द':'d','ध':'dh','न':'n','प':'p','फ':'ph','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'v','श':'sh','ष':'sh','स':'s','ह':'h'
  }
  out = []
  for ch in dev:
    if ch in MATRA_MAP:
      out.append(MATRA_MAP[ch])
    else:
      out.append(m.get(ch, ch))
  return ''.join(out)

# --- Main Conversion Logic ---

import difflib

INPUT_FILE = 'Chhattisgarh_District to Ward Mapping_Ward Name Mapping.xlsx'
OUTPUT_FILE = 'data/datasets/chhattisgarh_wards.ndjson'
URBAN_FILE = 'data/datasets/chhattisgarh_urban.ndjson'

def load_urban_data():
    urban_map = {} # Hindi -> {english, hindi}
    if not os.path.exists(URBAN_FILE):
        print(f"Warning: {URBAN_FILE} not found. Skipping normalization.")
        return urban_map
        
    with open(URBAN_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            # Keys: ulb (Hindi), hierarchy (English last element)
            hindi_name = data.get('ulb') or data.get('nagar_nigam') or data.get('nagar_palika')
            
            # Extract English name from hierarchy or construct it?
            # Hierarchy: ["Chhattisgarh", "District", "ULB"]
            english_name = data.get('hierarchy', [])[-1] if data.get('hierarchy') else None
            
            if hindi_name and english_name:
                urban_map[hindi_name] = {
                    'hindi': hindi_name,
                    'english': english_name
                }
    return urban_map

def normalize_ulb(name_hindi, urban_map):
    if not urban_map:
        return name_hindi, None
        
    if name_hindi in urban_map:
        return urban_map[name_hindi]['hindi'], urban_map[name_hindi]['english']
        
    # Fuzzy match
    matches = difflib.get_close_matches(name_hindi, urban_map.keys(), n=1, cutoff=0.8)
    if matches:
        match = matches[0]
        return urban_map[match]['hindi'], urban_map[match]['english']
        
    return name_hindi, None

def convert():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    print("Loading urban data for normalization...")
    urban_map = load_urban_data()
    print(f"Loaded {len(urban_map)} ULBs.")

    print(f"Reading {INPUT_FILE}...")
    # Read header from row 0, data starts from row 1. But row 0 in pandas is the header. 
    # The file has a sub-header in row 1 (index 0 of data). We should filter it out.
    df = pd.read_excel(INPUT_FILE)
    
    # Expected columns: 'क्रमांक', 'संभाग', 'जिला', 'निकाय का प्रकार', 'निकाय का नाम', 'वार्ड क्रमांक', 'वार्ड का नाम'
    
    records_map = {} # Key: (District, ULB, WardNo) -> Record
    
    for _, row in df.iterrows():
        try:
            # Skip rows where 'क्रमांक' is NaN (like the sub-header row)
            if pd.isna(row['क्रमांक']):
                continue

            district_hindi = str(row['जिला']).strip()
            ulb_hindi_raw = str(row['निकाय का नाम']).strip()
            ward_no = str(row['वार्ड क्रमांक']).strip()
            if ward_no.endswith('.0'): ward_no = ward_no[:-2] # Fix float conversion
            
            ward_name_raw = str(row['वार्ड का नाम']).strip() if not pd.isna(row['वार्ड का नाम']) else ""
            
            # Normalize ULB Name
            ulb_hindi, ulb_english = normalize_ulb(ulb_hindi_raw, urban_map)
            
            # Generate English/Transliterated names
            district_english = translit_basic(fold_nukta(district_hindi)).title()
            if not ulb_english:
                ulb_english = translit_basic(fold_nukta(ulb_hindi)).title()
            
            # Construct Ward Names
            # Use actual ward name if available, else fallback to Number
            ward_name_hindi = ward_name_raw if ward_name_raw else f"वार्ड क्रमांक {ward_no}"
            ward_name_hindi_nukta = fold_nukta(ward_name_hindi)
            
            ward_name_english = translit_basic(ward_name_hindi_nukta).title() if ward_name_raw else f"Ward Number {ward_no}"
            ward_name_transliterated = translit_basic(ward_name_hindi_nukta) # Raw transliteration
            
            # Refinement: Replace "Vaard" with "Ward"
            ward_name_english = ward_name_english.replace("Vaard", "Ward")
            ward_name_transliterated = ward_name_transliterated.replace("Vaard", "Ward")
            
            # Create Record
            record = {
                "type": "ward",
                "ward_no": ward_no,
                "name_hindi": ward_name_hindi,
                "name_hindi_nukta": ward_name_hindi_nukta,
                "name_english": ward_name_english,
                "name_transliterated": ward_name_transliterated,
                "ulb_hindi": ulb_hindi,
                "ulb_english": ulb_english,
                "district_hindi": district_hindi,
                "district_english": district_english,
                "hierarchy": ["Chhattisgarh", district_english, ulb_english, ward_name_english],
                "variants": [
                    ward_name_hindi,
                    ward_name_hindi_nukta,
                    ward_name_english,
                    ward_name_transliterated,
                    f"Ward {ward_no}",
                    f"Ward No {ward_no}",
                    f"वार्ड {ward_no}",
                    f"वार्ड क्रमांक {ward_no}"
                ]
            }
            
            # Duplicate Handling
            key = (district_english, ulb_english, ward_no)
            if key in records_map:
                # If existing record has generic name and new one has specific name, replace it
                existing = records_map[key]
                if "Ward Number" in existing['name_english'] and "Ward Number" not in ward_name_english:
                    records_map[key] = record
            else:
                records_map[key] = record
            
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue
            
    records = list(records_map.values())
    print(f"Generated {len(records)} unique ward records.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
    print("Done.")

if __name__ == "__main__":
    convert()
