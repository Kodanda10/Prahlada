
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# Configuration
DATA_DIR = Path("data")
EMBEDDINGS_DIR = DATA_DIR / "embeddings" / "multilingual_geography"
MODEL_NAME = "intfloat/multilingual-e5-base"

# Input Files
FULL_VILLAGES_PATH = DATA_DIR / "full_villages.json"
URBAN_DATA_PATH = DATA_DIR / "datasets" / "chhattisgarh_urban.ndjson"
WARDS_PATH = DATA_DIR / "datasets" / "chhattisgarh_wards.ndjson"
CONSTITUENCIES_PATH = DATA_DIR / "constituencies.json"

def load_json(path):
    if not path.exists(): return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ndjson(path):
    data = []
    if not path.exists(): return []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def build_index():
    print(f"Loading data from {DATA_DIR}...")
    
    locations = []
    seen_names = set()

    def add_location(name):
        if name and name.strip() and name not in seen_names:
            locations.append(name.strip())
            seen_names.add(name.strip())

    # 1. Load Districts
    constituencies = load_json(CONSTITUENCIES_PATH)
    for dist in constituencies.get("districts", {}):
        add_location(dist)
        add_location(f"{dist} District")
        add_location(f"{dist} जिला")

    # 2. Load Villages
    villages = load_json(FULL_VILLAGES_PATH).get("villages", [])
    print(f"Processing {len(villages)} villages...")
    for v in villages:
        add_location(v.get("name"))
    
    # 3. Load Urban Bodies (ULBs)
    ulbs = load_ndjson(URBAN_DATA_PATH)
    print(f"Processing {len(ulbs)} ULBs...")
    for u in ulbs:
        add_location(u.get("ulb"))
        add_location(u.get("nagar_nigam"))
        add_location(u.get("nagar_palika"))
        
    # 4. Load Wards (NEW)
    wards = load_ndjson(WARDS_PATH)
    print(f"Processing {len(wards)} wards...")
    for w in wards:
        # Add "Ward X, ULB" combinations for better semantic matching
        ward_no = w.get("ward_no")
        ulb_eng = w.get("ulb_english")
        ulb_hin = w.get("ulb_hindi")
        
        # English Variants
        add_location(w.get("name_english"))
        add_location(w.get("name_transliterated"))
        if ulb_eng:
            add_location(f"{w.get('name_english')}, {ulb_eng}")
            add_location(f"{w.get('name_transliterated')}, {ulb_eng}")
            add_location(f"Ward {ward_no}, {ulb_eng}")
            
        # Hindi Variants
        add_location(w.get("name_hindi"))
        add_location(w.get("name_hindi_nukta"))
        if ulb_hin:
            add_location(f"{w.get('name_hindi')}, {ulb_hin}")
            add_location(f"{w.get('name_hindi_nukta')}, {ulb_hin}")
            add_location(f"वार्ड {ward_no}, {ulb_hin}")
            
    print(f"Total unique locations to index: {len(locations)}")
    
    # Generate Embeddings
    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Generating embeddings (this may take a while)...")
    embeddings = model.encode(locations, normalize_embeddings=True, show_progress_bar=True)
    
    # Build FAISS Index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    
    # Save Output
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    print(f"Saving to {EMBEDDINGS_DIR}...")
    
    # Save locations list
    with open(EMBEDDINGS_DIR / "locations.json", 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
        
    # Save raw embeddings
    np.save(EMBEDDINGS_DIR / "embeddings.npy", embeddings)
    
    # Save FAISS index
    faiss.write_index(index, str(EMBEDDINGS_DIR / "faiss_index.bin"))
    
    print("✅ Index rebuild complete!")

if __name__ == "__main__":
    build_index()
