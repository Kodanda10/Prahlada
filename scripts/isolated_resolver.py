import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union, Set
from collections import Counter, defaultdict, deque

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Data files
FULL_VILLAGES_PATH = DATA_DIR / "full_villages.json"
CONSTITUENCIES_PATH = DATA_DIR / "constituencies.json"
URBAN_DATA_PATH = DATA_DIR / "datasets" / "chhattisgarh_urban.ndjson"
WARDS_PATH = DATA_DIR / "datasets" / "chhattisgarh_wards.ndjson"
LANDMARKS_PATH = DATA_DIR / "landmarks.json"

STATIC_LANDMARKS = {
    "Patna": "Patna",
    "पटना": "Patna",
    "Bankipur": "Patna",
    "बांकीपुर": "Patna",
    "Vidhan Sabha": "नवा रायपुर",
    "विधानसभा": "नवा रायपुर",
    "Mantralaya": "नवा रायपुर",
    "मंत्रालय": "नवा रायपुर",
    "High Court": "बिलासपुर",
    "हाई कोर्ट": "बिलासपुर",
    "Police Line": "रायगढ़",
    "पुलिस लाइन": "रायगढ़"
}

DICTIONARY_HIGH_CONFIDENCE = 0.88
LANDMARK_CONFIDENCE = 0.95

def load_ndjson(path: Union[str, Path]) -> List[Dict[str, Any]]:
    data = []
    if not Path(path).exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def load_json(path: Union[str, Path]) -> Any:
    if not Path(path).exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class GeoHierarchyResolver:
    """Resolve complete administrative hierarchy: District->Block->GP->Village/ULB->Ward"""
    
    def __init__(self):
        self.villages_data = self._load_villages_data()
        self.constituencies = load_json(CONSTITUENCIES_PATH)
        self.urban_data = self._load_urban_data()
        self.wards_data = self._load_wards_data()
        
        self.village_index = self._build_village_index()
        self.ward_index = {}
        self.ulb_index = self._build_ulb_index()
        self.district_map = self._build_district_map()
    
    def _load_villages_data(self) -> List[Dict]:
        if FULL_VILLAGES_PATH.exists():
            data = load_json(FULL_VILLAGES_PATH)
            return data.get("villages", [])
        return []

    def _load_urban_data(self) -> List[Dict]:
        if URBAN_DATA_PATH.exists():
            return load_ndjson(URBAN_DATA_PATH)
        return []

    def _load_wards_data(self) -> List[Dict]:
        if WARDS_PATH.exists():
            return load_ndjson(WARDS_PATH)
        return []

    def _build_village_index(self) -> Dict[str, Dict]:
        index = {}
        for row in self.villages_data:
            village = row.get("name")
            if village:
                index[village] = {
                    "district": row.get("district"),
                    "block": row.get("block"),
                    "gp": row.get("gram_panchayat"),
                    "assembly": row.get("assembly_constituency"),
                    "parliamentary": row.get("parliamentary_constituency"),
                    "hierarchy_path": [
                        "छत्तीसगढ़",
                        f"{row.get('district', '')} जिला",
                        row.get('assembly_constituency', ''),
                        f"{row.get('block', '')} ब्लॉक",
                        f"{row.get('gram_panchayat', '')} पंचायत"
                    ],
                    "type": "rural"
                }
        return index
    
    def _build_ulb_index(self) -> Dict[str, Dict]:
        index = {}
        districts = self.constituencies.get("districts", {})
        for dist_name, dist_data in districts.items():
            ulbs = dist_data.get("ulb_names", [])
            for ulb in ulbs:
                index[ulb] = {
                    "district": dist_name,
                    "ulb_type": "ULB",
                    "ward_count": 0,
                    "assembly": dist_data.get("assembly"),
                    "parliamentary": dist_data.get("parliamentary"),
                    "hierarchy_path": ["छत्तीसगढ़", f"{dist_name} जिला", ulb],
                    "type": "urban"
                }

        for row in self.urban_data:
            ulb = row.get("ulb") or row.get("nagar_nigam") or row.get("nagar_palika")
            if ulb:
                index[ulb] = {
                    "district": row.get("district"),
                    "ulb_type": row.get("ulb_type"),
                    "ward_count": row.get("ward_count", 0),
                    "assembly": row.get("assembly"),
                    "parliamentary": row.get("parliamentary"),
                    "hierarchy_path": [
                        "छत्तीसगढ़", 
                        f"{row.get('district', '')} जिला", 
                        ulb
                    ],
                    "type": "urban"
                }
        
        # Link Wards to ULBs and Build Ward Index
        for ward in self.wards_data:
            ulb_keys = [ward.get("ulb_english"), ward.get("ulb_hindi")]
            target_ulb = None
            
            for key in ulb_keys:
                if key and key in index:
                    target_ulb = key
                    break
            
            if target_ulb:
                if "wards" not in index[target_ulb]:
                    index[target_ulb]["wards"] = []
                index[target_ulb]["wards"].append(ward)
                
                if index[target_ulb].get("ward_count", 0) == 0:
                     index[target_ulb]["ward_count"] = len(index[target_ulb]["wards"])
                else:
                     index[target_ulb]["ward_count"] = len(index[target_ulb]["wards"])
                
                ulb_eng = ward.get("ulb_english")
                ulb_hin = ward.get("ulb_hindi")
                ward_no = ward.get("ward_no")
                
                ward_record = {
                    "district": index[target_ulb]["district"],
                    "ulb": target_ulb,
                    "ulb_type": index[target_ulb]["ulb_type"],
                    "ward_no": ward_no,
                    "ward_name": ward.get("name_english"),
                    "ward_name_hindi": ward.get("name_hindi"),
                    "hierarchy_path": index[target_ulb]["hierarchy_path"] + [ward.get("name_english")],
                    "type": "ward"
                }
                
                if ulb_eng:
                    self.ward_index[f"{ward.get('name_english')}, {ulb_eng}"] = ward_record
                    self.ward_index[f"Ward {ward_no}, {ulb_eng}"] = ward_record
                    self.ward_index[f"Ward Number {ward_no}, {ulb_eng}"] = ward_record
                
                if ulb_hin:
                    self.ward_index[f"{ward.get('name_hindi')}, {ulb_hin}"] = ward_record
                    self.ward_index[f"वार्ड {ward_no}, {ulb_hin}"] = ward_record
                    self.ward_index[f"वार्ड क्रमांक {ward_no}, {ulb_hin}"] = ward_record

        return index

    def _build_district_map(self) -> Dict[str, Dict]:
        index = {}
        districts = self.constituencies.get("districts", {})
        for dist_name, dist_data in districts.items():
            index[dist_name] = {
                "canonical": dist_name,
                "hierarchy": ["छत्तीसगढ़", f"{dist_name} जिला"],
                "assembly": dist_data.get("assembly"),
                "parliamentary": dist_data.get("parliamentary")
            }
            
        index["Patna"] = {
            "canonical": "Patna",
            "hierarchy": ["Bihar", "Patna"],
            "assembly": [],
            "parliamentary": []
        }
        return index
    
    def resolve_hierarchy(self, location_name: str, context_text: str = "") -> Optional[Dict]:
        if location_name in self.ward_index:
            w = self.ward_index[location_name]
            return {
                "district": w["district"],
                "ulb": w["ulb"],
                "ulb_type": w["ulb_type"],
                "ward": w["ward_no"],
                "ward_name": w["ward_name"],
                "hierarchy_path": w["hierarchy_path"],
                "canonical": f"{w['ward_name']}, {w['ulb']}",
                "canonical_key": f"CG_WARD_{w['ulb']}_{w['ward_no']}",
                "location_type": "ward",
                "source": "hierarchy_resolver"
            }

        if location_name in self.village_index:
            v = self.village_index[location_name]
            return {
                "district": v["district"],
                "assembly": v["assembly"],
                "parliamentary": v["parliamentary"],
                "block": v["block"],
                "gp": v["gp"],
                "village": location_name,
                "ulb": None,
                "ward": None,
                "zone": None,
                "hierarchy_path": [p for p in v["hierarchy_path"] if p],
                "canonical": location_name,
                "canonical_key": f"CG_VILLAGE_{location_name}",
                "location_type": "rural",
                "source": "hierarchy_resolver"
            }
        
        if location_name in self.ulb_index:
            u = self.ulb_index[location_name]
            ward = self._extract_ward(context_text)
            zone = self._extract_zone(context_text)
            hierarchy = u["hierarchy_path"] + ([f"वार्ड {ward}"] if ward else [])
            
            loc_type = "urban"
            if location_name in ["नवा रायपुर", "अटल नगर"]:
                loc_type = "planned_city"
            
            return {
                "district": u["district"],
                "assembly": u["assembly"],
                "parliamentary": u["parliamentary"],
                "block": None,
                "gp": None,
                "village": None,
                "ulb": location_name,
                "ulb_type": u["ulb_type"],
                "ward": ward,
                "zone": zone,
                "hierarchy_path": [p for p in hierarchy if p],
                "canonical": location_name,
                "canonical_key": f"CG_ULB_{location_name}",
                "location_type": loc_type,
                "source": "hierarchy_resolver"
            }
        
        if location_name in self.district_map:
             d = self.district_map[location_name]
             return {
                "district": d["canonical"],
                "assembly": d["assembly"],
                "parliamentary": d["parliamentary"],
                "hierarchy_path": d["hierarchy"],
                "canonical": d["canonical"],
                "canonical_key": f"CG_DISTRICT_{d['canonical']}",
                "location_type": "district",
                "source": "hierarchy_resolver"
             }

        return None
    
    def _extract_ward(self, text: str) -> Optional[str]:
        patterns = [
            r"वार्ड[-–]?\s*(\d+)",
            r"Ward[-–]?\s*(\d+)",
            r"सेक्टर[-–]?\s*(\d+)",
            r"Sector[-–]?\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_zone(self, text: str) -> Optional[str]:
        return None # Simplified for isolation

class HybridLocationResolver:
    def __init__(self, enable_semantic=False):
        self.enable_semantic = False # Disabled for isolation
        self.semantic_linker = None
        self.trace_log = []
        self.geo_resolver = GeoHierarchyResolver()
        self.landmarks = load_json(LANDMARKS_PATH)
        
    def resolve(self, text: str, entities: List[str] = None) -> Tuple[Optional[Dict], float, str]:
        self.trace_log = []
        
        landmark_loc = self._landmark_lookup(text)
        if landmark_loc:
            self.trace_log.append(f"Landmark found: {landmark_loc['canonical']}")
            return landmark_loc, LANDMARK_CONFIDENCE, "landmark_oracle"
            
        candidates = self._extract_location_candidates(text)
        print(f"DEBUG: Candidates: {candidates}")
        for cand in candidates:
            resolved = self.geo_resolver.resolve_hierarchy(cand, text)
            print(f"DEBUG: resolve_hierarchy('{cand}') -> {resolved}")
            if resolved:
                self.trace_log.append(f"Hierarchy match: {cand}")
                return resolved, DICTIONARY_HIGH_CONFIDENCE, "hierarchy_resolver"
        
        return None, 0.0, "none"

    def _landmark_lookup(self, text: str) -> Optional[Dict]:
        for landmark, city in STATIC_LANDMARKS.items():
            if landmark.lower() in text.lower():
                resolved = self.geo_resolver.resolve_hierarchy(city, text)
                if resolved:
                    resolved["landmark_trigger"] = landmark
                    return resolved
        return None

    def _extract_location_candidates(self, text: str) -> List[str]:
        candidates = []
        suffix_pattern = r"([\u0900-\u097FA-Za-z]+)(?:\s+में|\s+से|\s+के|\s+me|\s+se|\s+ke)"
        for match in re.finditer(suffix_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        admin_pattern = r"([\u0900-\u097FA-Za-z]+)\s+(?:जिला|विधानसभा|तहसील|थाना|ब्लॉक|पंचायत|नगर)"
        for match in re.finditer(admin_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        if hasattr(self.geo_resolver, 'district_map'):
            for dist in self.geo_resolver.district_map:
                if dist in text:
                    candidates.append(dist)
                    
        seen = set()
        unique_candidates = []
        for c in candidates:
            c_clean = c.strip().strip(",").strip()
            if c_clean and c_clean not in seen:
                seen.add(c_clean)
                unique_candidates.append(c_clean)
                
        return sorted(unique_candidates, key=len, reverse=True)

if __name__ == "__main__":
    print("🚀 Initializing Isolated Resolver...")
    resolver = HybridLocationResolver()
    
    test_cases = ["रायपुर", "नवा रायपुर", "Raipur"]
    
    for loc in test_cases:
        print(f"\n🔍 Testing: '{loc}'")
        res = resolver.geo_resolver.resolve_hierarchy(loc)
        print(f"   👉 resolve_hierarchy('{loc}') -> {res}")
        
        full_res, conf, source = resolver.resolve(f"{loc} में कार्यक्रम", [])
        print(f"   👉 resolve('{loc}') -> {full_res} (Source: {source})")
