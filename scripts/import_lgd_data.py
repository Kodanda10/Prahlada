import pandas as pd
import json
from pathlib import Path
import sys

def import_lgd_data():
    print("🚀 Starting LGD Data Import...")
    
    # Paths
    excel_path = Path("LGD_Chhattisgarh Complete Geographical Data/District_Subdistrict_Village_Gps_2025-11-27_01-45-36.xlsx")
    target_path = Path("data/full_villages.json")
    
    if not excel_path.exists():
        print(f"❌ Source file not found: {excel_path}")
        return
        
    print("📖 Reading Excel file (this may take a moment)...")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"❌ Failed to read Excel: {e}")
        return
        
    print(f"📊 Loaded {len(df)} rows.")
    
    # Normalize column names (strip whitespace, lowercase)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    print(f"   Columns: {list(df.columns)}")
    
    # Expected columns (based on typical LGD format, adjusting as needed)
    # We need: Village Name (English), Village Name (Local), District, Block, GP
    
    # Let's try to map columns
    # Assuming columns like: 'village_name_in_english', 'village_name_in_local_language', 'district_name_in_english', ...
    
    villages = []
    
    # Iterate and build village records
    # Using a set to track existing to avoid duplicates in this import
    seen_villages = set()
    
    for _, row in df.iterrows():
        # Adjust these keys based on actual column names printed above if it fails
        try:
            v_name_en = str(row.get('village_name_in_english', '')).strip()
            v_name_local = str(row.get('village_name_in_local_language', '')).strip()
            district = str(row.get('district_name_in_english', '')).strip()
            subdistrict = str(row.get('subdistrict_name_in_english', '')).strip() # Tehsil/Block
            block = str(row.get('block_name_in_english', '')).strip() # Might be different
            gp = str(row.get('gram_panchayat_name_in_english', '')).strip()
            
            if not v_name_en or v_name_en.lower() == 'nan':
                continue
                
            key = f"{district}|{subdistrict}|{v_name_en}"
            if key in seen_villages:
                continue
            seen_villages.add(key)
            
            record = {
                "name": v_name_en,
                "hindi": v_name_local if v_name_local and v_name_local.lower() != 'nan' else v_name_en,
                "district": district,
                "state": "Chhattisgarh",
                "block": block if block and block.lower() != 'nan' else subdistrict,
                "gram_panchayat": gp if gp and gp.lower() != 'nan' else None,
                "type": "village",
                "source": "LGD_2025"
            }
            villages.append(record)
            
        except Exception as e:
            continue
            
    print(f"✅ Extracted {len(villages)} unique villages.")
    
    # Load existing target
    if target_path.exists():
        with open(target_path, 'r') as f:
            target_data = json.load(f)
    else:
        target_data = {"villages": []}
        
    # Merge
    # We'll replace the entire list or append? 
    # If LGD is "Complete", maybe we should replace?
    # But we might have other custom data.
    # Let's append new ones.
    
    existing_keys = {f"{v.get('district')}|{v.get('block')}|{v.get('name')}" for v in target_data.get("villages", [])}
    
    added = 0
    for v in villages:
        key = f"{v.get('district')}|{v.get('block')}|{v.get('name')}"
        if key not in existing_keys:
            target_data["villages"].append(v)
            added += 1
            
    print(f"➕ Added {added} new villages to database.")
    
    # Save
    print("💾 Saving database...")
    with open(target_path, 'w') as f:
        json.dump(target_data, f, ensure_ascii=False, indent=2)
        
    print("✅ Done.")

if __name__ == "__main__":
    import_lgd_data()
