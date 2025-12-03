import json
from pathlib import Path
import shutil

def import_data():
    print("🚀 Starting Raigarh Data Import...")
    
    # Paths
    source_path = Path("KnowledgeBank/geo-data/raigarh_assembly_constituency_detailed.json")
    target_path = Path("data/full_villages.json")
    
    if not source_path.exists():
        print(f"❌ Source file not found: {source_path}")
        return
        
    if not target_path.exists():
        print(f"❌ Target file not found: {target_path}")
        return

    # Backup Target
    backup_path = target_path.with_suffix(".json.bak_import")
    shutil.copy(target_path, backup_path)
    print(f"📦 Backed up target to {backup_path}")

    # Load Source
    with open(source_path, 'r') as f:
        source_data = json.load(f)
        
    # Load Target
    with open(target_path, 'r') as f:
        target_data = json.load(f)
        
    existing_villages = {v.get("name") for v in target_data.get("villages", [])}
    print(f"📋 Existing villages: {len(existing_villages)}")
    
    # Transform and Add
    new_villages = []
    
    ac_name = source_data.get("assembly_constituency", "Raigarh")
    blocks = source_data.get("blocks", {})
    
    for block_name, block_data in blocks.items():
        gps = block_data.get("gram_panchayats", {})
        for gp_name, villages_list in gps.items():
            # Deduplicate villages in the list
            unique_villages = set(villages_list)
            
            for v_name in unique_villages:
                if v_name not in existing_villages:
                    # Create new village record
                    new_record = {
                        "name": v_name,
                        # "hindi": v_name, # We don't have Hindi name in source, use English
                        "district": "Raigarh", # Inferred
                        "state": "Chhattisgarh",
                        "assembly_constituency": ac_name,
                        "block": block_name,
                        "gram_panchayat": gp_name,
                        "type": "village",
                        "source": "imported_raigarh_data"
                    }
                    new_villages.append(new_record)
                    existing_villages.add(v_name)
                    
    print(f"➕ Found {len(new_villages)} new villages to add.")
    
    if new_villages:
        target_data["villages"].extend(new_villages)
        
        with open(target_path, 'w') as f:
            json.dump(target_data, f, ensure_ascii=False, indent=2)
            
        print("✅ Import complete and saved.")
    else:
        print("⚠️  No new data to import.")

if __name__ == "__main__":
    import_data()
