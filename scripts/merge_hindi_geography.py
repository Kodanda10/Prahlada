#!/usr/bin/env python3
"""
Hindi Geography Data Merge Script

This script merges Hindi names from chhattisgarh_complete_geography.json
into chhattisgarh_hierarchy_enriched.json to create a bilingual dataset.

Output: chhattisgarh_hierarchy_hindi.json with both English and Hindi names
"""

import json
import os
from difflib import SequenceMatcher
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
PUBLIC_DIR = BASE_DIR / "public"

HINDI_SOURCE = PUBLIC_DIR / "chhattisgarh_complete_geography.json"
ENGLISH_SOURCE = PUBLIC_DIR / "chhattisgarh_hierarchy_enriched.json"
OUTPUT_FILE = PUBLIC_DIR / "chhattisgarh_hierarchy_hindi.json"


def normalize(s: str) -> str:
    """Normalize string for fuzzy matching"""
    if not s:
        return ""
    return s.lower().strip().replace(" ", "").replace("-", "")


def similar(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def find_best_match(target: str, candidates: list, threshold: float = 0.6) -> tuple:
    """Find best matching string from candidates"""
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        if isinstance(candidate, dict):
            name = candidate.get("name", "")
        else:
            name = candidate
        
        score = similar(target, name)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    return best_match, best_score


def build_hindi_mapping(hindi_data: dict) -> dict:
    """Build a lookup dictionary from Hindi geography data"""
    mapping = {
        "districts": {},  # English name -> Hindi name
        "blocks": {},
        "villages": {}
    }
    
    # District level mapping
    for district in hindi_data.get("districts", []):
        hindi_name = district.get("name", "")
        # Try to infer English name from common patterns
        mapping["districts"][hindi_name] = hindi_name
        
        for ac in district.get("acs", []):
            for block in ac.get("blocks", []):
                block_name_hi = block.get("name", "")
                mapping["blocks"][block_name_hi] = block_name_hi
                
                for gp in block.get("gps", []):
                    for village in gp.get("villages", []):
                        village_name_hi = village.get("name", "")
                        mapping["villages"][village_name_hi] = village_name_hi
    
    return mapping


# Manual English -> Hindi mapping for districts (most reliable)
DISTRICT_MAPPING = {
    "Balod": "बलोद",
    "Baloda Bazar": "बलौदा बाजार",
    "Balrampur": "बलरामपुर",
    "Bastar": "बस्तर",
    "Bemetara": "बेमेतरा",
    "Bijapur": "बीजापुर",
    "Bilaspur": "बिलासपुर",
    "Dantewada": "दंतेवाड़ा",
    "Dhamtari": "धमतरी",
    "Durg": "दुर्ग",
    "Gariaband": "गरियाबंद",
    "Gaurela-Pendra-Marwahi": "गौरेला-पेंड्रा-मरवाही",
    "Janjgir-Champa": "जांजगीर-चांपा",
    "Jashpur": "जशपुर",
    "Kabirdham": "कबीरधाम",
    "Kanker": "कांकेर",
    "Khairagarh-Chhuikhadan-Gandai": "खैरागढ़-छुईखदान-गंडई",
    "Kondagaon": "कोंडागांव",
    "Korba": "कोरबा",
    "Koriya": "कोरिया",
    "Mahasamund": "महासमुंद",
    "Manendragarh-Chirmiri-Bharatpur": "मनेंद्रगढ़-चिरमिरी-भरतपुर",
    "Mohla-Manpur-Ambagarh Chowki": "मोहला-मानपुर-अंबागढ़ चौकी",
    "Mungeli": "मुंगेली",
    "Narayanpur": "नारायणपुर",
    "Raigarh": "रायगढ़",
    "Raipur": "रायपुर",
    "Rajnandgaon": "राजनांदगांव",
    "Sarangarh-Bilaigarh": "सारंगढ़-बिलाईगढ़",
    "Sakti": "सक्ती",
    "Sukma": "सुकमा",
    "Surajpur": "सूरजपुर",
    "Surguja": "सरगुजा",
}

# Common block name patterns
BLOCK_MAPPING = {
    "Balod": "बलोद",
    "Dondi": "डोंडी",
    "Dondi Lohara": "डोंडी लोहारा",
    "Dondilohara": "डोंडीलोहारा",
    "Gurur": "गुरूर",
    "Gunderdehi": "गुंडरदेही",
    "Durg": "दुर्ग",
    "Bhilai": "भिलाई",
    "Patan": "पाटन",
    "Dhamdha": "धमधा",
    "Raipur": "रायपुर",
    "Arang": "अरंग",
    "Abhanpur": "आभनपुर",
    "Tilda": "तिल्दा",
    "Bilaspur": "बिलासपुर",
    "Takhatpur": "तखतपुर",
    "Masturi": "मस्तूरी",
    "Kota": "कोटा",
    "Jagdalpur": "जगदलपुर",
    "Bastar": "बस्तर",
    "Tokapal": "तोकापाल",
    "Lohandiguda": "लोहंडीगुड़ा",
    "Kondagaon": "कोंडागांव",
    "Narayanpur": "नारायणपुर",
    "Kanker": "कांकेर",
    "Antagarh": "अंतागढ़",
    "Bhanupratappur": "भानुप्रतापपुर",
    "Dantewada": "दंतेवाड़ा",
    "Geedam": "गीदम",
    "Katekalyan": "काटेकल्याण",
    "Sukma": "सुकमा",
    "Bijapur": "बीजापुर",
    "Bhairamgarh": "भैरमगढ़",
    "Korba": "कोरबा",
    "Katghora": "कटघोरा",
    "Pali": "पाली",
    "Raigarh": "रायगढ़",
    "Gharghoda": "घरघोड़ा",
    "Dharamjaigarh": "धरमजयगढ़",
    "Jashpur": "जशपुर",
    "Kunkuri": "कुनकुरी",
    "Bagicha": "बगीचा",
    "Surguja": "सरगुजा",
    "Ambikapur": "अंबिकापुर",
    "Sitapur": "सीतापुर",
    "Surajpur": "सूरजपुर",
    "Premnagar": "प्रेमनगर",
    "Baikunthpur": "बैकुंठपुर",
    "Koriya": "कोरिया",
    "Manendragarh": "मनेंद्रगढ़",
    "Dhamtari": "धमतरी",
    "Kurud": "कुरुद",
    "Magarlod": "मगरलोड",
    "Nagri": "नगरी",
    "Rajnandgaon": "राजनांदगांव",
    "Dongargarh": "डोंगरगढ़",
    "Khairagarh": "खैरागढ़",
    "Chhuria": "छुरिया",
    "Kabirdham": "कबीरधाम",
    "Kawardha": "कवर्धा",
    "Pandariya": "पंडरिया",
    "Bodla": "बोदला",
    "Mahasamund": "महासमुंद",
    "Saraipali": "सरायपाली",
    "Bagbahra": "बागबहरा",
    "Pithora": "पिथौरा",
    "Gariaband": "गरियाबंद",
    "Mainpur": "मैनपुर",
    "Chhura": "छुरा",
    "Fingeshwar": "फिंगेश्वर",
    "Janjgir": "जांजगीर",
    "Champa": "चांपा",
    "Sakti": "सक्ती",
    "Akaltara": "अकलतरा",
    "Mungeli": "मुंगेली",
    "Lormi": "लोरमी",
    "Patharia": "पथरिया",
    "Bemetara": "बेमेतरा",
    "Saja": "साजा",
    "Berla": "बेरला",
    "Nawagarh": "नवागढ़",
    "Baloda Bazar": "बलौदा बाजार",
    "Bhatapara": "भाटापारा",
    "Simga": "सिमगा",
    "Kasdol": "कसडोल",
    "Pallari": "पल्लारी",
    "Sarangarh": "सारंगढ़",
    "Bilaigarh": "बिलाईगढ़",
    # Sanjari Balod Assembly Constituency
    "Sanjari Balod": "संजारी बालोद",
}


def merge_geography_data():
    """Main function to merge Hindi names into the hierarchy"""
    
    print("🔄 Loading source files...")
    
    # Load Hindi source
    if HINDI_SOURCE.exists():
        with open(HINDI_SOURCE, 'r', encoding='utf-8') as f:
            hindi_data = json.load(f)
        print(f"✅ Loaded Hindi source: {HINDI_SOURCE.name}")
    else:
        print(f"❌ Hindi source not found: {HINDI_SOURCE}")
        hindi_data = {}
    
    # Load English source
    if ENGLISH_SOURCE.exists():
        with open(ENGLISH_SOURCE, 'r', encoding='utf-8') as f:
            english_data = json.load(f)
        print(f"✅ Loaded English source: {ENGLISH_SOURCE.name}")
    else:
        print(f"❌ English source not found: {ENGLISH_SOURCE}")
        return
    
    # Build merged structure
    print("\n🔄 Merging data...")
    
    merged = {}
    stats = {"districts": 0, "acs": 0, "blocks": 0, "villages": 0}
    
    for district_en, district_data in english_data.items():
        # Get Hindi district name
        district_hi = DISTRICT_MAPPING.get(district_en, district_en)
        
        merged[district_en] = {
            "name_hi": district_hi,
            "acs": {}
        }
        stats["districts"] += 1
        
        for ac_en, ac_data in district_data.items():
            # Get Hindi AC name (try mapping, fallback to English)
            ac_hi = BLOCK_MAPPING.get(ac_en, ac_en)
            
            merged[district_en]["acs"][ac_en] = {
                "name_hi": ac_hi,
                "blocks": {}
            }
            stats["acs"] += 1
            
            for block_en, villages in ac_data.items():
                # Get Hindi block name
                block_hi = BLOCK_MAPPING.get(block_en, block_en)
                
                merged[district_en]["acs"][ac_en]["blocks"][block_en] = {
                    "name_hi": block_hi,
                    "villages": []
                }
                stats["blocks"] += 1
                
                # Process villages
                for village in villages:
                    village_name = village.get("name", "")
                    # For villages, use the name as-is or try mapping
                    village_hi = BLOCK_MAPPING.get(village_name, village_name)
                    
                    merged_village = {
                        **village,
                        "name_hi": village_hi
                    }
                    merged[district_en]["acs"][ac_en]["blocks"][block_en]["villages"].append(merged_village)
                    stats["villages"] += 1
    
    # Save merged file
    print(f"\n💾 Saving merged file to: {OUTPUT_FILE.name}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Merge complete!")
    print(f"   Districts: {stats['districts']}")
    print(f"   ACs: {stats['acs']}")
    print(f"   Blocks: {stats['blocks']}")
    print(f"   Villages: {stats['villages']}")
    
    return merged


if __name__ == "__main__":
    merge_geography_data()
