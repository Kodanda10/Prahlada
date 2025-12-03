import json
from pathlib import Path

def check_village():
    path = Path("data/full_villages.json")
    if not path.exists():
        print("File not found")
        return

    with open(path, 'r') as f:
        data = json.load(f)
        villages = data.get("villages", [])
        
    print(f"Total villages: {len(villages)}")
    
    target_sub = "कुकुर"
    target_en_sub = "Kukur"
    
    found = False
    for v in villages:
        name = v.get("name", "")
        if target_sub in name or target_en_sub in name:
            print(f"Found match: {v}")
            found = True
            
    if not found:
        print(f"❌ {target}/{target_en} NOT found in database.")

if __name__ == "__main__":
    check_village()
