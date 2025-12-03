#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Parser V1 - Hybrid Rule-Based + Semantic + Entity Resolution + Geo-Hierarchy

Consolidated single-file parser for tweet processing.
"""

import json
import re
import time
import hashlib
import argparse
import unittest
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union, Set
from collections import Counter

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

import sys

# Base paths
# Assuming this script is in scripts/gemini_parser_v1.py, so PROJECT_ROOT is up one level
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"

# Data files
FULL_VILLAGES_PATH = DATA_DIR / "full_villages.json"
CONSTITUENCIES_PATH = DATA_DIR / "constituencies.json"
URBAN_DATA_PATH = DATA_DIR / "datasets" / "chhattisgarh_urban.ndjson"

# Semantic Search Thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.75
SEMANTIC_LOCATION_LIMIT = 3

# Dictionary Lookup Thresholds
DICTIONARY_HIGH_CONFIDENCE = 0.88
CONFIDENCE_THRESHOLD_HIGH = 0.88

# Deduplication
DEDUPLICATION_ENABLED = True
FINGERPRINT_TOP_PEOPLE = 3

# Confidence Scoring Weights
CONFIDENCE_WEIGHTS = {
    'base_event': 0.7,
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

# Text Validation
MIN_SUBSTANTIAL_LENGTH = 20
SHORT_TWEET_PENALTY = 0.85

# High-Precision Event Types
HIGH_PRECISION_EVENTS = [
    "शोक संदेश",
    "जन्मदिन शुभकामना",
    "आंतरिक सुरक्षा / पुलिस",
    "खेल / गौरव",
    "आपदा / दुर्घटना"
]

HIGH_PRECISION_CONFIDENCE_FLOOR = 0.92

# Rescue Logic
RESCUE_CONFIDENCE_BONUSES = {
    'sports': 0.18,
    'security': 0.20,
    'admin': 0.15,
    'election': 0.17,
    'infra_dev': 0.16,
    'scheme': 0.15,
    'political': 0.15,
    'cultural': 0.14,
    'greetings': 0.10
}

# Geo-Hierarchy Resolution
GEO_HIERARCHY_ENABLED = True

# Performance
MAX_FAISS_QUERIES_PER_TWEET = 5
PROCESSING_TIMEOUT_MS = 150

# Output
OUTPUT_ENCODING = "utf-8"
OUTPUT_INDENT = None

# ==========================================
# SHARED UTILS
# ==========================================

def load_ndjson(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load NDJSON file."""
    data = []
    if not Path(path).exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def load_json(path: Union[str, Path]) -> Any:
    """Load JSON file."""
    if not Path(path).exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# ==========================================
# TAXONOMIES
# ==========================================

ALLOWED_EVENT_TYPES_HI = [
    "बैठक",
    "जनसम्पर्क / जनदर्शन",
    "प्रशासनिक समीक्षा बैठक",
    "निरीक्षण",
    "रैली",
    "चुनाव प्रचार",
    "उद्घाटन",
    "योजना घोषणा",
    "धार्मिक / सांस्कृतिक कार्यक्रम",
    "सम्मान / Felicitation",
    "प्रेस कॉन्फ़्रेंस / मीडिया",
    "शुभकामना / बधाई",
    "जन्मदिन शुभकामना",
    "शोक संदेश",
    "आंतरिक सुरक्षा / पुलिस",
    "खेल / गौरव",
    "राजनीतिक वक्तव्य",
    "आपदा / दुर्घटना",
    "अन्य",
]

CONTENT_MODES = [
    "मैदान-स्तर कार्यक्रम",
    "नीति / वक्तव्य",
    "डिजिटल / सोशल-media पोस्ट",
    "खेल / उपलब्धि पर प्रतिक्रिया",
    "सामान्य शुभकामनाएँ / पर्व",
]

EVENT_KEYWORD_CLUSTERS: List[Tuple[List[str], str]] = [
    (["माओवाद", "नक्सल", "नक्सली", "लाल आतंक", "सुरक्षा बल", "जवानों", "शहीद",
      "आत्मसमर्पण", "बस्तर ओलंपिक", "ऑपरेशन", "पुलिस स्मृति", "police", "jawan", "encounter", "ied"], "आंतरिक सुरक्षा / पुलिस"),

    (["मैच जीत", "टीम इंडिया", "क्रिकेट", "पदक", "स्वर्ण पदक", "खिलाड़ी",
      "ओलंपिक", "खेल", "tournament", "चैंपियंस ट्रॉफी", "गर्व का क्षण", "medal", "won", "winner", "bcci"], "खेल / गौरव"),

    (["हादसा", "दुर्घटना", "रेल हादसा", "बस हादसा", "आगजनी", "ध्वस्त", "जनहानि", "tragedy", "accident", "collision"], "आपदा / दुर्घटना"),

    (["डबल इंजन", "कांग्रेस सरकार", "भ्रष्टाचार", "तुष्टिकरण", "आपातकाल",
      "विकसित भारत", "मोदी की गारंटी", "विपक्ष", "आरोप", "statement", "political", "manifesto"], "राजनीतिक वक्तव्य"),

    (["बैठक", "मुलाकात", "भेंट", "बैठक ली", "बैठक में", "बैठक का", "अध्यक्षता की", "सत्र", "सदन की कार्यवाही"], "बैठक"),
    (["जनसम्पर्क", "जनसंपर्क", "जन संपर्क", "जनदर्शन", "जन-दर्शन", "जन सुनवाई", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन"),
    (["समीक्षा बैठक", "समीक्षा की", "समीक्षा की गई", "अधिकारियों के साथ", "विभागीय बैठक", "कलेक्टर", "कलेक्टरेट", "समीक्षा कार्य"], "प्रशासनिक समीक्षा बैठक"),
    (["निरीक्षण", "inspection", "निरीक्षण किया"], "निरीक्षण"),
    (["रैली", "जनसभा", "public rally", "road show", "रोड शो"], "रैली"),
    (["चुनावी", "मतदान", "मतदाता", "चुनाव प्रचार", "poll campaign", "voting", "polling"], "चुनाव प्रचार"),
    (["उद्घाटन", "लोकार्पण", "inauguration", "inaugurated", "शिलान्यास", "dedication"], "उद्घाटन"),
    (["घोषणा", "नई योजना", "योजना की जानकारी", "योजना का लाभ", "scheme launch"], "योजना घोषणा"),
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "गुरु नानक", "मस्जिद", "धार्मिक", "सांस्कृतिक कार्यक्रम", "जयंती", "pujya", "saints"], "धार्मिक / सांस्कृतिक कार्यक्रम"),
    (["सम्मान", "सम्मानित", "शॉल", "श्रीफल", "समारोह", "felicitation", "award"], "सम्मान / Felicitation"),
    (["प्रेस वार्ता", "प्रेस कॉन्फ़्रेंस", "मीडिया से बातचीत"], "प्रेस कॉन्फ़्रेंस / मीडिया"),
    (["शुभकामनाएं", "शुभकामनाएँ", "बधाई", "congratulations", "best wishes", "greetings"], "शुभकामना / बधाई"),
    (["जन्मदिन", "birthday", "अवतरण दिवस"], "जन्मदिन शुभकामना"),
    (["श्रद्धांजलि", "शोक संदेश", "दिवंगत", "अंतिम यात्रा", "पुण्यतिथि", "condolence", "tribute", "rip"], "शोक संदेश"),
]

SCHEME_PATTERNS = {
    r"\bPMAY\b": "प्रधानमंत्री आवास योजना", r"प्रधानमंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"PM Awas": "प्रधानमंत्री आवास योजना", r"आयुष्मान भारत": "आयुष्मान भारत",
    r"\bAyushman\b": "आयुष्मान भारत", r"उज्ज्वला योजना": "प्रधानमंत्री उज्ज्वला योजना",
    r"स्वच्छ भारत": "स्वच्छ भारत मिशन", r"जन धन": "प्रधानमंत्री जन धन योजना",
    r"\bJan Dhan\b": "प्रधानमंत्री जन धन योजना", r"\bGST\b": "GST",
}

# ==========================================
# LOCATION DICTIONARIES
# ==========================================

CANONICAL_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "रायगढ़": {"canonical": "रायगढ़", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "Raigarh": {"canonical": "रायगढ़", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "खरसिया": {"canonical": "खरसिया", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "Kharsia": {"canonical": "खरसिया", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "रायपुर": {"canonical": "रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "Raipur": {"canonical": "रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "नया रायपुर": {"canonical": "नया रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "बिलासपुर": {"canonical": "बिलासपुर", "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "Bilaspur": {"canonical": "बिलासपुर", "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "कोरबा": {"canonical": "कोरबा", "hierarchy": ["छत्तीसगढ़", "कोरबाजिला"]},
    "Korba": {"canonical": "कोरबा", "hierarchy": ["छत्तीसगढ़", "कोरबाजिला"]},
    "रतनपुर": {"canonical": "रतनपुर", "hierarchy": ["छत्तीसगढ़", "बिलासपुरजिला"]},
    "दुर्ग": {"canonical": "दुर्ग", "hierarchy": ["छत्तीसगढ़", "दुर्गजिला"]},
    "Durg": {"canonical": "दुर्ग", "hierarchy": ["छत्तीसगढ़", "दुर्गजिला"]},
    "भिलाई": {"canonical": "भिलाई", "hierarchy": ["छत्तीसगढ़", "दुर्गजिला"]},
    "Bhilai": {"canonical": "भिलाई", "hierarchy": ["छत्तीसगढ़", "दुर्गजिला"]},
    "अंबिकापुर": {"canonical": "अंबिकापुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "Ambikapur": {"canonical": "अंबिकापुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "सुरजपुर": {"canonical": "सुरजपुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुरजिला"]},
    "जगदलपुर": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तरजिला"]},
    "Jagdalpur": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तरजिला"]},
    "कोंडागाँव": {"canonical": "कोंडागाँव", "hierarchy": ["छत्तीसगढ़", "कोंडागाँवजिला"]},
    "नारायणपुर": {"canonical": "नारायणपुर", "hierarchy": ["छत्तीसगढ़", "नारायणपुरजिला"]},
    "जांजगीर": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "Janjgir": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "चंपा": {"canonical": "चंपा", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "राजनांदगाँव": {"canonical": "राजनांदगाँव", "hierarchy": ["छत्तीसगढ़", "राजनांदगाँवजिला"]},
    "महासमुंद": {"canonical": "महासमुंद", "hierarchy": ["छत्तीसगढ़", "महासमुंदजिला"]},
    "धमतरी": {"canonical": "धमतरी", "hierarchy": ["छत्तीसगढ़", "धमतरीजिला"]},
    "बालोद": {"canonical": "बालोद", "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "गरियाबंद": {"canonical": "गरियाबंद", "hierarchy": ["छत्तीसगढ़", "गरियाबंदजिला"]},
    "बीजापुर": {"canonical": "बीजापुर", "hierarchy": ["छत्तीसगढ़", "बीजापुरजिला"]},
    "दंतेवाड़ा": {"canonical": "दंतेवाड़ा", "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ाजिला"]},
    "सुकमा": {"canonical": "सुकमा", "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
    "बलौदाबाजार": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजारजिला"]},
    "भाटापारा": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजारजिला"]},
    "कवर्धा": {"canonical": "कवर्धा", "hierarchy": ["छत्तीसगढ़", "कबीरधामजिला"]},
    "कांकेर": {"canonical": "कांकेर", "hierarchy": ["छत्तीसगढ़", "कांकेरजिला"]},
    "कोरिया": {"canonical": "कोरिया", "hierarchy": ["छत्तीसगढ़", "कोरियाजिला"]},
    "जशपुर": {"canonical": "जशपुर", "hierarchy": ["छत्तीसगढ़", "जशपुरजिला"]},
    "मुंगेली": {"canonical": "मुंगेली", "hierarchy": ["छत्तीसगढ़", "मुंगेलीजिला"]},
    "बेमेतरा": {"canonical": "बेमेतरा", "hierarchy": ["छत्तीसगढ़", "बेमेतराजिला"]},
    "गौरेला": {"canonical": "गौरेला-पेंड्रा-मरवाही", "hierarchy": ["छत्तीसगढ़", "GPMजिला"]},
    "पेंड्रा": {"canonical": "गौरेला-पेंड्रा-मरवाही", "hierarchy": ["छत्तीसगढ़", "GPMजिला"]},
    "सारंगढ़": {"canonical": "सारंगढ़-बिलाईगढ़", "hierarchy": ["छत्तीसगढ़", "सारंगढ़-बिलाईगढ़जिला"]},
    "मोहला": {"canonical": "मोहला-मानपुर", "hierarchy": ["छत्तीसगढ़", "मोहला-मानपुरजिला"]},
    "शक्ति": {"canonical": "शक्ति", "hierarchy": ["छत्तीसगढ़", "शक्तिजिला"]},
    "खैरागढ़": {"canonical": "खैरागढ़", "hierarchy": ["छत्तीसगढ़", "खैरागढ़जिला"]},
    "मनेंद्रगढ़": {"canonical": "मनेंद्रगढ़", "hierarchy": ["छत्तीसगढ़", "MCBजिला"]},
}

# ==========================================
# GEO HIERARCHY RESOLVER
# ==========================================

class GeoHierarchyResolver:
    """Resolve complete administrative hierarchy: District->Block->GP->Village/ULB->Ward"""
    
    def __init__(self):
        # Load comprehensive geography datasets
        self.villages_data = self._load_villages_data()
        self.constituencies = load_json(CONSTITUENCIES_PATH)
        self.urban_data = self._load_urban_data()
        
        # Build indexes
        self.village_index = self._build_village_index()      # ~20K villages
        self.ulb_index = self._build_ulb_index()              # ULBs
        self.district_map = self._build_district_map()         # 33 districts
    
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
        """Index: village_name -> {district, block, gp, ac, pc, hierarchy}"""
        index = {}
        for row in self.villages_data:
            village = row.get("name")
            if village:
                # Normalize name if needed
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
        """Index: ulb_name -> {district, ulb_type, ward_count, ac, pc, hierarchy}"""
        index = {}
        
        districts = self.constituencies.get("districts", {})
        for dist_name, dist_data in districts.items():
            ulbs = dist_data.get("ulb_names", [])
            for ulb in ulbs:
                index[ulb] = {
                    "district": dist_name,
                    "ulb_type": "ULB", # Generic if not known
                    "ward_count": 0,
                    "assembly": dist_data.get("assembly"), # Default to district HQ assembly or similar
                    "parliamentary": dist_data.get("parliamentary"),
                    "hierarchy_path": ["छत्तीसगढ़", f"{dist_name} जिला", ulb],
                    "type": "urban"
                }

        # From urban_data (if available, richer data)
        for row in self.urban_data:
            ulb = row.get("ulb") or row.get("nagar_nigam") or row.get("nagar_palika")
            if ulb:
                index[ulb] = {
                    "district": row.get("district"),
                    "ulb_type": row.get("ulb_type"),  # "नगर निगम", "नगर पालिका", etc
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
        """Index: district_name -> details"""
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
        """
        Resolve complete hierarchy for any location mention.
        """
        # Priority 1: Village lookup
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
        
        # Priority 2: ULB lookup
        if location_name in self.ulb_index:
            u = self.ulb_index[location_name]
            
            # Extract ward/zone from context
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
        
        # Priority 3: District/Tehsil/Block (from constituencies.json blocks or district map)
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
        """Extract ward number from context: 'वार्ड 12', 'ward 12'"""
        patterns = [
            r"वार्ड\s*(?:नंबर\s*)?(\d+)",
            r"ward\s*(?:no\.IBLE\s*)?(\d+)",
            r"वार्ड\s+([अ-ह]+)"  # Hindi number words could be handled here
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_zone(self, text: str) -> Optional[str]:
        """Extract zone info: 'जोन 1', 'zone A'"""
        patterns = [
             r"जोन\s*(?:नंबर\s*)?(\d+)",
             r"zone\s*(?:no\.IBLE\s*)?(\d+)",
             r"जोन\s+([अ-ह]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

# ==========================================
# LOCATION RESOLVER
# ==========================================

class HybridLocationResolver:
    """Combines dictionary, semantic search, and hierarchy resolution"""
    
    def __init__(self, enable_semantic=True, data_dir: Optional[Path] = None):
        self.enable_semantic = enable_semantic
        self.semantic_linker = None
        
        if enable_semantic:
            try:
                from api.src.parsing.semantic_location_linker import MultilingualFAISSLocationLinker
                self.semantic_linker = MultilingualFAISSLocationLinker()
                # Ensure data is loaded (this might take a moment)
                self.semantic_linker.load_multilingual_data()
            except ImportError:
                print("⚠️  Semantic linker not available. Falling back to rule-based only.")
                self.enable_semantic = False
            except Exception as e:
                print(f"⚠️  Semantic linker init failed: {e}")
                self.enable_semantic = False
                
        self.geo_resolver = GeoHierarchyResolver()
        self.dictionary = CANONICAL_LOCATIONS
        
        self.stats = {
            'dict_hits': 0,
            'semantic_hits': 0,
            'hierarchy_enrichments': 0,
            'not_found': 0
        }
    
    def resolve(self, text: str, old_location: Optional[Dict] = None) -> Tuple[Optional[Dict], float]:
        """
        Three-stage resolution:
        1. Dictionary lookup (fast, high confidence)
        2. FAISS semantic search (medium confidence)
        3. Geo-hierarchy enrichment (adds missing fields)
        """
        # Stage 1: Dictionary
        dict_match, dict_conf = self._dictionary_lookup(text, old_location)
        if dict_match and dict_conf >= 0.88:
            self.stats['dict_hits'] += 1
            # Enrich with full hierarchy
            enriched = self.geo_resolver.resolve_hierarchy(
                dict_match["canonical"],
                context_text=text
            )
            if enriched:
                self.stats['hierarchy_enrichments'] += 1
                return enriched, dict_conf
            return dict_match, dict_conf
        
        # Stage 2: Extract candidates and run semantic search
        if self.enable_semantic and self.semantic_linker:
            candidates = self._extract_location_candidates(text)
            semantic_matches = []
            
            for candidate in candidates:
                # Skip short candidates
                if len(candidate) < 3: continue
                
                matches = self.semantic_linker.find_semantic_matches(
                    candidate, 
                    limit=3, 
                    min_score=0.75
                )
                if matches:
                    semantic_matches.extend(matches)
            
            if semantic_matches:
                # Take best match
                best = max(semantic_matches, key=lambda x: x['similarity_score'])
                best_name = best['name']
                best_score = best['similarity_score']
                
                # Stage 3: Resolve full hierarchy
                full_location = self.geo_resolver.resolve_hierarchy(best_name, text)
                
                if full_location:
                    self.stats['semantic_hits'] += 1
                    # Slight discount for semantic match compared to exact dictionary match
                    final_score = best_score * 0.95 
                    full_location["source"] = "semantic"
                    return full_location, final_score
        
        # Fallback: partial location from dictionary if it was found but low confidence
        if dict_match:
            self.stats['dict_hits'] += 1
            return dict_match, dict_conf
        
        self.stats['not_found'] += 1
        return None, 0.0

    def _dictionary_lookup(self, text: str, old_location: Optional[Dict]) -> Tuple[Optional[Dict], float]:
        candidates = []
        if old_location and old_location.get("canonical"):
            candidates.append(old_location["canonical"])

        text_lower = text.lower()
        for key, info in self.dictionary.items():
            if key in text or key.lower() in text_lower:
                candidates.append(key)
        
        # Also check inline candidates against dictionary
        inline_candidates = self._extract_location_candidates(text)
        for cand in inline_candidates:
            if cand in self.dictionary:
                candidates.append(cand)

        if not candidates:
            return None, 0.0

        best_raw = Counter(candidates).most_common(1)[0][0]
        loc_info = self.dictionary.get(best_raw)
        
        if not loc_info:
             return None, 0.0

        return {
            "district": loc_info.get("hierarchy", ["", ""])[-1].replace(" जिला", ""),
            "canonical": loc_info["canonical"],
            "hierarchy_path": loc_info.get("hierarchy", []),
            "visit_count": 1,
            "canonical_key": f"CG_{loc_info['canonical']}",
            "source": "dictionary"
        }, 0.88

    def _extract_location_candidates(self, text: str) -> List[str]:
        """Extract location names with administrative markers"""
        # Simplified pattern to avoid range errors. Matches Devanagari and Latin chars.
        # \u0900-\u097F is the Devanagari block.
        name_pattern = r"([अ-हA-Za-z\u0900-\u097F]+)"
        
        patterns = [
            name_pattern + r"\s+जिला",
            name_pattern + r"\s+विधानसभा",
            name_pattern + r"\s+तहसील",
            name_pattern + r"\s+थाना",
            name_pattern + r"\s+विकासखंड",
            name_pattern + r"\s+चौकी",
            name_pattern + r"\s+ग्राम\s+पंचायत",
            name_pattern + r"\s+गाँव",
            name_pattern + r"\s+नगर\s+(?:निगम|पालिका|पंचायत)"
        ]
        candidates = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip()
                if len(name) >= 2:
                    candidates.append(name)
        return list(set(candidates))  # Deduplicate

    def get_stats(self):
        return self.stats

# ==========================================
# ENTITY EXTRACTOR
# ==========================================

class EntityExtractor:
    """
    Entity Extraction Module
    
    Enhanced extraction with INTRA-TWEET entity deduplication.
    All extractors return deduplicated lists.
    """
    
    def extract_schemes(self, text: str) -> Tuple[List[str], float]:
        schemes = set()
        for pattern, canonical in SCHEME_PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                schemes.add(canonical)
        return sorted(list(schemes)), 0.0

    def extract_target_groups(self, text: str) -> Tuple[List[str], float]:
        groups = set()
        keywords = ["किसान", "महिला", "युवा", "छात्र", "आदिवासी", "farmers", "women", "youth", "students", "tribals"]
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                groups.add(kw)
        return sorted(list(groups)), 0.0

    def extract_communities(self, text: str) -> Tuple[List[str], float]:
        # Placeholder
        return [], 0.0

    def extract_orgs(self, text: str) -> Tuple[List[str], float]:
        # Placeholder
        return [], 0.0

    def extract_word_buckets(self, text: str) -> Tuple[List[str], float]:
        # Placeholder
        return [], 0.0

# ==========================================
# RESCUE DETECTOR
# ==========================================

class RescueDetector:
    """Detect specific event types to rescue them from 'Other' classification"""
    
    def rescue(self, text: str, current_event: str, location: Optional[Dict], schemes: List[str]) -> Dict[str, Any]:
        text_l = text.lower()
        
        rescue_info = {
            "event_type": current_event,
            "content_mode": "डिजिटल / सोशल-media पोस्ट",
            "is_rescued": False,
            "rescue_tag": None,
            "confidence_bonus": 0.0
        }

        # --- Priority 1: High Specificity ---
        if self._looks_like_sports_tweet(text_l) or self._looks_like_sports_achievement(text_l):
            rescue_info.update({
                "event_type": "खेल / गौरव", 
                "content_mode": "खेल / उपलब्धि पर प्रतिक्रिया",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "sports_v8",
                "confidence_bonus": 0.18
            })
            return rescue_info

        if self._looks_like_security_context(text_l):
            rescue_info.update({
                "event_type": "आंतरिक सुरक्षा / पुलिस", 
                "content_mode": "नीति / वक्तव्य",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "security_v8",
                "confidence_bonus": 0.20
            })
            return rescue_info

        # --- Priority 2: Governance ---
        if self._looks_like_administrative_update(text_l):
            rescue_info.update({
                "event_type": "प्रशासनिक समीक्षा बैठक", 
                "content_mode": "नीति / वक्तव्य",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "admin_v8",
                "confidence_bonus": 0.15
            })
            return rescue_info

        if self._looks_like_election_politics(text_l):
            rescue_info.update({
                "event_type": "चुनाव प्रचार", 
                "content_mode": "मैदान-स्तर कार्यक्रम",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "election_v8",
                "confidence_bonus": 0.17
            })
            return rescue_info

        # --- Priority 3: Development & Schemes ---
        if self._looks_like_industrial_development(text_l) or self._looks_like_infrastructure_work(text_l):
            rescue_info.update({
                "event_type": "उद्घाटन", 
                "content_mode": "मैदान-स्तर कार्यक्रम",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "infra_dev",
                "confidence_bonus": 0.16
            })
            return rescue_info

        if self._looks_like_scheme_implementation(text_l, schemes) or self._looks_like_relief_humanitarian(text_l):
            rescue_info.update({
                "event_type": "योजना घोषणा", 
                "content_mode": "मैदान-स्तर कार्यक्रम",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "scheme_v8",
                "confidence_bonus": 0.15
            })
            return rescue_info

        # --- Priority 4: Political / Social ---
        if self._looks_like_general_political(text_l) or self._looks_like_policy_statement(text_l):
            rescue_info.update({
                "event_type": "राजनीतिक वक्तव्य", 
                "content_mode": "नीति / वक्तव्य",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "political_v8",
                "confidence_bonus": 0.15
            })
            return rescue_info

        if self._looks_like_cultural_religious(text_l):
            rescue_info.update({
                "event_type": "धार्मिक / सांस्कृतिक कार्यक्रम", 
                "content_mode": "सामान्य शुभकामनाएँ / पर्व",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "cultural_v8",
                "confidence_bonus": 0.14
            })
            return rescue_info

        if self._looks_like_congratulatory_general(text_l):
            rescue_info.update({
                "event_type": "शुभकामना / बधाई", 
                "content_mode": "सामान्य शुभकामनाएँ / पर्व",
                "is_rescued": current_event == "अन्य",
                "rescue_tag": "greetings_v8",
                "confidence_bonus": 0.10
            })
            return rescue_info

        return rescue_info

    def _looks_like_sports_tweet(self, text_l: str) -> bool:
        SPORTS_SPECIFIC = ["क्रिकेट", "टीम इंडिया", "world cup", "t20", "ipl", "odi", "bcci", "रणजी"]
        if any(kw in text_l for kw in SPORTS_SPECIFIC): return True
        if "मैच" in text_l and any(kw in text_l for kw in ["जीत", "हार", "विकेट", "रन", "won", "lost"]): return True
        return False

    def _looks_like_sports_achievement(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["स्वर्ण पदक", "रजत पदक", "कांस्य पदक", "medal", "gold medal", "championship"])

    def _looks_like_security_context(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["माओवादी", "माओवाद", "नक्सल", "आतंक", "उग्रवाद", "शहीद", "jawan", "encounter"])

    def _looks_like_administrative_update(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["बैठक", "समीक्षा", "कलेक्टर", "निर्देश", "अधिकारी", "progress", "status", "निरीक्षण", "inspection"])

    def _looks_like_scheme_implementation(self, text_l: str, schemes: List) -> bool:
        return bool(schemes) or any(kw in text_l for kw in ["लाभार्थी", "वितरण", "खाता", "subsidy", "dbt", "installments"])

    def _looks_like_election_politics(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["चुनाव", "मतदान", "वोट", "प्रचार", "कैंपेन", "प्रत्याशी", "nomination"])

    def _looks_like_industrial_development(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["उद्योग", "निवेश", "फैक्ट्री", "रोजगार", "infotech", "industrial", "mou"])

    def _looks_like_infrastructure_work(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["सड़क", "पुल", "भवन", "निर्माण", "construction", "bridge", "highway"])

    def _looks_like_relief_humanitarian(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["राहत", "आपदा", "बाढ़", "मुआवजा", "क्षतिपूर्ति", "हादसा", "दुर्घटना"])

    def _looks_like_general_political(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["डबल इंजन", "कांग्रेस", "भाजपा", "विपक्ष", "तुष्टिकरण", "भ्रष्टाचार", "आरोप"])

    def _looks_like_policy_statement(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["विकसित भारत", "मोदी की गारंटी", "सबका साथ", "संकल्प"])

    def _looks_like_cultural_religious(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["मंदिर", "पूजा", "दर्शन", "जयंती", "महोत्सव", "पर्व", "arti"])

    def _looks_like_congratulatory_general(self, text_l: str) -> bool:
        return any(kw in text_l for kw in ["बधाई", "शुभकामना", "best wishes"])

# ==========================================
# CONFIDENCE SCORER
# ==========================================

class ConfidenceScorer:
    """Compute confidence score for parsed tweet"""
    
    def compute(self, event_type: str, location: Optional[Dict], schemes: List[str], 
                target_groups: List[str], communities: List[str], orgs: List[str], 
                people: List[str], text_len: int, rescue_info: Dict[str, Any]) -> float:
        
        # Base confidence
        base_conf = 0.4
        if event_type != "अन्य":
            base_conf = 0.85
        
        # Add rescue bonus
        final_conf = base_conf + rescue_info.get("confidence_bonus", 0.0)
        
        # Location boost
        if location and location.get("canonical"):
            if event_type != "अन्य":
                final_conf += 0.08
        
        # Length validation
        is_substantial = text_len > 20
        
        # High Precision Boost
        if event_type in HIGH_PRECISION_EVENTS and is_substantial:
            if rescue_info.get("is_rescued") or final_conf > 0.7:
                final_conf = max(final_conf, 0.92)
        
        # Cap at 0.99
        return round(min(final_conf, 0.99), 3)

    def determine_review_status(self, confidence: float) -> Tuple[str, bool]:
        if confidence >= CONFIDENCE_AUTO_APPROVE:
            return "auto_approved", False
        elif confidence < CONFIDENCE_NEEDS_REVIEW:
            return "pending", True
        else:
            return "pending", True

# ==========================================
# MAIN PARSER CLASS
# ==========================================

class GeminiParserV1:
    """
    Gemini Parser V1 - Consolidated single-file parser. 
    
    Features:
    - Hybrid location resolution (dictionary + FAISS semantic + geo-hierarchy)
    - Enhanced entity extraction with intra-tweet deduplication
    - Contextual rescue logic
    - Weighted confidence scoring
    """
    
    def __init__(self, enable_full_hierarchy=True,
                 enable_semantic=True, data_dir: Optional[Path] = None):
        print("Initializing Gemini Parser V1...")
        
        self.enable_full_hierarchy = enable_full_hierarchy
        
        # Initialize components
        self.location_resolver = HybridLocationResolver(
            enable_semantic=enable_semantic,
            data_dir=data_dir
        )
        self.entity_extractor = EntityExtractor()
        self.rescue_detector = RescueDetector()
        self.confidence_scorer = ConfidenceScorer()
        
        self.stats = {
            'total_tweets': 0,
            'processing_times': [],
            'faiss_queries': 0
        }
        
        print("✅ Parser initialized")
    
    def parse_tweet(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse single tweet to v8 format.
        """
        start_time = time.time()
        
        # Extract text
        text = record.get("raw_text") or record.get("text") or ""
        
        # Get hints from older parser versions
        old_pd = (
            record.get("parsed_data_v7") or 
            record.get("parsed_data_v6") or
            record.get("parsed_data_v5") or 
            {}
        )
        
        # Extract entities (already deduplicated within each extractor)
        schemes, _ = self.entity_extractor.extract_schemes(text)
        target_groups, _ = self.entity_extractor.extract_target_groups(text)
        communities, _ = self.entity_extractor.extract_communities(text)
        orgs, _ = self.entity_extractor.extract_orgs(text)
        word_buckets, _ = self.entity_extractor.extract_word_buckets(text)
        
        # Entity Resolution: Deduplicate people (from old_pd)
        people_mentioned = list(set(old_pd.get("people_mentioned", [])))
        people_canonical = list(set(old_pd.get("people_canonical", [])))
        
        # Hybrid location resolution
        location, loc_conf = self.location_resolver.resolve(text, old_pd.get("location"))
        
        # Base event detection from keyword clusters
        base_event, base_conf = self._detect_base_event(text)
        
        # Rescue logic
        rescue_info = self.rescue_detector.rescue(text, base_event, location, schemes)
        final_event = rescue_info.get("event_type", base_event)
        content_mode = rescue_info.get("content_mode", "डिजिटल / सोशल-media पोस्ट")
        
        # Confidence scoring
        final_confidence = self.confidence_scorer.compute(
            event_type=final_event,
            location=location,
            schemes=schemes,
            target_groups=target_groups,
            communities=communities,
            orgs=orgs,
            people=people_mentioned,
            text_len=len(text),
            rescue_info=rescue_info
        )
        
        # Review status
        review_status, needs_review = self.confidence_scorer.determine_review_status(
            final_confidence
        )
        
        # Build parsed_data_v8
        parsed_data_v8 = {
            # Core fields (backward compatible)
            "event_type": final_event,
            "event_type_secondary": [],
            "event_date": record.get("created_at", "")[:10] if record.get("created_at") else None,
            "location": location,
            "people_mentioned": people_mentioned,
            "people_canonical": people_canonical,
            
            # Entity fields
            "schemes_mentioned": schemes,
            "word_buckets": word_buckets,
            "target_groups": target_groups,
            "communities": communities,
            "organizations": orgs,
            
            # Location hierarchy
            "hierarchy_path": (location or {}).get("hierarchy_path", []),
            "visit_count": (location or {}).get("visit_count", 1),
            "vector_embedding_id": (location or {}).get("vector_embedding_id"),
            
            # Confidence & review
            "confidence": final_confidence,
            "review_status": review_status,
            "needs_review": needs_review,
            
            # Content mode
            "content_mode": content_mode,
            
            # Rescue metadata
            "is_other_original": (base_event == "अन्य"),
            "is_rescued_other": rescue_info.get("is_rescued", False),
            "rescue_tag": rescue_info.get("rescue_tag"),
            "rescue_confidence_bonus": rescue_info.get("confidence_bonus", 0.0),
            
            # V8 specific fields
            "semantic_location_used": (location or {}).get("source") == "semantic",
            "location_type": (location or {}).get("location_type")  # rural/urban/district
        }
        
        processing_time = int((time.time() - start_time) * 1000)
        self.stats['processing_times'].append(processing_time)
        
        if processing_time > PROCESSING_TIMEOUT_MS:
            print(f"⚠️  Slow processing: {processing_time}ms for tweet {record.get('tweet_id')}")
        
        return {
            **record,
            "parsed_data_v8": parsed_data_v8,
            "metadata_v8": {
                "model": "gemini-parser-v1",
                "processing_time_ms": processing_time,
                "version": "1.0.0"
            }
        }
    
    def _detect_base_event(self, text: str) -> tuple:
        """
        Detect base event type from keyword clusters.
        """
        text_l = text.lower()
        
        for keywords, label in EVENT_KEYWORD_CLUSTERS:
            if any(k.lower() in text_l for k in keywords):
                return label, 0.85
        
        return "अन्य", 0.4
    
    def parse_file(self, input_path: Path, output_dir: Path):
        """
        Parse entire JSONL file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🚀 Parsing: {input_path}")
        print(f"   Output: {output_dir}/")
        
        tweets = []
        with input_path.open("r", encoding=OUTPUT_ENCODING) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    parsed = self.parse_tweet(record)
                    tweets.append(parsed)
                    
                    if line_num % 100 == 0:
                        print(f"   Processed {line_num} tweets...")
                except Exception as e:
                    print(f"   Error on line {line_num}: {e}")
                    continue
        
        self.stats['total_tweets'] = len(tweets)
        
        # Write all tweets (No tweet-level deduplication as per user request)
        output_file = output_dir / "parsed_tweets_v8.jsonl"
        
        with output_file.open("w", encoding=OUTPUT_ENCODING) as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + "\n")
        
        # Collect stats
        all_stats = self._collect_stats(tweets, None)
        stats_file = output_dir / "parsed_tweets_v8_stats.json"
        
        with stats_file.open("w", encoding=OUTPUT_ENCODING) as f:
            json.dump(all_stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Parsing complete!")
        print(f"   Total: {len(tweets)} tweets")
        print(f"   Output: {output_file}")
    
    def _collect_stats(self, tweets, dup_stats):
        """Collect comprehensive parsing statistics"""
        event_counts = {}
        location_types = {'rural': 0, 'urban': 0, 'district': 0, 'none': 0}
        confidence_bins = {'high': 0, 'medium': 0, 'low': 0}
        
        for tweet in tweets:
            pd = tweet.get("parsed_data_v8", {})
            
            # Event counts
            event = pd.get("event_type", "अन्य")
            event_counts[event] = event_counts.get(event, 0) + 1
            
            # Location types
            loc_type = pd.get("location_type")
            if loc_type in location_types:
                location_types[loc_type] += 1
            else:
                location_types['none'] += 1
            
            # Confidence bins
            conf = pd.get("confidence", 0)
            if conf >= 0.9:
                confidence_bins['high'] += 1
            elif conf >= 0.75:
                confidence_bins['medium'] += 1
            else:
                confidence_bins['low'] += 1
        
        stats = {
            "parser_version": "1.0.0",
            "total_tweets": len(tweets),
            "event_distribution": event_counts,
            "location_type_distribution": location_types,
            "confidence_distribution": confidence_bins,
            "avg_processing_time_ms": (
                sum(self.stats['processing_times']) / len(self.stats['processing_times'])
                if self.stats['processing_times'] else 0
            ),
            "location_resolver_stats": self.location_resolver.get_stats()
        }
        
        if dup_stats:
            stats["deduplication"] = dup_stats
        
        return stats

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Gemini Parser V1 - Hybrid Rule-Based + Semantic + Entity Resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("input", type=Path, help="Input JSONL file")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    parser.add_argument("--no-hierarchy", action="store_true",
                       help="Disable full hierarchy resolution (faster)")
    parser.add_argument("--no-semantic", action="store_true",
                       help="Disable FAISS semantic search (faster)")
    parser.add_argument("--data-dir", type=Path,
                       help="Custom data directory path")
    
    args = parser.parse_args()
    
    # Initialize parser
    gemini_parser = GeminiParserV1(
        enable_full_hierarchy=not args.no_hierarchy,
        enable_semantic=not args.no_semantic,
        data_dir=args.data_dir
    )
    
    # Parse file
    gemini_parser.parse_file(args.input, args.output_dir)

if __name__ == "__main__":
    main()
