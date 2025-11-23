import json
import re
import time
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import Counter, defaultdict

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

VERSION = "4.0.0"
OUTPUT_ENCODING = "utf-8"
PROCESSING_TIMEOUT_MS = 200
CONFIDENCE_AUTO_APPROVE = 0.85
CONFIDENCE_NEEDS_REVIEW = 0.40
FINGERPRINT_SIMILARITY_THRESHOLD = 0.85

# Paths (V2 Dependency)
DATA_DIR = Path("data")
GEO_FILE = DATA_DIR / "chhattisgarh_complete_geography.json"
URBAN_FILE = DATA_DIR / "datasets/chhattisgarh_urban.ndjson"
CONSTITUENCIES_FILE = DATA_DIR / "constituencies.json"  # Optional, can fallback

# ==========================================
# EMBEDDED TAXONOMIES (From V3)
# ==========================================

EVENT_KEYWORD_CLUSTERS_WEIGHTED = [
    {
        "event_type": "जनसम्पर्क / जनदर्शन",
        "weight": 1.2,
        "tier_1": ["जनसम्पर्क", "जनदर्शन", "मुलाकात", "भेंट", "दौरा", "प्रवास", "आगमन"],
        "tier_2": ["स्वागत", "अभिनंदन", "चर्चा", "संवाद"],
        "tier_3": ["शामिल", "उपस्थित", "कार्यक्रम"]
    },
    {
        "event_type": "राजनीतिक वक्तव्य",
        "weight": 1.0,
        "tier_1": ["प्रेस वार्ता", "बयान", "संबोधन", "आरोप", "प्रत्यारोप", "कांग्रेस", "भाजपा"],
        "tier_2": ["सरकार", "विपक्ष", "घोटाला", "भ्रष्टाचार", "विकास"],
        "tier_3": ["ट्वीट", "मीडिया", "पत्रकार"]
    },
    {
        "event_type": "धार्मिक / सांस्कृतिक कार्यक्रम",
        "weight": 1.1,
        "tier_1": ["पूजा", "अर्चना", "दर्शन", "आरती", "मंदिर", "महोत्सव", "जयंती", "पर्व"],
        "tier_2": ["पुण्यतिथि", "श्रद्धांजलि", "नमन", "स्मरण"],
        "tier_3": ["आयोजन", "समारोह", "उत्सव"]
    },
    {
        "event_type": "आंतरिक सुरक्षा / पुलिस",
        "weight": 1.5,
        "tier_1": ["नक्सल", "माओवादी", "शहीद", "मुठभेड़", "गिरफ्तार", "आत्मसमर्पण", "बरामद"],
        "tier_2": ["पुलिस", "जवान", "सुरक्षा", "बल", "आईईडी"],
        "tier_3": ["सर्चिंग", "अभियान", "थाना"]
    },
    {
        "event_type": "खेल / गौरव",
        "weight": 1.4,
        "tier_1": ["पदक", "मेडल", "विजेता", "चैंपियन", "खेल", "खिलाड़ी", "जीत"],
        "tier_2": ["प्रतियोगिता", "टूर्नामेंट", "आयोजन"],
        "tier_3": ["बधाई", "शुभकामनाएं"]
    },
    {
        "event_type": "आपदा / दुर्घटना",
        "weight": 1.3,
        "tier_1": ["हादसा", "दुर्घटना", "मौत", "घायल", "आग", "बाढ़", "सूखा"],
        "tier_2": ["राहत", "बचाव", "मुआवजा"],
        "tier_3": ["नुकसान", "क्षति"]
    },
    {
        "event_type": "बैठक",
        "weight": 1.0,
        "tier_1": ["बैठक", "समीक्षा", "मीटिंग"],
        "tier_2": ["अधिकारी", "निर्देश", "चर्चा"],
        "tier_3": ["आयोजित", "संपन्न"]
    },
    {
        "event_type": "उद्घाटन",
        "weight": 1.2,
        "tier_1": ["उद्घाटन", "लोकार्पण", "शिलान्यास", "भूमिपूजन"],
        "tier_2": ["सौगात", "शुभारंभ"],
        "tier_3": ["विकास कार्य"]
    },
    {
        "event_type": "योजना घोषणा",
        "weight": 1.2,
        "tier_1": ["योजना", "घोषणा", "लागू", "शुभारंभ"],
        "tier_2": ["लाभार्थी", "वितरण", "खाता"],
        "tier_3": ["सरकार", "पहल"]
    },
    {
        "event_type": "शुभकामना / बधाई",
        "weight": 0.8,
        "tier_1": ["बधाई", "शुभकामनाएं", "हार्दिक"],
        "tier_2": ["प्रसन्नता", "खुशी"],
        "tier_3": ["मंगलमय"]
    },
    {
        "event_type": "शोक संदेश",
        "weight": 1.3,
        "tier_1": ["निधन", "शोक", "दुखद", "श्रद्धांजलि", "ईश्वर"],
        "tier_2": ["आत्मा", "शांति", "संवेदना"],
        "tier_3": ["परिवार"]
    },
    {
        "event_type": "जन्मदिन शुभकामना",
        "weight": 1.2,
        "tier_1": ["जन्मदिन", "अवतरण दिवस", "दीर्घायु"],
        "tier_2": ["स्वस्थ", "जीवन"],
        "tier_3": ["कामना"]
    },
    {
        "event_type": "सम्मान / Felicitation",
        "weight": 1.1,
        "tier_1": ["सम्मान", "पुरस्कार", "सम्मानित", "प्रशस्ति"],
        "tier_2": ["गौरव", "उपलब्धि"],
        "tier_3": ["समारोह"]
    },
    {
        "event_type": "निरीक्षण",
        "weight": 1.1,
        "tier_1": ["निरीक्षण", "जायजा", "अवलोकन"],
        "tier_2": ["स्थल", "कार्य"],
        "tier_3": ["भ्रमण"]
    },
    {
        "event_type": "प्रशासनिक समीक्षा बैठक",
        "weight": 1.2,
        "tier_1": ["कलेक्टर", "एसपी", "कमिश्नर", "समीक्षा बैठक", "टीएल"],
        "tier_2": ["निर्देश", "पालन", "रिपोर्ट"],
        "tier_3": ["विभाग"]
    },
    {
        "event_type": "रैली",
        "weight": 1.1,
        "tier_1": ["रैली", "जुलूस", "प्रदर्शन", "सभा"],
        "tier_2": ["नारेबाजी", "भीड़"],
        "tier_3": ["शामिल"]
    },
    {
        "event_type": "चुनाव प्रचार",
        "weight": 1.2,
        "tier_1": ["प्रचार", "जनसंपर्क", "वोट", "मतदान"],
        "tier_2": ["प्रत्याशी", "उम्मीदवार"],
        "tier_3": ["समर्थन"]
    }
]

SCHEME_PATTERNS = {
    r"पीएम\s*आवास": "प्रधानमंत्री आवास योजना",
    r"PMAY": "प्रधानमंत्री आवास योजना",
    r"महतारी\s*वंदन": "महतारी वंदन योजना",
    r"किसान\s*न्याय": "राजीव गांधी किसान न्याय योजना",
    r"गोधन\s*न्याय": "गोधन न्याय योजना",
    r"मनरेगा": "मनरेगा",
    r"MNREGA": "मनरेगा",
    r"आयुष्मान": "आयुष्मान भारत",
    r"उज्ज्वला": "प्रधानमंत्री उज्ज्वला योजना",
    r"जन\s*धन": "प्रधानमंत्री जन धन योजना",
    r"स्वच्छ\s*भारत": "स्वच्छ भारत मिशन",
    r"जल\s*जीवन": "जल जीवन मिशन",
    r"GST": "GST"
}

WORD_BUCKETS = {
    "agriculture": ["किसान", "कृषि", "धान", "फसल", "बीज", "खाद", "सिंचाई", "बोनस", "समर्थन मूल्य", "MSP"],
    "education": ["शिक्षा", "स्कूल", "कॉलेज", "विद्यार्थी", "छात्र", "शिक्षक", "भर्ती", "परीक्षा", "परिणाम"],
    "health": ["स्वास्थ्य", "अस्पताल", "इलाज", "डॉक्टर", "दवा", "मेडिकल", "एम्बुलेंस", "टीकाकरण"],
    "infrastructure": ["सड़क", "बिजली", "पानी", "निर्माण", "पुल", "भवन", "रेलवे", "कनेक्टिविटी"],
    "welfare": ["राशन", "पेंशन", "आवास", "गरीब", "कल्याण", "सहायता", "अनुदान"],
    "governance": ["प्रशासन", "योजना", "बैठक", "समीक्षा", "निरीक्षण", "उद्घाटन", "लोकार्पण"],
    "security": ["पुलिस", "नक्सल", "सुरक्षा", "कानून", "अपराध", "गिरफ्तार", "जवान"],
    "culture": ["संस्कृति", "त्योहार", "परंपरा", "मेला", "महोत्सव", "कला", "पर्यटन"],
    "employment": ["रोजगार", "नौकरी", "भर्ती", "स्वरोजगार", "कौशल", "प्रशिक्षण"],
    "development": ["विकास", "प्रगति", "सौगात", "आधारशिला", "विकसित"]
}

COMMUNITIES = {
    "farmers": ["किसान", "कृषक", "अन्नदाता"],
    "women": ["महिला", "नारी", "माता", "बहन", "बेटी", "शक्ति", "महतारी"],
    "youth": ["युवा", "छात्र", "विद्यार्थी", "बेरोजगार"],
    "scheduled_tribes": ["आदिवासी", "वनवासी", "जनजाति", "ST"],
    "scheduled_castes": ["दलित", "अनुसूचित जाति", "SC"],
    "obc": ["पिछड़ा वर्ग", "OBC", "साहू", "कुर्मी", "यादव"],
    "general": ["सामान्य वर्ग", "सवर्ण"],
    "students": ["छात्र", "छात्राएं", "विद्यार्थी"]
}

ORGANIZATIONS = {
    "political": ["भाजपा", "कांग्रेस", "बीजेपी", "INC", "आप", "बसपा", "जकांछ"],
    "government": ["सरकार", "शासन", "प्रशासन", "विभाग", "मंत्रालय", "आयोग", "निगम", "मंडल"],
    "corporate": ["अडानी", "अंबानी", "टाटा", "जिंदल", "बालको", "एनटीपीसी", "SECL"],
    "ngo": ["समिति", "संगठन", "संघ", "फाउंडेशन", "ट्रस्ट", "सेवा"]
}

CONSENSUS_WEIGHTS = {
    'keyword': 0.25,
    'semantic': 0.20,
    'hierarchy': 0.20,
    'rescue': 0.15,
    'dictionary': 0.10,
    'faiss_agreement': 0.10
}

# Manual mappings for villages where Hindi name is missing or in English script in dataset
MANUAL_VILLAGE_MAPPING = {
    "सिलोतरा": "Siltara",
    "कुकुर्दा": "Kukurda",
    "लैलूंगा": "Lailunga",
    "तमनार": "Tamnar",
    "पत्थलगांव": "Pathalgaon",
    "धरमजयगढ़": "Dharamjaigarh",
    "बस्तर": "Bastar",
    "कोंडागाँव": "Kondagaon",
    "कोंटा": "Konta",
    "गीदम": "Geedam",
    "बसना": "Basna",
    "मनेंद्रगढ़": "Manendragarh",
    "नारायणपुर": "Narayanpur",
    "भानुप्रतापपुर": "Bhanupratappur",
    "डोंगरगढ़": "Dongargarh",
    "खैरागढ़": "Khairagarh",
    "पेंड्रा": "Pendra",
    "मरवाही": "Marwahi",
    "सारंगढ़": "Sarangarh",
    "बिलाईगढ़": "Bilaigarh",
    "शक्ति": "Sakti",
    "मोहला": "Mohla",
    "मानपुर": "Manpur",
    "रायपुर": "Raipur"
}

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def load_json(path: Path) -> Dict:
    """Load JSON file safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def load_ndjson(path: Path) -> List[Dict]:
    """Load NDJSON file safely."""
    data = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception as e:
        print(f"Error loading {path}: {e}")
    return data

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    if not text: return ""
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    text = clean_text(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ==========================================
# LOGIC CLASSES (From V3)
# ==========================================

class MultiSignalEventDetector:
    """Advanced event detection using multiple weighted signals."""
    def __init__(self):
        self.clusters = EVENT_KEYWORD_CLUSTERS_WEIGHTED
    
    def detect(self, text: str) -> Tuple[str, float, List[str]]:
        text_lower = text.lower()
        scores = {}
        for cluster in self.clusters:
            event_type = cluster["event_type"]
            score = 0.0
            tier_1_matches = sum(1 for kw in cluster["tier_1"] if kw in text_lower)
            if tier_1_matches > 0: score += min(tier_1_matches * 0.6, 1.0)
            tier_2_matches = sum(1 for kw in cluster["tier_2"] if kw in text_lower)
            if tier_2_matches > 0: score += min(tier_2_matches * 0.3, 0.6)
            tier_3_matches = sum(1 for kw in cluster["tier_3"] if kw in text_lower)
            if tier_3_matches > 0: score += min(tier_3_matches * 0.1, 0.3)
            score *= cluster["weight"]
            if score > 0: scores[event_type] = min(score, 1.0)
        
        if not scores: return "अन्य", 0.3, []
        sorted_events = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_event, primary_score = sorted_events[0]
        secondary_events = [e for e, s in sorted_events[1:] if s > 0.4][:3]
        return primary_event, primary_score, secondary_events

class TieredRescueDetector:
    """Sophisticated rescue logic with tiered scoring."""
    RESCUE_TIERS = {
        'sports_critical': {'patterns': [r'(मैच|match)\s*(जीत|won|win)', r'(पदक|medal)\s*(जीत|won)', r'(ओलंपिक|olympic)', r'(चैंपियन|champion)'], 'weight': 1.0, 'confidence_boost': 0.25, 'target_event': 'खेल / गौरव'},
        'security_critical': {'patterns': [r'(माओवाद|naxal|नक्सल)', r'(शहीद|martyr)', r'(आत्मसमर्पण|surrender)', r'(encounter|मुठभेड़)'], 'weight': 1.0, 'confidence_boost': 0.25, 'target_event': 'आंतरिक सुरक्षा / पुलिस'},
        'admin_high': {'patterns': [r'(समीक्षा\s*बैठक)', r'(कलेक्टर|collector)', r'(अधिकारियों\s*के\s*साथ)'], 'weight': 0.8, 'confidence_boost': 0.18, 'target_event': 'प्रशासनिक समीक्षा बैठक'},
        'political_high': {'patterns': [r'(डबल\s*इंजन)', r'(भ्रष्टाचार|corruption)', r'(विकसित\s*भारत)', r'(मोदी\s*की\s*गारंटी)'], 'weight': 0.8, 'confidence_boost': 0.18, 'target_event': 'राजनीतिक वक्तव्य'}
    }
    
    def rescue(self, text: str, current_event: str, location: Optional[Dict], schemes: List[str]) -> Dict[str, Any]:
        rescue_info = {"event_type": current_event, "content_mode": "डिजिटल / सोशल-मीडिया पोस्ट", "is_rescued": False, "rescue_tag": None, "confidence_bonus": 0.0}
        if current_event != "अन्य": return rescue_info
        text_lower = text.lower()
        tier_scores = {}
        for tier_name, tier_config in self.RESCUE_TIERS.items():
            matches = sum(1 for p in tier_config['patterns'] if re.search(p, text_lower))
            if matches > 0:
                score = min(matches / len(tier_config['patterns']), 1.0) * tier_config['weight']
                tier_scores[tier_name] = {'score': score, 'config': tier_config}
        if not tier_scores: return rescue_info
        best_tier = max(tier_scores.items(), key=lambda x: x[1]['score'])
        tier_name, tier_data = best_tier
        if tier_data['score'] > 0.5:
            rescue_info.update({"event_type": tier_data['config']['target_event'], "is_rescued": True, "rescue_tag": tier_name, "confidence_bonus": tier_data['config']['confidence_boost']})
            if 'sports' in tier_name: rescue_info["content_mode"] = "खेल / उपलब्धि पर प्रतिक्रिया"
            elif 'security' in tier_name or 'political' in tier_name: rescue_info["content_mode"] = "नीति / वक्तव्य"
            else: rescue_info["content_mode"] = "मैदान-स्तर कार्यक्रम"
        return rescue_info

class EnhancedEntityExtractor:
    """Comprehensive entity extraction."""
    def extract_schemes(self, text: str) -> List[str]:
        schemes = set()
        for pattern, canonical in SCHEME_PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE): schemes.add(canonical)
        return sorted(list(schemes))
    
    def extract_word_buckets(self, text: str) -> List[str]:
        text_lower = text.lower()
        buckets = set()
        for bucket_name, keywords in WORD_BUCKETS.items():
            if any(kw in text_lower for kw in keywords): buckets.add(bucket_name)
        return sorted(list(buckets))
    
    def extract_communities(self, text: str) -> List[str]:
        text_lower = text.lower()
        communities = set()
        for community_name, keywords in COMMUNITIES.items():
            if any(kw in text_lower for kw in keywords): communities.add(community_name)
        return sorted(list(communities))
    
    def extract_organizations(self, text: str) -> List[str]:
        text_lower = text.lower()
        orgs = set()
        for org_type, keywords in ORGANIZATIONS.items():
            if any(kw in text_lower for kw in keywords): orgs.add(org_type)
        return sorted(list(orgs))
    
    def extract_target_groups(self, text: str) -> List[str]:
        groups = set()
        text_lower = text.lower()
        for community_name, keywords in COMMUNITIES.items():
            if any(kw in text_lower for kw in keywords): groups.add(community_name)
        return sorted(list(groups))

class ConsensusConfidenceScorer:
    """Multi-signal consensus-based confidence scoring."""
    def calculate(self, signals: Dict[str, float]) -> float:
        weighted_sum = 0.0
        total_weight = 0.0
        for signal_name, weight in CONSENSUS_WEIGHTS.items():
            if signal_name in signals and signals[signal_name] is not None:
                weighted_sum += signals[signal_name] * weight
                total_weight += weight
        if total_weight == 0: return 0.3
        base_confidence = weighted_sum / total_weight
        high_conf_signals = sum(1 for s in signals.values() if s and s > 0.8)
        if high_conf_signals >= 3: base_confidence *= 1.1
        return min(base_confidence, 1.0)
    
    def determine_review_status(self, confidence: float, event_type: str) -> Tuple[str, bool]:
        high_precision_events = ["शोक संदेश", "जन्मदिन शुभकामना", "आंतरिक सुरक्षा / पुलिस", "खेल / गौरव", "आपदा / दुर्घटना"]
        threshold = 0.92 if event_type in high_precision_events else CONFIDENCE_AUTO_APPROVE
        if confidence >= threshold: return "auto_approved", False
        return "pending", True

# ==========================================
# GEO HIERARCHY RESOLVER (From V2)
# ==========================================

class GeoHierarchyResolver:
    """Resolve complete administrative hierarchy using comprehensive external data."""
    
    def __init__(self):
        print("Loading geography data...")
        self.villages_data = self._load_geography_ndjson()
        self.urban_data = self._load_urban_data()
        
        # Build indexes
        self.village_index = self._build_village_index()
        self.ulb_index = self._build_ulb_index()
        self.district_map = self._build_district_map()
        
        print(f"Loaded {len(self.village_index)} villages, {len(self.ulb_index)} ULBs, {len(self.district_map)} districts")
        
        self.stats = {'dict_hits': 0, 'hierarchy_hits': 0, 'not_found': 0}
        
        # Context Keywords for Disambiguation
        self.CONTEXT_KEYWORDS = {
            'urban': {
                'ward', 'zone', 'parshad', 'parishad', 'nagar', 'nigam', 'palika', 'cm', 'mayor', 'mahapaur', 
                'chairman', 'sabhapati', 'alderman', 'smart city', 'traffic', 'sadak', 'naali',
                'वार्ड', 'जोन', 'पार्षद', 'परिषद', 'नगर', 'निगम', 'पालिका', 'महापौर', 'सभापति', 'स्मार्ट सिटी', 'सड़क', 'नाली'
            },
            'rural': {
                'gram', 'panchayat', 'sarpanch', 'sachiv', 'janpad', 'mnrega', 'kisan', 'khet', 'fasal', 
                'kharif', 'rabi', 'paddy', 'dhan', 'gothan', 'aadiwasi', 'van', 'jungle',
                'ग्राम', 'पंचायत', 'सरपंच', 'सचिव', 'जनपद', 'मनरेगा', 'किसान', 'खेत', 'फसल', 'खरीफ', 'रबी', 'धान', 'गौठान', 'आदिवासी', 'वन', 'जंगल'
            }
        }

    def _detect_context(self, text: str) -> str:
        """Detect if text context is predominantly urban or rural."""
        text_lower = text.lower()
        urban_score = sum(1 for kw in self.CONTEXT_KEYWORDS['urban'] if kw in text_lower)
        rural_score = sum(1 for kw in self.CONTEXT_KEYWORDS['rural'] if kw in text_lower)
        
        if urban_score > rural_score: return 'urban'
        if rural_score > urban_score: return 'rural'
        return 'neutral'

    def _load_geography_ndjson(self) -> List[Dict]:
        """Load comprehensive geography from NDJSON (17MB)."""
        ndjson_path = DATA_DIR / "datasets/chhattisgarh_geography.ndjson"
        if ndjson_path.exists():
            return load_ndjson(ndjson_path)
        print(f"⚠️  Geography file not found: {ndjson_path}")
        return []

    def _load_urban_data(self) -> List[Dict]:
        if URBAN_FILE.exists(): return load_ndjson(URBAN_FILE)
        return []

    def _build_village_index(self) -> Dict[str, Dict]:
        """Build index from flat NDJSON records."""
        index = {}
        for row in self.villages_data:
            # NDJSON fields: district, block, gram_panchayat, village
            v_name_en = row.get("village")
            
            # Get Hindi name from variants
            v_name_hi = None
            if "variants" in row and "village" in row["variants"]:
                v_name_hi = row["variants"]["village"].get("hindi")
            
            dist_name = row.get("district")
            block_name = row.get("block")
            gp_name = row.get("gram_panchayat")
            
            # Build hierarchy
            hierarchy = [
                "छत्तीसगढ़",
                f"{dist_name} जिला",
                f"{block_name} विकासखंड",
                f"{gp_name} पंचायत",
                v_name_en
            ]
            
            # Create location object
            loc_data = {
                "district": dist_name,
                "block": block_name,
                "gp": gp_name,
                "assembly": None,
                "hierarchy_path": hierarchy,
                "type": "rural",
                "canonical": v_name_en  # Use English as canonical for consistency, or Hindi if preferred
            }
            
            # Index English name
            if v_name_en:
                index[v_name_en] = loc_data
            
            # Index Hindi name
            if v_name_hi:
                # Create a copy with Hindi canonical if we want, or keep English canonical
                # For now, let's keep English canonical but allow lookup by Hindi
                index[v_name_hi] = loc_data
        
        # Apply Manual Mappings
        for hindi_name, english_name in MANUAL_VILLAGE_MAPPING.items():
            if english_name in index:
                index[hindi_name] = index[english_name]
                
        return index
    
    def _build_ulb_index(self) -> Dict[str, Dict]:
        index = {}
        for row in self.urban_data:
            ulb = row.get("ulb") or row.get("nagar_nigam") or row.get("nagar_palika")
            if ulb:
                index[ulb] = {
                    "district": row.get("district"), "ulb_type": row.get("ulb_type"),
                    "assembly": row.get("assembly"), "hierarchy_path": ["छत्तीसगढ़", f"{row.get('district', '')} जिला", ulb],
                    "type": "urban", "canonical": ulb
                }
        return index

    def _build_district_map(self) -> Dict[str, Dict]:
        index = {}
        # Extract unique districts from village data
        for row in self.villages_data:
            name = row.get("district")
            if name and name not in index:
                index[name] = {"canonical": name, "hierarchy": ["छत्तीसगढ़", f"{name} जिला"], "type": "district"}
        return index
    
    def resolve(self, text: str) -> Tuple[Optional[Dict], float]:
        """Multi-stage location resolution."""
        potential_matches = []
        
        # Extract candidates using V3's robust regex
        candidates = self._extract_location_candidates(text)
        all_tokens = self._extract_all_tokens(text)
        all_candidates = list(set(candidates + all_tokens))
        
        for candidate in all_candidates:
            if len(candidate) < 2: continue
            
            # Check village index
            if candidate in self.village_index:
                loc = self.village_index[candidate]
                potential_matches.append((self._format_location(loc), 0.95, 'hierarchy'))
            
            # Check ULB index
            if candidate in self.ulb_index:
                loc = self.ulb_index[candidate]
                
                # Extract ward/zone from context
                ward = self._extract_ward(text)
                zone = self._extract_zone(text)
                
                # Create a copy to avoid modifying the index
                loc_copy = loc.copy()
                loc_copy['ward'] = ward
                loc_copy['zone'] = zone
                
                if ward:
                    loc_copy['hierarchy_path'] = loc['hierarchy_path'] + [f"वार्ड {ward}"]
                
                potential_matches.append((self._format_location(loc_copy), 0.90, 'hierarchy'))
            
            # Check district
            if candidate in self.district_map:
                loc = self.district_map[candidate]
                potential_matches.append((self._format_location(loc), 0.85, 'hierarchy'))
        
        if potential_matches:
            best_match = self._select_best_match(potential_matches, text)
            self.stats['hierarchy_hits'] += 1
            return best_match[0], best_match[1]
        
        self.stats['not_found'] += 1
        return None, 0.0

    def _extract_location_candidates(self, text: str) -> List[str]:
        patterns = [
            r"जिला\s+([^\s,।]+)", r"विधानसभा\s+([^\s,।]+)", r"तहसील\s+([^\s,।]+)",
            r"थाना\s+([^\s,।]+)", r"विकासखंड\s+([^\s,।]+)", r"ग्राम\s+पंचायत\s+([^\s,।]+)",
            r"गाँव\s+([^\s,।]+)", r"गांव\s+([^\s,।]+)", r"ग्राम\s+([^\s,।]+)",
            r"([^\s,।]+)\s+जिला", r"([^\s,।]+)\s+विधानसभा",
            r"नगर\s+निगम\s+([^\s,।]+)", r"नगर\s+पालिका\s+([^\s,।]+)", r"नगर\s+पंचायत\s+([^\s,।]+)"
        ]
        candidates = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip()
                if len(name) >= 2: candidates.append(name)
        return list(set(candidates))
    
    def _extract_all_tokens(self, text: str) -> List[str]:
        tokens = re.split(r'[\s,।\-!?;:"]+', text)
        stop_words = {"का", "के", "की", "में", "से", "को", "पर", "और", "है", "हैं", "कि", "भी", "ही", "ने", "एक", "किया", "कर", "रहे", "थी", "थे"}
        return [t for t in tokens if len(t) >= 2 and t not in stop_words]
    
    def _extract_ward(self, text: str) -> Optional[str]:
        """Extract ward number."""
        match = re.search(r'(?:वार्ड|ward)\s*(?:क्रमांक|no|number|नंबर|नं)?\s*[\.:-]?\s*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_zone(self, text: str) -> Optional[str]:
        """Extract zone number."""
        match = re.search(r'(?:जोन|zone)\s*(?:क्रमांक|no|number|नंबर|नं)?\s*[\.:-]?\s*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _format_location(self, loc: Dict) -> Dict:
        return {
            'canonical': loc['canonical'],
            'district': loc.get('district', loc.get('canonical')), # For districts, district IS the canonical name
            'location_type': loc['type'],
            'hierarchy_path': loc.get('hierarchy_path', []),
            'assembly': loc.get('assembly'),
            'block': loc.get('block'),
            'gp': loc.get('gp'),
            'village': loc['canonical'] if loc['type'] == 'rural' else None,
            'ulb': loc['canonical'] if loc['type'] == 'urban' else None,
            'ward': loc.get('ward'),
            'zone': loc.get('zone'),
            'canonical_key': f"CG_{loc['type'].upper()}_{loc['canonical']}",
            'source': 'hierarchy_resolver',
            'visit_count': 1
        }
    
    def _select_best_match(self, matches: List[Tuple], text: str) -> Tuple:
        """Select best match using smart context scoring."""
        context_type = self._detect_context(text)
        text_lower = text.lower()
        
        def specificity_score(match_tuple):
            loc, conf, src = match_tuple
            score = 0.5 # Base score
            
            ltype = loc.get('location_type')
            canonical = loc.get('canonical', '').lower()
            
            # 1. Specificity Bonus
            if ltype == 'rural': score += 0.3
            elif ltype == 'urban': score += 0.2
            elif ltype == 'district': score += 0.1
            
            # 2. Context Bonus
            if context_type == 'urban' and ltype == 'urban': score += 0.5
            if context_type == 'rural' and ltype == 'rural': score += 0.5
            
            # 3. Explicit Prefix/Suffix Bonus
            # Check for "Gram <Name>" or "<Name> Gram"
            if ltype == 'rural':
                if re.search(f"(gram|panchayat)\\s+{re.escape(canonical)}", text_lower) or \
                   re.search(f"{re.escape(canonical)}\\s+(gram|panchayat)", text_lower):
                    score += 1.0
            
            # Check for "Nagar <Name>" or "<Name> Nagar" or "Ward <Name>"
            if ltype == 'urban':
                if re.search(f"(nagar|ward|zone|parshad|parishad)\\s+.*{re.escape(canonical)}", text_lower) or \
                   re.search(f"{re.escape(canonical)}\\s+(nagar|ward|zone|parshad|parishad)", text_lower):
                    score += 1.0
                
            # 4. Hierarchy Depth Bonus
            score += len(loc.get('hierarchy_path', [])) * 0.05
            
            # 5. Confidence
            score += conf
            
            return score
            
        return max(matches, key=specificity_score)
    
    def get_stats(self) -> Dict:
        return self.stats

# ==========================================
# MAIN PARSER CLASS
# ==========================================

class GeminiParserFinal:
    """
    Definitive Parser (V4) merging V2 data loading with V3 logic.
    """
    def __init__(self):
        print("Initializing Gemini Parser Final (V4)...")
        self.event_detector = MultiSignalEventDetector()
        self.rescue_detector = TieredRescueDetector()
        self.entity_extractor = EnhancedEntityExtractor()
        self.location_resolver = GeoHierarchyResolver()
        self.confidence_scorer = ConsensusConfidenceScorer()
        
        self.stats = {
            'total_tweets': 0,
            'processing_times': [],
            'event_distribution': Counter(),
            'location_type_distribution': Counter(),
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        print("✅ Parser initialized")
    
    def parse_tweet(self, tweet: Dict) -> Dict:
        start_time = time.time()
        text = tweet.get('text', '')
        
        # Stage 1: Event Detection
        primary_event, event_confidence, secondary_events = self.event_detector.detect(text)
        
        # Stage 2: Location Resolution
        location, location_confidence = self.location_resolver.resolve(text)
        
        # Stage 3: Entity Extraction
        schemes = self.entity_extractor.extract_schemes(text)
        word_buckets = self.entity_extractor.extract_word_buckets(text)
        communities = self.entity_extractor.extract_communities(text)
        organizations = self.entity_extractor.extract_organizations(text)
        target_groups = self.entity_extractor.extract_target_groups(text)
        
        # Stage 4: Rescue Detection
        rescue_info = self.rescue_detector.rescue(text, primary_event, location, schemes)
        if rescue_info['is_rescued']:
            primary_event = rescue_info['event_type']
            content_mode = rescue_info['content_mode']
            rescue_bonus = rescue_info['confidence_bonus']
        else:
            content_mode = "डिजिटल / सोशल-मीडिया पोस्ट"
            rescue_bonus = 0.0
        
        # Stage 5: Confidence Scoring
        confidence_signals = {
            'keyword': event_confidence,
            'hierarchy': location_confidence if location else 0.0,
            'rescue': rescue_bonus,
            'dictionary': 0.0 # Dictionary lookup merged into hierarchy resolver
        }
        final_confidence = self.confidence_scorer.calculate(confidence_signals)
        review_status, needs_review = self.confidence_scorer.determine_review_status(final_confidence, primary_event)
        
        # Build parsed data
        parsed_data = {
            'event_type': primary_event,
            'event_type_secondary': secondary_events,
            'event_date': tweet.get('created_at', '')[:10] if tweet.get('created_at') else '',
            'location': location if location else {},
            'people_mentioned': [],
            'people_canonical': [],
            'schemes_mentioned': schemes,
            'word_buckets': word_buckets,
            'target_groups': target_groups,
            'communities': communities,
            'organizations': organizations,
            'hierarchy_path': location.get('hierarchy_path', []) if location else [],
            'visit_count': 1,
            'vector_embedding_id': None,
            'confidence': round(final_confidence, 2),
            'review_status': review_status,
            'needs_review': needs_review,
            'content_mode': content_mode,
            'is_other_original': primary_event == "अन्य" and not rescue_info['is_rescued'],
            'is_rescued_other': rescue_info['is_rescued'],
            'rescue_tag': rescue_info.get('rescue_tag'),
            'rescue_confidence_bonus': rescue_bonus,
            'semantic_location_used': False,
            'location_type': location.get('location_type', '') if location else ''
        }
        
        # Stats
        processing_time = int((time.time() - start_time) * 1000)
        self.stats['processing_times'].append(processing_time)
        self.stats['event_distribution'][primary_event] += 1
        if location: self.stats['location_type_distribution'][location.get('location_type', 'unknown')] += 1
        
        output_tweet = tweet.copy()
        output_tweet['parsed_data_v8'] = parsed_data
        output_tweet['metadata_v8'] = {'model': 'gemini-parser-final', 'processing_time_ms': processing_time, 'version': VERSION}
        return output_tweet

    def parse_file(self, input_path: Path, output_dir: Path):
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🚀 Parsing: {input_path}")
        print(f"   Output: {output_dir}/\n")
        
        tweets = []
        with input_path.open('r', encoding='utf-8') as f:
            for line in f:
                if line.strip(): tweets.append(json.loads(line))
        
        self.stats['total_tweets'] = len(tweets)
        parsed_tweets = []
        
        for i, tweet in enumerate(tweets):
            parsed = self.parse_tweet(tweet)
            parsed_tweets.append(parsed)
            if (i + 1) % 100 == 0: print(f"   Processed {i + 1} tweets...")
        
        output_file = output_dir / "parsed_tweets_v8.jsonl"
        with output_file.open('w', encoding=OUTPUT_ENCODING) as f:
            for tweet in parsed_tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        
        # Stats
        avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0
        stats_output = {
            'total_tweets': self.stats['total_tweets'],
            'event_distribution': dict(self.stats['event_distribution']),
            'location_type_distribution': dict(self.stats['location_type_distribution']),
            'average_processing_time_ms': round(avg_time, 2),
            'location_resolver_stats': self.location_resolver.get_stats(),
            'version': VERSION
        }
        with (output_dir / "parsed_tweets_v8_stats.json").open('w', encoding=OUTPUT_ENCODING) as f:
            f.write(json.dumps(stats_output, ensure_ascii=False, indent=2))
        
        print(f"\n✅ Parsing complete!")
        print(f"   Total: {len(parsed_tweets)} tweets")
        print(f"   Output: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Gemini Parser Final (V4)')
    parser.add_argument('input_file', type=str, help='Input JSONL file')
    parser.add_argument('output_dir', type=str, help='Output directory')
    args = parser.parse_args()
    
    gemini_parser = GeminiParserFinal()
    gemini_parser.parse_file(Path(args.input_file), Path(args.output_dir))

if __name__ == '__main__':
    main()
