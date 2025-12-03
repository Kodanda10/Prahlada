#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Dhruv – Parsing Logic V7.0 ("Think Harder" Edition)

Optimizations over V6:
1. 🛡️ **False Positive Protection**: "Victory/Win" removed from standalone Sports rescue (prevents Election confusion).
2. ⚖️ **Logic Re-Balancing**: 'Administrative Review' now prioritized OVER 'Scheme Announcement' (prevents "Reviewing Scheme" -> "New Scheme").
3. 📍 **Hyper-Local Extraction**: Added Tahsil, Thana, Block, and Chowki to inline location detection.
4. 🧠 **Contextual Confidence**: Boosts require signal validation (length > 20 chars) to prevent short-text errors.

Usage:
  python3 parse_v7.py input.jsonl output.jsonl
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

# -------------------------
# 1. Taxonomy & Constants
# -------------------------

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
    "डिजिटल / सोशल-मीडिया पोस्ट",
    "खेल / उपलब्धि पर प्रतिक्रिया",
    "सामान्य शुभकामनाएँ / पर्व",
]

# High-Precision Clusters (Used for Base Detection)
EVENT_KEYWORD_CLUSTERS: List[Tuple[List[str], str]] = [
    (["माओवाद", "नक्सल", "नक्सली", "लाल आतंक", "सुरक्षा बल", "जवानों", "शहीद", 
      "आत्मसमर्पण", "बस्तर ओलंपिक", "ऑपरेशन", "पुलिस स्मृति", "police", "jawan", "encounter", "ied"], "आंतरिक सुरक्षा / पुलिस"),

    (["मैच जीत", "टीम इंडिया", "क्रिकेट", "पदक", "स्वर्ण पदक", "खिलाड़ी", 
      "ओलंपिक", "खेल", "tournament", "चैंपियंस ट्रॉफी", "गर्व का क्षण", "medal", "won", "winner", "bcci"], "खेल / गौरव"),

    (["हादसा", "दुर्घटना", "रेल हादसा", "बस हादसा", "आगजनी", "बाढ़", "प्राकृतिक आपदा", "accident", "tragedy", "collision"], "आपदा / दुर्घटना"),

    (["डबल इंजन", "कांग्रेस सरकार", "भ्रष्टाचार", "तुष्टिकरण", "आपातकाल", 
      "विकसित भारत", "मोदी की गारंटी", "विपक्ष", "आरोप", "statement", "political", "manifesto"], "राजनीतिक वक्तव्य"),

    (["बैठक", "मुलाकात", "भेंट", "बैठक ली", "बैठक में", "बैठक का", "अध्यक्षता की", "सत्र", "सदन की कार्यवाही"], "बैठक"),
    (["जनसम्पर्क", "जन संपर्क", "जनसंपर्क", "जनदर्शन", "जन-दर्शन", "जन सुनवाई", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन"),
    (["समीक्षा बैठक", "समीक्षा की", "समीक्षा की गई", "अधिकारियों के साथ", "विभागीय बैठक", "कलेक्टर", "कलेक्टरेट", "समीक्षा कार्य"], "प्रशासनिक समीक्षा बैठक"),
    (["निरीक्षण", "निरीक्षण किया", "निरीक्षण हेतु", "inspection"], "निरीक्षण"),
    (["रैली", "जनसभा", "public rally", "road show", "रोड शो"], "रैली"),
    (["चुनावी", "मतदाता", "मतदान", "चुनाव प्रचार", "poll campaign", "voting", "polling"], "चुनाव प्रचार"),
    (["उद्घाटन", "लोकार्पण", "inauguration", "inaugurated", "शिलान्यास", "dedication"], "उद्घाटन"),
    (["घोषणा", "नई योजना", "योजना की जानकारी", "योजना का लाभ", "scheme launch"], "योजना घोषणा"),
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "गुरु नानक", "मस्जिद", "धार्मिक", "सांस्कृतिक कार्यक्रम", "जयंती", "pujya", "saints"], "धार्मिक / सांस्कृतिक कार्यक्रम"),
    (["सम्मान", "सम्मानित", "शॉल", "श्रीफल", "समारोह", "felicitation", "award"], "सम्मान / Felicitation"),
    (["प्रेस वार्ता", "प्रेस कॉन्फ़्रेंस", "मीडिया ब्रिफिंग", "मीडिया से बातचीत", "pc"], "प्रेस कॉन्फ़्रेंस / मीडिया"),
    (["शुभकामनाएं", "शुभकामनाएँ", "बधाई", "congratulations", "best wishes", "greetings"], "शुभकामना / बधाई"),
    (["जन्मदिन", "birthday", "अवतरण दिवस"], "जन्मदिन शुभकामना"),
    (["श्रद्धांजलि", "शोक संदेश", "दिवंगत", "अंतिम यात्रा", "पुण्यतिथि", "condolence", "tribute", "rip"], "शोक संदेश"),
]

SCHEME_PATTERNS = {
    r"\bPMAY\b": "प्रधानमंत्री आवास योजना", r"प्रधानमंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"PM Awas": "प्रधानमंत्री आवास योजना", r"आयुष्मान भारत": "आयुष्मान भारत",
    r"\bAyushman\b": "आयुष्मान भारत", r"उज्ज्वला योजना": "प्रधानमंत्री उज्ज्वला योजना",
    r"स्वच्छ भारत": "स्वच्छ भारत मिशन", r"जन धन": "प्रधानमंत्री जन धन योजना",
    r"\bGST\b": "GST",
}

# -------------------------
# 2. Locations (Dictionary)
# -------------------------
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
    "कोरबा": {"canonical": "कोरबा", "hierarchy": ["छत्तीसगढ़", "कोरबा जिला"]},
    "Korba": {"canonical": "कोरबा", "hierarchy": ["छत्तीसगढ़", "कोरबा जिला"]},
    "रतनपुर": {"canonical": "रतनपुर", "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "दुर्ग": {"canonical": "दुर्ग", "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "Durg": {"canonical": "दुर्ग", "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "भिलाई": {"canonical": "भिलाई", "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "Bhilai": {"canonical": "भिलाई", "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "अंबिकापुर": {"canonical": "अंबिकापुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "Ambikapur": {"canonical": "अंबिकापुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "सुरजपुर": {"canonical": "सुरजपुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर जिला"]},
    "जगदलपुर": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "Jagdalpur": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "कोंडागाँव": {"canonical": "कोंडागाँव", "hierarchy": ["छत्तीसगढ़", "कोंडागाँव जिला"]},
    "नारायणपुर": {"canonical": "नारायणपुर", "hierarchy": ["छत्तीसगढ़", "नारायणपुर जिला"]},
    "जांजगीर": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "Janjgir": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "चंपा": {"canonical": "चंपा", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपाजिला"]},
    "राजनांदगाँव": {"canonical": "राजनांदगाँव", "hierarchy": ["छत्तीसगढ़", "राजनांदगाँव जिला"]},
    "महासमुंद": {"canonical": "महासमुंद", "hierarchy": ["छत्तीसगढ़", "महासमुंद जिला"]},
    "धमतरी": {"canonical": "धमतरी", "hierarchy": ["छत्तीसगढ़", "धमतरी जिला"]},
    "बालोद": {"canonical": "बालोद", "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "गरियाबंद": {"canonical": "गरियाबंद", "hierarchy": ["छत्तीसगढ़", "गरियाबंद जिला"]},
    "बीजापुर": {"canonical": "बीजापुर", "hierarchy": ["छत्तीसगढ़", "बीजापुर जिला"]},
    "दंतेवाड़ा": {"canonical": "दंतेवाड़ा", "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ा जिला"]},
    "सुकमा": {"canonical": "सुकमा", "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
    # V5.2 Additions
    "बलौदाबाजार": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजार जिला"]},
    "भाटापारा": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजार जिला"]},
    "कवर्धा": {"canonical": "कवर्धा", "hierarchy": ["छत्तीसगढ़", "कबीरधाम जिला"]},
    "कांकेर": {"canonical": "कांकेर", "hierarchy": ["छत्तीसगढ़", "कांकेर जिला"]},
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

# -------------------------
# 3. Feature Extractors
# -------------------------

def extract_schemes(text: str) -> Tuple[List[str], float]:
    schemes = set()
    for pattern, canonical in SCHEME_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE): schemes.add(canonical)
    return sorted(schemes), 0.0  # Confidence handled in main logic

def extract_inline_location_candidates(text: str) -> List[str]:
    candidates: List[str] = []
    # V7 Enhanced Patterns: Added Tahsil, Thana, Block, Chowki
    patterns = [
        r"([अ-हक़-य़A-Za-z]+)\s+जिला", r"([अ-हक़-य़A-Za-z]+)\s+विधानसभा", 
        r"([अ-हक़-य़A-Za-z]+)\s+नगर निगम", r"([अ-हक़-य़A-Za-z]+)\s+तहसील",
        r"([अ-हक़-य़A-Za-z]+)\s+थाना", r"([अ-हक़-य़A-Za-z]+)\s+विकासखंड",
        r"([अ-हक़-य़A-Za-z]+)\s+चौकी"
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            if len(m.group(1).strip()) >= 2: candidates.append(m.group(1).strip())
    return candidates

def normalize_location(text: str, old_location: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    candidates = []
    if old_location and old_location.get("canonical"): candidates.append(old_location["canonical"])
    
    for key in CANONICAL_LOCATIONS.keys():
        if key in text or key.lower() in text.lower(): candidates.append(key)
    
    candidates.extend(extract_inline_location_candidates(text))
    
    if not candidates: return None, 0.0
    
    best_raw = Counter(candidates).most_common(1)[0][0]
    loc_info = CANONICAL_LOCATIONS.get(best_raw)
    
    if not loc_info:
        # Fallback for detected but unknown locations (e.g. extracted from inline)
        return {"canonical": best_raw, "hierarchy_path": ["छत्तीसगढ़"], "visit_count": 1}, 0.55
        
    return {
        "district": loc_info.get("hierarchy", [""])[-1].replace("जिला", ""),
        "canonical": loc_info["canonical"],
        "hierarchy_path": loc_info.get("hierarchy", []),
        "visit_count": 1,
        "canonical_key": f"CG_{loc_info['canonical']}"
    }, 0.88

# -------------------------
# 4. Rescue Detectors (V7 Refined)
# -------------------------

def _looks_like_sports_tweet(text_l: str) -> bool:
    # V7 Change: Removed "जीत/विजय" standalone to prevent Election false positives
    # Must be specific to sports context
    SPORTS_SPECIFIC = ["क्रिकेट", "टीम इंडिया", "world cup", "t20", "ipl", "odi", "bcci", "रणजी"]
    if any(kw in text_l for kw in SPORTS_SPECIFIC): return True
    
    # "Match" + Context
    if "मैच" in text_l and any(kw in text_l for kw in ["जीत", "हार", "विकेट", "रन", "won", "lost"]): return True
    return False

def _looks_like_sports_achievement(text_l: str) -> bool:
    return any(kw in text_l for kw in ["स्वर्ण पदक", "रजत पदक", "कांस्य पदक", "medal", "gold medal", "championship"])

def _looks_like_security_context(text_l: str) -> bool:
    return any(kw in text_l for kw in ["माओवादी", "माओवाद", "नक्सल", "आतंक", "उग्रवाद", "शहीद", "jawan", "encounter"])

def _looks_like_administrative_update(text_l: str) -> bool:
    # V7: Added "Progress", "Status" for stronger detection
    return any(kw in text_l for kw in ["बैठक", "समीक्षा", "कलेक्टर", "निर्देश", "अधिकारी", "progress", "status", "निरीक्षण", "inspection"])

def _looks_like_scheme_implementation(text_l: str, schemes: List) -> bool:
    return bool(schemes) or any(kw in text_l for kw in ["लाभार्थी", "वितरण", "खाता", "subsidy", "dbt", "installments"])

def _looks_like_election_politics(text_l: str) -> bool:
    return any(kw in text_l for kw in ["चुनाव", "मतदान", "वोट", "प्रचार", "कैंपेन", "प्रत्याशी", "nomination"])

def _looks_like_industrial_development(text_l: str) -> bool:
    return any(kw in text_l for kw in ["उद्योग", "निवेश", "फैक्ट्री", "रोजगार", "infotech", "industrial", "mou"])

def _looks_like_infrastructure_work(text_l: str) -> bool:
    return any(kw in text_l for kw in ["सड़क", "पुल", "भवन", "निर्माण", "construction", "bridge", "highway"])

def _looks_like_relief_humanitarian(text_l: str) -> bool:
    return any(kw in text_l for kw in ["राहत", "आपदा", "बाढ़", "मुआवजा", "क्षतिपूर्ति", "हादसा", "दुर्घटना"])

def _looks_like_general_political(text_l: str) -> bool:
    return any(kw in text_l for kw in ["डबल इंजन", "कांग्रेस", "भाजपा", "विपक्ष", "तुष्टिकरण", "भ्रष्टाचार", "आरोप"])

def _looks_like_policy_statement(text_l: str) -> bool:
    return any(kw in text_l for kw in ["विकसित भारत", "मोदी की गारंटी", "सबका साथ", "संकल्प"])

def _looks_like_cultural_religious(text_l: str) -> bool:
    return any(kw in text_l for kw in ["मंदिर", "पूजा", "दर्शन", "जयंती", "महोत्सव", "पर्व", "arti"])

def _looks_like_congratulatory_general(text_l: str) -> bool:
    return any(kw in text_l for kw in ["बधाई", "शुभकामना", "best wishes"])

# -------------------------
# 5. Rescue Orchestrator (V7 Priority Logic)
# -------------------------

def rescue_other_events_v7(text: str, base_pd: Dict[str, Any]) -> Dict[str, Any]:
    text_l = text.lower()
    original_event = base_pd.get("event_type")
    schemes = base_pd.get("schemes_mentioned") or []
    
    pd_extra = {
        "event_type": original_event,
        "content_mode": None,
        "is_other_original": (original_event == "अन्य"),
        "is_rescued_other": False,
        "rescue_tag": None,
        "rescue_confidence_bonus": 0.0,
    }

    # --- Priority 1: High Specificity ---
    
    if _looks_like_sports_tweet(text_l) or _looks_like_sports_achievement(text_l):
        pd_extra.update({"event_type": "खेल / गौरव", "content_mode": "खेल / उपलब्धि पर प्रतिक्रिया"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "sports_v7", "rescue_confidence_bonus": 0.18})
        return pd_extra

    if _looks_like_security_context(text_l):
        pd_extra.update({"event_type": "आंतरिक सुरक्षा / पुलिस", "content_mode": "नीति / वक्तव्य"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "security_v7", "rescue_confidence_bonus": 0.20})
        return pd_extra

    # --- Priority 2: Governance (Re-Ordered for V7) ---
    
    # V7 Check: Administrative Review checks FIRST to prevent "Reviewing Scheme" -> "Scheme Launch" error
    if _looks_like_administrative_update(text_l):
        pd_extra.update({"event_type": "प्रशासनिक समीक्षा बैठक", "content_mode": "नीति / वक्तव्य"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "admin_v7", "rescue_confidence_bonus": 0.15})
        return pd_extra

    if _looks_like_election_politics(text_l):
        pd_extra.update({"event_type": "चुनाव प्रचार", "content_mode": "मैदान-स्तर कार्यक्रम"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "election_v7", "rescue_confidence_bonus": 0.17})
        return pd_extra
        
    # --- Priority 3: Development & Schemes ---

    if _looks_like_industrial_development(text_l) or _looks_like_infrastructure_work(text_l):
        pd_extra.update({"event_type": "उद्घाटन", "content_mode": "मैदान-स्तर कार्यक्रम"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "infra_dev", "rescue_confidence_bonus": 0.16})
        return pd_extra

    if _looks_like_scheme_implementation(text_l, schemes) or _looks_like_relief_humanitarian(text_l):
        # Note: Relief is often a scheme/distribution activity
        pd_extra.update({"event_type": "योजना घोषणा", "content_mode": "मैदान-स्तर कार्यक्रम"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "scheme_v7", "rescue_confidence_bonus": 0.15})
        return pd_extra

    # --- Priority 4: Political / Social ---

    if _looks_like_general_political(text_l) or _looks_like_policy_statement(text_l):
        pd_extra.update({"event_type": "राजनीतिक वक्तव्य", "content_mode": "नीति / वक्तव्य"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "political_v7", "rescue_confidence_bonus": 0.15})
        return pd_extra

    if _looks_like_cultural_religious(text_l):
        pd_extra.update({"event_type": "धार्मिक / सांस्कृतिक कार्यक्रम", "content_mode": "सामान्य शुभकामनाएँ / पर्व"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "cultural_v7", "rescue_confidence_bonus": 0.14})
        return pd_extra

    if _looks_like_congratulatory_general(text_l):
        pd_extra.update({"event_type": "शुभकामना / बधाई", "content_mode": "सामान्य शुभकामनाएँ / पर्व"})
        if original_event == "अन्य": pd_extra.update({"is_rescued_other": True, "rescue_tag": "greetings_v7", "rescue_confidence_bonus": 0.10})
        return pd_extra

    # Fallback
    pd_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
    return pd_extra

# -------------------------
# 6. Confidence & Main Loop
# -------------------------

def compute_confidence_v7(base_conf: float, pd_extra: Dict[str, Any], base_pd: Dict[str, Any], text_len: int) -> float:
    final_conf = base_conf + pd_extra.get("rescue_confidence_bonus", 0.0)
    event_type = pd_extra.get("event_type") or base_pd.get("event_type")
    has_location = bool(base_pd.get("location") and base_pd["location"].get("canonical"))
    
    # V7 Validation: Only boost if tweet is substantial (>20 chars) to avoid short-text ambiguity
    is_substantial = text_len > 20
    
    # High Precision Boost (Conditional)
    HIGH_PRECISION = ["शोक संदेश", "जन्मदिन शुभकामना", "आंतरिक सुरक्षा / पुलिस", "खेल / गौरव", "आपदा / दुर्घटना"]
    if event_type in HIGH_PRECISION and is_substantial:
        if pd_extra.get("is_rescued_other") or base_pd["confidence"] > 0.7:
            final_conf = max(final_conf, 0.92)
    
    # Triangulation
    if has_location and event_type != "अन्य": final_conf += 0.08
    
    return round(min(final_conf, 0.99), 3)

def parse_tweet_v7(record: Dict[str, Any]) -> Dict[str, Any]:
    text = record.get("raw_text") or record.get("text") or ""
    old_pd = record.get("parsed_data_v6") or record.get("parsed_data_v5") or {}
    
    schemes, _ = extract_schemes(text)
    loc_obj, _ = normalize_location(text, old_pd.get("location"))
    
    # Base Detection
    text_l = text.lower()
    base_event = "अन्य"
    base_conf = 0.4
    for keywords, label in EVENT_KEYWORD_CLUSTERS:
        if any(k in text_l for k in keywords):
            base_event = label
            base_conf = 0.85
            break
            
    base_pd = {"event_type": base_event, "location": loc_obj, "schemes_mentioned": schemes, "confidence": base_conf}
    
    # Rescue
    pd_extra = rescue_other_events_v7(text, base_pd)
    final_conf = compute_confidence_v7(base_conf, pd_extra, base_pd, len(text))
    
    parsed_v7 = {**base_pd, **pd_extra, "confidence": final_conf}
    parsed_v7["review_status"] = "auto_approved" if final_conf >= 0.9 else "pending"
    
    return {**record, "parsed_data_v7": parsed_v7}

def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("parsed_tweets_v6.jsonl")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("parsed_tweets_v7.jsonl")
    
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if line.strip(): fout.write(json.dumps(parse_tweet_v7(json.loads(line)), ensure_ascii=False) + "\n")
    print(f"✅ V7 Parsing Complete. Output: {output_path}")

if __name__ == "__main__":
    main()
