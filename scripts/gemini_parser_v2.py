#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Parser V2 - SOTA Upgrade
"Evidence-Based" Parsing Engine

Features:
- Deep-Location Engine (Landmarks, Suffix Stripping, Timeline Inference)
- Entity Resurrection (Regex, Honorifics, VIP List)
- Multi-Label Event Classifier (Score-Based)
- Traceability (Parsing Trace)
"""

import json
import re
import time
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union, Set
from collections import Counter, defaultdict, deque

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

VERSION = "2.0.0"

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"

# Data files
FULL_VILLAGES_PATH = DATA_DIR / "full_villages.json"
CONSTITUENCIES_PATH = DATA_DIR / "constituencies.json"
URBAN_DATA_PATH = DATA_DIR / "datasets" / "chhattisgarh_urban.ndjson"
LANDMARKS_PATH = DATA_DIR / "landmarks.json"
VIP_LIST_PATH = DATA_DIR / "vip_list.json"

# Semantic Search Thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.75
SEMANTIC_LOCATION_LIMIT = 3

# Dictionary Lookup Thresholds
DICTIONARY_HIGH_CONFIDENCE = 0.88
LANDMARK_CONFIDENCE = 0.95

# Timeline Inference
TIMELINE_WINDOW_SIZE = 3
TIMELINE_TIME_WINDOW_HOURS = 4

# Confidence Scoring Weights
CONFIDENCE_WEIGHTS = {
    'base_event': 0.6,
    'location': 0.15,
    'schemes': 0.08,
    'target_groups': 0.06,
    'communities': 0.04,
    'orgs': 0.04,
    'people': 0.03,
}

# Confidence Thresholds
CONFIDENCE_AUTO_APPROVE = 0.90
CONFIDENCE_NEEDS_REVIEW = 0.75

# Output
OUTPUT_ENCODING = "utf-8"

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
# TAXONOMIES & PATTERNS
# ==========================================

# Expanded Event Keywords with Scores
# Format: (Keywords, Label, Score)
EVENT_SCORING_RULES = [
    # Critical / High Priority
    (["माओवाद", "नक्सल", "नक्सली", "लाल आतंक", "सुरक्षा बल", "जवानों", "शहीद", "आत्मसमर्पण", "encounter", "ied"], "आंतरिक सुरक्षा / पुलिस", 2),
    (["मैच जीत", "टीम इंडिया", "क्रिकेट", "पदक", "स्वर्ण पदक", "खिलाड़ी", "ओलंपिक", "medal", "won", "winner"], "खेल / गौरव", 2),
    (["हादसा", "दुर्घटना", "रेल हादसा", "बस हादसा", "आगजनी", "ध्वस्त", "जनहानि", "tragedy", "accident"], "आपदा / दुर्घटना", 2),
    
    # Governance
    (["बैठक", "मुलाकात", "भेंट", "समीक्षा", "अध्यक्षता"], "बैठक", 1),
    (["जनसम्पर्क", "जनदर्शन", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन", 1),
    (["निरीक्षण", "inspection"], "निरीक्षण", 1),
    (["रैली", "जनसभा", "road show"], "रैली", 1),
    (["चुनाव", "मतदान", "प्रचार"], "चुनाव प्रचार", 1),
    (["उद्घाटन", "लोकार्पण", "शिलान्यास"], "उद्घाटन", 2),
    (["योजना", "घोषणा", "लाभार्थी"], "योजना घोषणा", 1),
    
    # Cultural / Social
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "मस्जिद", "धार्मिक", "जयंती"], "धार्मिक / सांस्कृतिक कार्यक्रम", 1),
    (["सम्मान", "सम्मानित", "felicitation"], "सम्मान / Felicitation", 1),
    (["प्रेस", "मीडिया", "वार्ता"], "प्रेस कॉन्फ़्रेंस / मीडिया", 1),
    (["शुभकामना", "बधाई", "wishes"], "शुभकामना / बधाई", 1),
    (["जन्मदिन", "birthday"], "जन्मदिन शुभकामना", 1),
    (["शोक", "श्रद्धांजलि", "condolence", "rip"], "शोक संदेश", 2),
    
    # Political
    (["कांग्रेस", "भाजपा", "विपक्ष", "आरोप", "बयान"], "राजनीतिक वक्तव्य", 1),
]

SCHEME_PATTERNS = {
    r"\bPMAY\b": "प्रधानमंत्री आवास योजना", r"प्रधानमंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"PM Awas": "प्रधानमंत्री आवास योजना", r"आयुष्मान भारत": "आयुष्मान भारत",
    r"\bAyushman\b": "आयुष्मान भारत", r"उज्ज्वला योजना": "प्रधानमंत्री उज्ज्वला योजना",
    r"स्वच्छ भारत": "स्वच्छ भारत मिशन", r"जन धन": "प्रधानमंत्री जन धन योजना",
    r"\bJan Dhan\b": "प्रधानमंत्री जन धन योजना", r"\bGST\b": "GST",
    r"महतारी वंदन": "महतारी वंदन योजना", r"Mahtari Vandan": "महतारी वंदन योजना",
}

# ==========================================
# GEO HIERARCHY RESOLVER (Reused from V1)
# ==========================================

class GeoHierarchyResolver:
    """Resolve complete administrative hierarchy: District->Block->GP->Village/ULB->Ward"""
    
    def __init__(self):
        self.villages_data = self._load_villages_data()
        self.constituencies = load_json(CONSTITUENCIES_PATH)
        self.urban_data = self._load_urban_data()
        
        self.village_index = self._build_village_index()
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
        return index
    
    def resolve_hierarchy(self, location_name: str, context_text: str = "") -> Optional[Dict]:
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
                "location_type": "urban",
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
        patterns = [r"वार्ड\s*(?:नंबर\s*)?(\d+)", r"ward\s*(?:no\.IBLE\s*)?(\d+)"]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match: return match.group(1)
        return None
    
    def _extract_zone(self, text: str) -> Optional[str]:
        patterns = [r"जोन\s*(?:नंबर\s*)?(\d+)", r"zone\s*(?:no\.IBLE\s*)?(\d+)"]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match: return match.group(1)
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
        self.trace_log = []
        
        if enable_semantic:
            try:
                from api.src.parsing.semantic_location_linker import MultilingualFAISSLocationLinker
                self.semantic_linker = MultilingualFAISSLocationLinker()
                self.semantic_linker.load_multilingual_data()
            except:
                self.enable_semantic = False
                
        self.geo_resolver = GeoHierarchyResolver()
        self.landmarks = load_json(LANDMARKS_PATH)
        
        # Re-use V1 dictionary (CANONICAL_LOCATIONS) - Inlined for simplicity or load from file
        # For V2, we rely heavily on the geo_resolver's indexes + landmarks
        
    def resolve(self, text: str) -> Tuple[Optional[Dict], float, str]:
        """
        Returns: (LocationDict, Confidence, SourceTrace)
        """
        self.trace_log = []
        
        # 1. Landmark Oracle
        landmark_loc = self._landmark_lookup(text)
        if landmark_loc:
            self.trace_log.append(f"Landmark found: {landmark_loc['canonical']}")
            return landmark_loc, LANDMARK_CONFIDENCE, "landmark_oracle"
            
        # 2. Dictionary / Hierarchy Lookup
        candidates = self._extract_location_candidates(text)
        for cand in candidates:
            resolved = self.geo_resolver.resolve_hierarchy(cand, text)
            if resolved:
                self.trace_log.append(f"Hierarchy match: {cand}")
                return resolved, DICTIONARY_HIGH_CONFIDENCE, "hierarchy_resolver"
        
        # 3. Semantic Search
        if self.enable_semantic and self.semantic_linker:
            for cand in candidates:
                if len(cand) < 3: continue
                matches = self.semantic_linker.find_semantic_matches(cand, limit=1, min_score=0.75)
                if matches:
                    best = matches[0]
                    resolved = self.geo_resolver.resolve_hierarchy(best['name'], text)
                    if resolved:
                        self.trace_log.append(f"Semantic match: {cand} -> {best['name']}")
                        return resolved, best['similarity_score'] * 0.9, "semantic_search"
        
        return None, 0.0, "none"

    def _landmark_lookup(self, text: str) -> Optional[Dict]:
        for landmark, city in self.landmarks.items():
            if landmark in text: # Case sensitive? Maybe not.
                # Resolve the city/district
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
        # Hindi: रायपुर में, दुर्ग से
        suffix_pattern = r"([अ-हA-Za-z]+)(?:\s+में|\s+से|\s+के|\s+me|\s+se|\s+ke)\b"
        for match in re.finditer(suffix_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        # 2. Admin markers (from V1)
        admin_pattern = r"([अ-हA-Za-z]+)\s+(?:जिला|विधानसभा|तहसील|थाना|ब्लॉक|पंचायत|नगर)"
        for match in re.finditer(admin_pattern, text, re.IGNORECASE):
            candidates.append(match.group(1))
            
        # 3. De-fuse compound words (Simple heuristic)
        # e.g., "shaktijila" -> "shakti" (covered by admin pattern if space exists, but if no space?)
        # For now, rely on clean spaces.
        
        return list(set(candidates))

# ==========================================
# ENTITY RESURRECTION
# ==========================================

class EntityExtractorV2:
    def __init__(self):
        self.vip_list = load_json(VIP_LIST_PATH)
        
    def extract_people(self, text: str) -> List[str]:
        people = set()
        
        # 1. VIP List (Exact Match)
        for vip in self.vip_list:
            if vip in text:
                people.add(vip)
                
        # 2. Honorifics (Hindi NER)
        # Pattern: (Shri|Smt|Dr|Mananiya) [Word] [Word] (Ji)?
        honorifics = r"(?:श्री|श्रीमती|डॉ\.|माननीय|Shri|Smt|Dr)\s+([अ-हA-Za-z]+(?:\s+[अ-हA-Za-z]+)?)(?:\s+जी|ji)?"
        for match in re.finditer(honorifics, text, re.IGNORECASE):
            name = match.group(1).strip()
            if name not in ["मुख्यमंत्री", "प्रधानमंत्री", "अध्यक्ष", "CM", "PM"]: # Stopwords
                people.add(name)
                
        # 3. Handles and Hashtags (Potential people)
        # Only add if they look like names? For now, add all handles as potential people mentions
        # or separate field? User asked for "People" column population.
        # Let's be conservative: Handles often represent people.
        handles = re.findall(r"@(\w+)", text)
        people.update(handles)
        
        return sorted(list(people))

    def extract_schemes(self, text: str) -> List[str]:
        schemes = set()
        for pattern, canonical in SCHEME_PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                schemes.add(canonical)
        return sorted(list(schemes))
        
    def extract_others(self, text: str) -> Dict[str, List[str]]:
        # Placeholder for other entities
        return {
            "target_groups": [],
            "communities": [],
            "orgs": []
        }

# ==========================================
# MULTI-LABEL EVENT CLASSIFIER
# ==========================================

class MultiLabelEventClassifier:
    """
    Score-Based Classification with Tie-Breakers
    """
    def classify(self, text: str, schemes: List[str]) -> Tuple[str, Dict[str, int]]:
        scores = defaultdict(int)
        text_l = text.lower()
        
        # 1. Keyword Scoring
        for keywords, label, score in EVENT_SCORING_RULES:
            if any(k.lower() in text_l for k in keywords):
                scores[label] += score
                
        # 2. Rescue / Context Rules
        if "ayushman" in text_l and "mandir" in text_l:
            scores["योजना घोषणा"] += 3 # Boost Scheme
            scores["धार्मिक / सांस्कृतिक कार्यक्रम"] -= 5 # Penalize Religious
            
        if "rail" in text_l and "haadsa" in text_l:
            scores["आपदा / दुर्घटना"] += 3
            scores["योजना घोषणा"] -= 5
            
        if "air show" in text_l or "surya kiran" in text_l:
            scores["खेल / गौरव"] += 3
            scores["धार्मिक / सांस्कृतिक कार्यक्रम"] -= 5

        if schemes:
            scores["योजना घोषणा"] += 2

        # 3. Winner Takes All
        if not scores:
            return "अन्य", dict(scores)
            
        # Sort by score (desc), then by priority rules (implicit in sort stability or explicit check)
        # Tie-Breakers: Disaster > Scheme, Rally > Religious
        # We can enforce this by adding tiny offsets to scores
        if scores.get("आपदा / दुर्घटना", 0) > 0: scores["आपदा / दुर्घटना"] += 0.1
        if scores.get("रैली", 0) > 0: scores["रैली"] += 0.1
        
        best_event = max(scores.items(), key=lambda x: x[1])
        
        if best_event[1] <= 0:
            return "अन्य", dict(scores)
            
        return best_event[0], dict(scores)

# ==========================================
# MAIN PARSER V2
# ==========================================

class GeminiParserV2:
    def __init__(self, enable_semantic=True):
        print("Initializing Gemini Parser V2 (SOTA)...")
        self.location_resolver = HybridLocationResolver(enable_semantic=enable_semantic)
        self.timeline_inference = TimelineInference()
        self.entity_extractor = EntityExtractorV2()
        self.event_classifier = MultiLabelEventClassifier()
        print("✅ Parser V2 initialized")

    def parse_tweet(self, record: Dict[str, Any]) -> Dict[str, Any]:
        text = record.get("raw_text") or record.get("text") or ""
        created_at = record.get("created_at")
        
        # 1. Entity Extraction
        people = self.entity_extractor.extract_people(text)
        schemes = self.entity_extractor.extract_schemes(text)
        other_entities = self.entity_extractor.extract_others(text)
        
        # 2. Event Classification
        event_type, event_scores = self.event_classifier.classify(text, schemes)
        
        # 3. Location Resolution
        location, loc_conf, loc_source = self.location_resolver.resolve(text)
        
        # 4. Timeline Inference (if location unknown)
        if not location:
            location = self.timeline_inference.infer(created_at)
            if location:
                loc_source = "temporal_inference"
                loc_conf = 0.6
        
        # Update Timeline
        self.timeline_inference.update(created_at, location)
        
        # 5. Parsing Trace
        parsing_trace = {
            "triggered_keywords": [k for k, v in event_scores.items() if v > 0],
            "location_source": loc_source,
            "event_score_matrix": event_scores,
            "timeline_used": (loc_source == "temporal_inference")
        }
        
        # 6. Confidence Scoring (Simplified for V2)
        confidence = 0.5
        if event_type != "अन्य": confidence += 0.3
        if location: confidence += 0.15
        if people: confidence += 0.05
        confidence = min(confidence, 0.99)
        
        # Construct Output
        parsed_data_v9 = {
            "event_type": event_type,
            "event_date": created_at[:10] if created_at else None,
            "location": location,
            "people_mentioned": people,
            "schemes_mentioned": schemes,
            "target_groups": other_entities["target_groups"],
            "communities": other_entities["communities"],
            "organizations": other_entities["orgs"],
            "confidence": confidence,
            "parsing_trace": parsing_trace,
            "model_version": "gemini-parser-v2"
        }
        
        return {
            **record,
            "parsed_data_v9": parsed_data_v9,
            "metadata_v9": {
                "model": "gemini-parser-v2",
                "version": VERSION
            }
        }

    def parse_file(self, input_path: Path, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n🚀 Parsing: {input_path}")
        
        tweets = []
        with input_path.open("r", encoding=OUTPUT_ENCODING) as f:
            for line in f:
                if line.strip():
                    tweets.append(self.parse_tweet(json.loads(line)))
                    
        output_file = output_dir / "parsed_tweets_gemini_parser_v2.jsonl"
        with output_file.open("w", encoding=OUTPUT_ENCODING) as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + "\n")
                
        print(f"✅ Done. Output: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Gemini Parser V2")
    parser.add_argument("input", type=Path, help="Input JSONL file")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    args = parser.parse_args()
    
    gp = GeminiParserV2()
    gp.parse_file(args.input, args.output_dir)

if __name__ == "__main__":
    main()
