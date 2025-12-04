import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union, Set
from collections import deque

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Data files
FULL_VILLAGES_PATH = DATA_DIR / "full_villages.json"
CONSTITUENCIES_PATH = DATA_DIR / "constituencies.json"
URBAN_DATA_PATH = DATA_DIR / "datasets" / "chhattisgarh_urban.ndjson"
WARDS_PATH = DATA_DIR / "datasets" / "chhattisgarh_wards.ndjson"
LANDMARKS_PATH = DATA_DIR / "landmarks.json"

# Static Landmarks (Hardcoded overrides/additions)
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
    "पुलिस लाइन": "रायगढ़",
    "Kukurda": "Kukurda",
    "कुकुर्दा": "Kukurda"
}

# Semantic Search Thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.75
SEMANTIC_LOCATION_LIMIT = 3

# Dictionary Lookup Thresholds
DICTIONARY_HIGH_CONFIDENCE = 0.88
LANDMARK_CONFIDENCE = 0.95

# Timeline Inference
TIMELINE_WINDOW_SIZE = 3
TIMELINE_TIME_WINDOW_HOURS = 4

# ==========================================
# SHARED UTILS
# ==========================================

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

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# ==========================================
# GEO HIERARCHY RESOLVER (Reused from V1)
# ==========================================

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
        # self.ward_index is already initialized in __init__
        for ward in self.wards_data:
            # Try to find ULB by English or Hindi name
            ulb_keys = [ward.get("ulb_english"), ward.get("ulb_hindi")]
            target_ulb = None
            
            for key in ulb_keys:
                if key and key in index:
                    target_ulb = key
                    break
            
            if target_ulb:
                # Add to ULB
                if "wards" not in index[target_ulb]:
                    index[target_ulb]["wards"] = []
                index[target_ulb]["wards"].append(ward)
                
                # Update ward count
                if index[target_ulb].get("ward_count", 0) == 0:
                     index[target_ulb]["ward_count"] = len(index[target_ulb]["wards"])
                else:
                     index[target_ulb]["ward_count"] = len(index[target_ulb]["wards"])
                
                # Add to Ward Index
                # Index by "Ward Name, ULB" and "Ward X, ULB"
                # These keys MUST match what FAISS/Search returns
                ulb_eng = ward.get("ulb_english")
                ulb_hin = ward.get("ulb_hindi")
                ward_no = ward.get("ward_no")
                
                ward_record = {
                    "district": index[target_ulb]["district"],
                    "ulb": target_ulb, # Hindi name usually
                    "ulb_type": index[target_ulb]["ulb_type"],
                    "ward_no": ward_no,
                    "ward_name": ward.get("name_english"),
                    "ward_name_hindi": ward.get("name_hindi"),
                    "hierarchy_path": index[target_ulb]["hierarchy_path"] + [ward.get("name_english")],
                    "type": "ward"
                }
                
                # English Keys
                if ulb_eng:
                    self.ward_index[f"{ward.get('name_english')}, {ulb_eng}"] = ward_record
                    self.ward_index[f"Ward {ward_no}, {ulb_eng}"] = ward_record
                    self.ward_index[f"Ward Number {ward_no}, {ulb_eng}"] = ward_record
                
                # Hindi Keys
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
            
        # Add External Locations (e.g. Patna) manually
        index["Patna"] = {
            "canonical": "Patna",
            "hierarchy": ["Bihar", "Patna"],
            "assembly": [],
            "parliamentary": []
        }
        return index
    
    def resolve_hierarchy(self, location_name: str, context_text: str = "") -> Optional[Dict]:
        # 0. Check Ward Index (Most Specific)
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
            
            # P5: Planned city type for Nava Raipur
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
        # P2: Enhanced ward/sector extraction
        # Pattern: वार्ड 12, Ward 5, सेक्टर-21
        patterns = [
            r"वार्ड[-–]?\s*(\d+)",
            r"Ward[-–]?\s*(\d+)",
            r"सेक्टर[-–]?\s*(\d+)",  # V2.1: Sector support
            r"Sector[-–]?\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_zone(self, text: str) -> Optional[str]:
        # P2: Enhanced zone extraction
        # Pattern: जोन A, Zone 3, ब्लॉक-B
        patterns = [
            r"जोन[-–]?\s*([A-Za-z\d]+)",
            r"Zone[-–]?\s*([A-Za-z\d]+)",
            r"ब्लॉक[-–]?\s*([A-Za-z\d]+)",  # V2.1: Block support
            r"Block[-–]?\s*([A-Za-z\d]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

# ==========================================
# TIMELINE INFERENCE ENGINE
# ==========================================

class TimelineInference:
    """
    The 'Ghost' Logic: Infers location from recent context.
    """
    def __init__(self):
        self.history = deque(maxlen=TIMELINE_WINDOW_SIZE) # Stores (timestamp, location_dict)

    def update(self, timestamp: str, location: Optional[Dict]):
        if location and timestamp:
            self.history.append((timestamp, location))

    def infer(self, current_timestamp: str) -> Optional[Dict]:
        """
        Check history for a valid location within the time window.
        """
        if not self.history or not current_timestamp:
            return None
        
        # Simple string comparison for now (assuming ISO format)
        # In production, use datetime objects
        
        # Look backwards
        for ts, loc in reversed(self.history):
            # Calculate time difference (simplified)
            # If within window (approx check), return loc
            # For now, just return the most recent valid location
            return {
                **loc,
                "source": "temporal_inference",
                "confidence_penalty": 0.4 # Reduce confidence for inferred locs
            }
        return None

# ==========================================
# HYBRID LOCATION RESOLVER (V2)
# ==========================================

class HybridLocationResolver:
    """
    Deep-Location Engine: Landmarks -> Dictionary -> Semantic -> Hierarchy
    """
    
    def __init__(self, enable_semantic=True):
        self.enable_semantic = enable_semantic
        self.semantic_linker = None
        self.semantic_linker_loaded = False  # Track if we've attempted to load
        self.trace_log = []
                
        self.geo_resolver = GeoHierarchyResolver()
        self.landmarks = load_json(LANDMARKS_PATH)
        
    def _ensure_semantic_linker(self):
        """Lazy load semantic linker only when first needed."""
        if not self.enable_semantic or self.semantic_linker_loaded:
            return
        
        self.semantic_linker_loaded = True  # Mark as attempted
        
        try:
            # Lazy import - only load when actually needed
            # Adjust import path for backend usage if necessary, but assuming api.src is in path
            # If not, we might need to fix this.
            from api.src.parsing.semantic_location_linker import MultilingualFAISSLocationLinker
            self.semantic_linker = MultilingualFAISSLocationLinker()
            self.semantic_linker.load_multilingual_data()
            print("✅ Semantic location linker loaded")
        except Exception as e:
            print(f"⚠️  Semantic search disabled: {type(e).__name__}: {str(e)[:100]}")
            self.enable_semantic = False
            self.semantic_linker = None
        
    def resolve(self, text: str, entities: List[str] = None) -> Tuple[Optional[Dict], float, str]:
        """
        Returns: (LocationDict, Confidence, SourceTrace)
        """
        self.trace_log = []
        
        # 1. Dictionary / Hierarchy Lookup (Explicit Candidates) - PRIORITY 1
        candidates = self._extract_location_candidates(text)
        for cand in candidates:
            resolved = self.geo_resolver.resolve_hierarchy(cand, text)
            if resolved:
                self.trace_log.append(f"Hierarchy match: {cand}")
                return resolved, DICTIONARY_HIGH_CONFIDENCE, "hierarchy_resolver"

        # 2. Landmark Oracle (Static + File)
        landmark_loc = self._landmark_lookup(text)
        if landmark_loc:
            self.trace_log.append(f"Landmark found: {landmark_loc['canonical']}")
            return landmark_loc, LANDMARK_CONFIDENCE, "landmark_oracle"
            
        # 3. Entity Inference (e.g. @RaigarhPolice)
        if entities:
            entity_loc = self._infer_from_entities(entities, text)
            if entity_loc:
                self.trace_log.append(f"Entity inference: {entity_loc['canonical']}")
                return entity_loc, 0.85, "entity_inference"
        
        # 4. Semantic Search (if enabled and available)
        if self.enable_semantic:
            # Lazy load semantic linker on first use
            self._ensure_semantic_linker()
            
            if self.semantic_linker:
                # print("DEBUG: Semantic Search Enabled")
                for cand in candidates:
                    if len(cand) < 3: continue
                    # print(f"DEBUG: Searching for '{cand}'")
                    matches = self.semantic_linker.find_semantic_matches(cand, limit=1, min_score=0.6)
                    # print(f"DEBUG: Matches for '{cand}': {matches}")
                    if matches:
                        best = matches[0]
                        resolved = self.geo_resolver.resolve_hierarchy(best['name'], text)
                        if resolved:
                            self.trace_log.append(f"Semantic match: {cand} -> {best['name']}")
                            return resolved, best['similarity_score'] * 0.9, "semantic_search"
        
        return None, 0.0, "none"

    def _landmark_lookup(self, text: str) -> Optional[Dict]:
        # Check Static Landmarks first
        for landmark, city in STATIC_LANDMARKS.items():
            if landmark.lower() in text.lower():
                resolved = self.geo_resolver.resolve_hierarchy(city, text)
                if resolved:
                    resolved["landmark_trigger"] = landmark
                    return resolved

        for landmark, city in self.landmarks.items():
            if landmark in text:
                resolved = self.geo_resolver.resolve_hierarchy(city, text)
                if resolved:
                    resolved["landmark_trigger"] = landmark
                    return resolved
        return None

    def _extract_location_candidates(self, text: str) -> List[str]:
        """
        Expanded Regex with Suffix Stripping
        """
        candidates = []
        
        # 1. Suffix patterns: "Raipur me", "Durg se"
        suffix_pattern = r"([\u0900-\u097FA-Za-z]+)(?:\s+में|\s+से|\s+के|\s+me|\s+se|\s+ke)"
        for match in re.finditer(suffix_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        # 2. Admin markers (from V1) - Suffix
        admin_pattern = r"([\u0900-\u097FA-Za-z]+)\s+(?:जिला|विधानसभा|तहसील|थाना|ब्लॉक|पंचायत|नगर)"
        for match in re.finditer(admin_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        # 2b. Admin markers (NEW) - Prefix
        # Matches: ग्राम कुकुर्दा -> कुकुर्दा
        prefix_pattern = r"(?:ग्राम|Gram|Village)\s+([\u0900-\u097FA-Za-z]+)"
        for match in re.finditer(prefix_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        # 3. Known Entity Lookup (Districts & ULBs)
        if hasattr(self.geo_resolver, 'district_map'):
            for dist in self.geo_resolver.district_map:
                if dist in text:
                    candidates.append(dist)
                    
        if hasattr(self.geo_resolver, 'ulb_index'):
            for ulb in self.geo_resolver.ulb_index:
                if ulb in text:
                    candidates.append(ulb)
                    
        # 4. Ward/Sector/Zone Patterns (NEW for V2.1)
        ward_pattern = r"((?:Ward|Sector|Zone|वार्ड|सेक्टर|जोन)\s*(?:No\.?|Number|क्रमांक)?\s*[\d\w-]+(?:,\s*[A-Za-z\u0900-\u097F]+)?)"
        for match in re.finditer(ward_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))

        # 5. N-gram generation for Semantic Search (if enabled)
        if self.enable_semantic:
            words = text.split()
            for n in range(2, 5):
                for i in range(len(words) - n + 1):
                    chunk = " ".join(words[i:i+n])
                    if len(chunk) > 5:
                        candidates.append(chunk)

        # Sort by length descending
        seen = set()
        unique_candidates = []
        for c in candidates:
            c_clean = c.strip().strip(",").strip()
            if c_clean and c_clean not in seen:
                seen.add(c_clean)
                unique_candidates.append(c_clean)
                
        return sorted(unique_candidates, key=len, reverse=True)

    def _infer_from_entities(self, entities: List[str], text: str) -> Optional[Dict]:
        """
        Infer location from handles like @RaigarhPolice, @BastarDistrict
        """
        for entity in entities:
            if not entity.startswith("@"):
                continue
                
            if hasattr(self.geo_resolver, 'district_map'):
                for dist in self.geo_resolver.district_map:
                    if dist.lower() in entity.lower():
                        return self.geo_resolver.resolve_hierarchy(dist, text)
                        
            if hasattr(self.geo_resolver, 'ulb_index'):
                for ulb in self.geo_resolver.ulb_index:
                    if len(ulb) > 3 and ulb.lower() in entity.lower():
                         return self.geo_resolver.resolve_hierarchy(ulb, text)
        return None
