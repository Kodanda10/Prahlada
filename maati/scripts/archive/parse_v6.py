#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Dhruv – Parsing Logic V6.0 (High-Confidence, Expanded Taxonomy)

V6.0 Updates:
- ✅ New Categories: Internal Security, Sports/Pride, Political Statement, Disaster/Accident.
- ✅ Signal Multiplier: Confidence boosted >0.90 for high-precision matches.
- ✅ Triangulation Bonus: (Event + Location + Person) = Confidence >0.95.
- ✅ Refined Rescue: Maps vague tweets to specific new categories.

Taxonomy (19 categories):
- Added: आंतरिक सुरक्षा / पुलिस, खेल / गौरव, राजनीतिक वक्तव्य, आपदा / दुर्घटना

Usage:
  python3 parse_v6.py input.jsonl output.jsonl
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

# -------------------------
# Paths
# -------------------------

DEFAULT_INPUT = Path(__file__).parent.parent / "data" / "parsed_tweets_v5.jsonl"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "data" / "parsed_tweets_v6.jsonl"

# -------------------------
# Taxonomies / Enums
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
    # --- NEW V6 CATEGORIES ---
    "आंतरिक सुरक्षा / पुलिस",
    "खेल / गौरव",
    "राजनीतिक वक्तव्य",
    "आपदा / दुर्घटना",
    # -------------------------
    "अन्य",
]

CONTENT_MODES = [
    "मैदान-स्तर कार्यक्रम",
    "नीति / वक्तव्य",
    "डिजिटल / सोशल-मीडिया पोस्ट",
    "खेल / उपलब्धि पर प्रतिक्रिया",
    "सामान्य शुभकामनाएँ / पर्व",
]

# keyword clusters → Hindi label (base event detection)
EVENT_KEYWORD_CLUSTERS: List[Tuple[List[str], str]] = [
    # 1. V6 NEW: Internal Security / Police
    (["माओवाद", "नक्सल", "नक्सली", "लाल आतंक", "सुरक्षा बल", "जवानों", "शहीद", 
      "आत्मसमर्पण", "बस्तर ओलंपिक", "ऑपरेशन", "पुलिस स्मृति", "police", "jawan"], "आंतरिक सुरक्षा / पुलिस"),

    # 2. V6 NEW: Sports / Pride
    (["मैच जीत", "टीम इंडिया", "क्रिकेट", "पदक", "स्वर्ण पदक", "खिलाड़ी", 
      "ओलंपिक", "खेल", "tournament", "चैंपियंस ट्रॉफी", "गर्व का क्षण", "medal", "won", "winner"], "खेल / गौरव"),

    # 3. V6 NEW: Disaster / Accident
    (["हादसा", "दुर्घटना", "रेल हादसा", "बस हादसा", "आगजनी", "बाढ़", "प्राकृतिक आपदा", "accident", "tragedy"], "आपदा / दुर्घटना"),

    # 4. V6 NEW: Political Statement
    (["डबल इंजन", "कांग्रेस सरकार", "भ्रष्टाचार", "तुष्टिकरण", "आपातकाल", 
      "विकसित भारत", "मोदी की गारंटी", "विपक्ष", "आरोप", "statement", "political"], "राजनीतिक वक्तव्य"),

    # --- Existing Categories ---
    (["बैठक", "मुलाकात", "भेंट", "बैठक ली", "बैठक में", "बैठक का", "अध्यक्षता की", "सत्र", "सदन की कार्यवाही"], "बैठक"),
    (["जनसम्पर्क", "जन संपर्क", "जनसंपर्क", "जनदर्शन", "जन-दर्शन", "जन सुनवाई", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन"),
    (["समीक्षा बैठक", "समीक्षा की", "समीक्षा की गई", "अधिकारियों के साथ", "विभागीय बैठक", "कलेक्टर", "कलेक्टरेट", "समीक्षा कार्य"], "प्रशासनिक समीक्षा बैठक"),
    (["निरीक्षण", "निरीक्षण किया", "निरीक्षण हेतु", "inspection"], "निरीक्षण"),
    (["रैली", "जनसभा", "public rally", "road show", "रोड शो"], "रैली"),
    (["चुनावी", "मतदाता", "मतदान", "चुनाव प्रचार", "poll campaign"], "चुनाव प्रचार"),
    (["उद्घाटन", "लोकार्पण", "inauguration", "inaugurated", "शिलान्यास"], "उद्घाटन"),
    (["घोषणा", "नई योजना", "योजना की जानकारी", "योजना का लाभ"], "योजना घोषणा"),
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "गुरु नानक", "मस्जिद", "धार्मिक", "सांस्कृतिक कार्यक्रम", "जयंती"], "धार्मिक / सांस्कृतिक कार्यक्रम"),
    (["सम्मान", "सम्मानित", "शॉल", "श्रीफल", "समारोह", "felicitation"], "सम्मान / Felicitation"),
    (["प्रेस वार्ता", "प्रेस कॉन्फ़्रेंस", "मीडिया ब्रिफिंग", "मीडिया से बातचीत"], "प्रेस कॉन्फ़्रेंस / मीडिया"),
    (["शुभकामनाएं", "शुभकामनाएँ", "बधाई", "congratulations"], "शुभकामना / बधाई"),
    (["जन्मदिन", "birthday"], "जन्मदिन शुभकामना"),
    (["श्रद्धांजलि", "शोक संदेश", "दिवंगत", "अंतिम यात्रा", "पुण्यतिथि", "condolence"], "शोक संदेश"),
]

SCHEME_PATTERNS = {
    r"\bPMAY\b": "प्रधानमंत्री आवास योजना",
    r"प्रधानमंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"प्रधान मंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"PM Awas": "प्रधानमंत्री आवास योजना",
    r"आवास योजना": "प्रधानमंत्री आवास योजना",
    r"आयुष्मान भारत": "आयुष्मान भारत",
    r"\bAyushman\b": "आयुष्मान भारत",
    r"Ayushman Bharat": "आयुष्मान भारत",
    r"उज्ज्वला योजना": "प्रधानमंत्री उज्ज्वला योजना",
    r"\bUjjwala\b": "प्रधानमंत्री उज्ज्वला योजना",
    r"स्वच्छ भारत": "स्वच्छ भारत मिशन",
    r"\bSBM\b": "स्वच्छ भारत मिशन",
    r"जन धन": "प्रधानमंत्री जन धन योजना",
    r"\bJan Dhan\b": "प्रधानमंत्री जन धन योजना",
    r"\bGST\b": "GST",
}

TARGET_GROUP_KEYWORDS = {
    "महिला": "महिला",
    "महिलाओं": "महिला",
    "नारी": "महिला",
    "युवा": "युवा",
    "युवाओं": "युवा",
    "किसान": "किसान",
    "किसानों": "किसान",
    "खेती": "किसान",
    "छात्र": "छात्र",
    "विद्यार्थी": "छात्र",
    "स्टूडेंट": "छात्र",
    "मजदूर": "मज़दूर",
    "मजदूरों": "मज़दूर",
    "व्यापारी": "व्यापारी",
    "व्यापारियों": "व्यापारी",
    "गरीब": "गरीब",
    "आर्थिक रूप से कमजोर": "गरीब",
    "बुजुर्ग": "बुज़ुर्ग",
    "वरिष्ठ नागरिक": "बुज़ुर्ग",
    "सरकारी कर्मचारी": "सरकारी कर्मचारी",
    "शासकीय कर्मचारी": "सरकारी कर्मचारी",
}

COMMUNITY_KEYWORDS = {
    "साहू": "साहू",
    "गोंड": "गोंड",
    "आदिवासी": "आदिवासी",
    "गोंडवाना": "गोंड",
    "वैश्य": "वैश्य",
    "ब्राह्मण": "ब्राह्मण",
    "कुर्मी": "कुर्मी",
    "तेली": "तेली",
    "ठाकुर": "ठाकुर",
    "कुशवाहा": "कुशवाहा",
    "दलित": "दलित",
    "अनुसूचित जाति": "अनुसूचित जाति",
    "अनुसूचित जनजाति": "अनुसूचित जनजाति",
    "ओबीसी": "ओबीसी",
    "मुस्लिम": "मुस्लिम",
    "इस्लाम": "मुस्लिम",
    "ईसाई": "ईसाई",
    "क्रिश्चियन": "ईसाई",
    "सिख": "सिख",
    "जैन": "जैन",
    "बौद्ध": "बौद्ध",
}

ORG_KEYWORDS = {
    "भाजपा": "भारतीय जनता पार्टी",
    "BJP": "भारतीय जनता पार्टी",
    "भारतीय जनता पार्टी": "भारतीय जनता पार्टी",
    "कांग्रेस": "भारतीय राष्ट्रीय कांग्रेस",
    "INC": "भारतीय राष्ट्रीय कांग्रेस",
    "Indian National Congress": "भारतीय राष्ट्रीय कांग्रेस",
    "RSS": "राष्ट्रीय स्वयंसेवक संघ",
    "आरएसएस": "राष्ट्रीय स्वयंसेवक संघ",
    "सरकार": "सरकार",
    "केंद्र सरकार": "केंद्र सरकार",
    "राज्य सरकार": "राज्य सरकार",
    "भारतीय सेना": "भारतीय सेना",
    "Indian Army": "भारतीय सेना",
}

# Extended canonical locations
CANONICAL_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "रायगढ़": {"canonical": "रायगढ़", "aliases": ["रायगढ़", "रायगढ़", "Raigarh", "Raigarhh"], "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "Raigarh": {"canonical": "रायगढ़", "aliases": ["रायगढ़", "रायगढ़", "Raigarh", "Raigarhh"], "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "खरसिया": {"canonical": "खरसिया", "aliases": ["खरसिया", "Kharsia", "Kharsiya"], "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "Kharsia": {"canonical": "खरसिया", "aliases": ["खरसिया", "Kharsia", "Kharsiya"], "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "रायपुर": {"canonical": "रायपुर", "aliases": ["रायपुर", "Raipur"], "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "Raipur": {"canonical": "रायपुर", "aliases": ["रायपुर", "Raipur"], "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "नया रायपुर": {"canonical": "नया रायपुर", "aliases": ["नया रायपुर", "New Raipur", "Naya Raipur"], "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "New Raipur": {"canonical": "नया रायपुर", "aliases": ["नया रायपुर", "New Raipur", "Naya Raipur"], "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "बिलासपुर": {"canonical": "बिलासपुर", "aliases": ["बिलासपुर", "Bilaspur"], "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "Bilaspur": {"canonical": "बिलासपुर", "aliases": ["बिलासपुर", "Bilaspur"], "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "कोरबा": {"canonical": "कोरबा", "aliases": ["कोरबा", "Korba"], "hierarchy": ["छत्तीसगढ़", "कोरबा जिला"]},
    "Korba": {"canonical": "कोरबा", "aliases": ["कोरबा", "Korba"], "hierarchy": ["छत्तीसगढ़", "कोरबा जिला"]},
    "रतनपुर": {"canonical": "रतनपुर", "aliases": ["रतनपुर", "Ratanpur"], "hierarchy": ["छत्तीसगढ़", "बिलासपुर जिला"]},
    "दुर्ग": {"canonical": "दुर्ग", "aliases": ["दुर्ग", "Durg"], "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "Durg": {"canonical": "दुर्ग", "aliases": ["दुर्ग", "Durg"], "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "भिलाई": {"canonical": "भिलाई", "aliases": ["भिलाई", "Bhilai"], "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "Bhilai": {"canonical": "भिलाई", "aliases": ["भिलाई", "Bhilai"], "hierarchy": ["छत्तीसगढ़", "दुर्ग जिला"]},
    "अंबिकापुर": {"canonical": "अंबिकापुर", "aliases": ["अंबिकापुर", "Ambikapur"], "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "Ambikapur": {"canonical": "अंबिकापुर", "aliases": ["अंबिकापुर", "Ambikapur"], "hierarchy": ["छत्तीसगढ़", "सुरजपुर/सरगुजा क्षेत्र"]},
    "सुरजपुर": {"canonical": "सुरजपुर", "aliases": ["सुरजपुर", "Surajpur"], "hierarchy": ["छत्तीसगढ़", "सुरजपुर जिला"]},
    "Surajpur": {"canonical": "सुरजपुर", "aliases": ["सुरजपुर", "Surajpur"], "hierarchy": ["छत्तीसगढ़", "सुरजपुर जिला"]},
    "जगदलपुर": {"canonical": "जगदलपुर", "aliases": ["जगदलपुर", "Jagdalpur"], "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "Jagdalpur": {"canonical": "जगदलपुर", "aliases": ["जगदलपुर", "Jagdalpur"], "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "कोंडागाँव": {"canonical": "कोंडागाँव", "aliases": ["कोंडागाँव", "Kondagaon"], "hierarchy": ["छत्तीसगढ़", "कोंडागाँव जिला"]},
    "Kondagaon": {"canonical": "कोंडागाँव", "aliases": ["कोंडागाँव", "Kondagaon"], "hierarchy": ["छत्तीसगढ़", "कोंडागाँव जिला"]},
    "नारायणपुर": {"canonical": "नारायणपुर", "aliases": ["नारायणपुर", "Narayanpur"], "hierarchy": ["छत्तीसगढ़", "नारायणपुर जिला"]},
    "Narayanpur": {"canonical": "नारायणपुर", "aliases": ["नारायणपुर", "Narayanpur"], "hierarchy": ["छत्तीसगढ़", "नारायणपुर जिला"]},
    "जांजगीर": {"canonical": "जांजगीर", "aliases": ["जांजगीर", "Janjgir"], "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "Janjgir": {"canonical": "जांजगीर", "aliases": ["जांजगीर", "Janjgir"], "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "चंपा": {"canonical": "चंपा", "aliases": ["चंपा", "Champa"], "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "राजनांदगाँव": {"canonical": "राजनांदगाँव", "aliases": ["राजनांदगाँव", "Rajandgaon"], "hierarchy": ["छत्तीसगढ़", "राजनांदगाँव जिला"]},
    "Rajandgaon": {"canonical": "राजनांदगाँव", "aliases": ["राजनांदगाँव", "Rajandgaon"], "hierarchy": ["छत्तीसगढ़", "राजनांदगाँव जिला"]},
    "महासमुंद": {"canonical": "महासमुंद", "aliases": ["महासमुंद", "Mahasamund"], "hierarchy": ["छत्तीसगढ़", "महासमुंद जिला"]},
    "Mahasamund": {"canonical": "महासमुंद", "aliases": ["महासमुंद", "Mahasamund"], "hierarchy": ["छत्तीसगढ़", "महासमुंद जिला"]},
    "धमतरी": {"canonical": "धमतरी", "aliases": ["धमतरी", "Dhamtari"], "hierarchy": ["छत्तीसगढ़", "धमतरी जिला"]},
    "Dhamtari": {"canonical": "धमतरी", "aliases": ["धमतरी", "Dhamtari"], "hierarchy": ["छत्तीसगढ़", "धमतरी जिला"]},
    "बालोद": {"canonical": "बालोद", "aliases": ["बालोद", "Balod"], "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "Balod": {"canonical": "बालोद", "aliases": ["बालोद", "Balod"], "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "गरियाबंद": {"canonical": "गरियाबंद", "aliases": ["गरियाबंद", "Gariaband"], "hierarchy": ["छत्तीसगढ़", "गरियाबंद जिला"]},
    "Gariaband": {"canonical": "गरियाबंद", "aliases": ["गरियाबंद", "Gariaband"], "hierarchy": ["छत्तीसगढ़", "गरियाबंद जिला"]},
    "बीजापुर": {"canonical": "बीजापुर", "aliases": ["बीजापुर", "Bijapur"], "hierarchy": ["छत्तीसगढ़", "बीजापुर जिला"]},
    "Bijapur": {"canonical": "बीजापुर", "aliases": ["बीजापुर", "Bijapur"], "hierarchy": ["छत्तीसगढ़", "बीजापुर जिला"]},
    "दंतेवाड़ा": {"canonical": "दंतेवाड़ा", "aliases": ["दंतेवाड़ा", "Dantewada"], "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ा जिला"]},
    "Dantewada": {"canonical": "दंतेवाड़ा", "aliases": ["दंतेवाड़ा", "Dantewada"], "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ा जिला"]},
    "सुकमा": {"canonical": "सुकमा", "aliases": ["सुकमा", "Sukma"], "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
    "Sukma": {"canonical": "सुकमा", "aliases": ["सुकमा", "Sukma"], "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
}

# -------------------------
# Feature extractors
# -------------------------

def normalize_event_type_base(raw_event_type_hi: Optional[str], text: str, schemes: List[str]) -> Tuple[str, float]:
    text_lower = text.lower()
    candidate: Optional[str] = None
    best_conf = 0.0

    # 1) keyword clusters
    for keywords, label in EVENT_KEYWORD_CLUSTERS:
        for kw in keywords:
            if kw.lower() in text_lower:
                base_conf = 0.80
                # Specific high-confidence categories
                if label in ("प्रशासनिक समीक्षा बैठक", "जनसम्पर्क / जनदर्शन", "आंतरिक सुरक्षा / पुलिस", "खेल / गौरव", "आपदा / दुर्घटना"):
                    base_conf = 0.88
                
                if base_conf > best_conf:
                    best_conf = base_conf
                    candidate = label
                break

    # 2) Use old hint if valid
    if raw_event_type_hi and raw_event_type_hi in ALLOWED_EVENT_TYPES_HI and raw_event_type_hi != "अन्य":
        if candidate is None:
            candidate = raw_event_type_hi
            best_conf = max(best_conf, 0.75)
        elif raw_event_type_hi == candidate:
            best_conf = max(best_conf, 0.93)

    # 3) schemes + no candidate -> Yojna
    if (candidate is None or candidate == "अन्य") and schemes:
        candidate = "योजना घोषणा"
        best_conf = max(best_conf, 0.8)

    # 4) fallback
    if candidate is None:
        candidate = "अन्य"
        best_conf = max(best_conf, 0.45)

    return candidate, best_conf

def extract_schemes(text: str) -> Tuple[List[str], float]:
    schemes = set()
    for pattern, canonical in SCHEME_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            schemes.add(canonical)
    if not schemes:
        return [], 0.0
    conf = min(0.96, 0.65 + 0.08 * len(schemes))
    return sorted(schemes), conf

def extract_target_groups(text: str) -> Tuple[List[str], float]:
    groups = set()
    for kw, canonical in TARGET_GROUP_KEYWORDS.items():
        if kw in text:
            groups.add(canonical)
    if not groups:
        return [], 0.0
    conf = min(0.9, 0.65 + 0.05 * len(groups))
    return sorted(groups), conf

def extract_communities(text: str) -> Tuple[List[str], float]:
    communities = set()
    for kw, canonical in COMMUNITY_KEYWORDS.items():
        if kw in text:
            communities.add(canonical)
    if not communities:
        return [], 0.0
    conf = min(0.9, 0.65 + 0.05 * len(communities))
    return sorted(communities), conf

def extract_orgs(text: str) -> Tuple[List[str], float]:
    orgs = set()
    lowered = text.lower()
    for kw, canonical in ORG_KEYWORDS.items():
        if kw.lower() in lowered:
            orgs.add(canonical)
    if not orgs:
        return [], 0.0
    conf = min(0.9, 0.65 + 0.05 * len(orgs))
    return sorted(orgs), conf

def extract_hashtags(text: str) -> List[str]:
    return re.findall(r"#(\w+)", text)

def make_word_buckets(text: str) -> Tuple[List[str], float]:
    buckets: List[str] = []
    for tag in extract_hashtags(text):
        t = tag.lower()
        if "pmawas" in t or "pmay" in t:
            buckets.append("PM आवास योजना")
        elif "ayushman" in t:
            buckets.append("आयुष्मान भारत")
        elif "gst" in t:
            buckets.append("GST")
        elif "kisan" in t or "farmer" in t:
            buckets.append("कृषि / किसान")
        elif "youth" in t or "yuva" in t:
            buckets.append("युवा")
        elif "mahila" in t or "women" in t:
            buckets.append("महिला सशक्तिकरण")

    topic_map = [
        (["किसान", "फसल", "खेती", "कृषि"], "कृषि / किसान"),
        (["महिला", "महिलाओं", "नारी"], "महिला सशक्तिकरण"),
        (["शिक्षा", "स्कूल", "कॉलेज", "विद्यालय"], "शिक्षा"),
        (["स्वास्थ्य", "अस्पताल", "चिकित्सा", "स्वास्थ्य शिविर"], "स्वास्थ्य"),
        (["बिजली", "रोशनी", "विद्युत"], "बिजली"),
        (["सड़क", "मार्ग", "highway", "पुल"], "सड़क / इन्फ्रा"),
        (["नौकरी", "रोज़गार", "रोजगार"], "रोज़गार"),
        (["युवा", "युवा सम्मेलन"], "युवा"),
        (["उद्यमी", "व्यापार", "उद्योग"], "उद्योग / व्यापार"),
    ]
    lower = text.lower()
    for words, bucket in topic_map:
        if any(w.lower() in lower for w in words):
            buckets.append(bucket)

    buckets = sorted(set(buckets))
    if not buckets:
        return [], 0.0
    conf = min(0.92, 0.55 + 0.05 * len(buckets))
    return buckets, conf

# -------------------------
# Location helpers
# -------------------------

def extract_inline_location_candidates(text: str) -> List[str]:
    candidates: List[str] = []
    patterns = [
        r"([अ-हक़-य़A-Za-z]+)\s+जिला", r"([अ-हक़-य़A-Za-z]+)\s+विधानसभा",
        r"([अ-हक़-य़A-Za-z]+)\s+ब्लॉक", r"([अ-हक़-य़A-Za-z]+)\s+नगर निगम",
        r"([अ-हक़-य़A-Za-z]+)\s+नगर पालिका", r"([अ-हक़-य़A-Za-z]+)\s+नगर पंचायत",
        r"([अ-हक़-य़A-Za-z]+)\s+ग्राम पंचायत", r"([अ-हक़-य़A-Za-z]+)\s+ग्राम",
        r"([अ-हक़-य़A-Za-z]+)\s+गाँव",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            name = m.group(1).strip()
            if len(name) >= 2:
                candidates.append(name)
    return candidates

def normalize_location(text: str, old_location: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    candidates: List[str] = []
    if old_location:
        can = old_location.get("canonical") or old_location.get("district")
        if can: candidates.append(str(can))
        aliases = old_location.get("aliases") or []
        for a in aliases:
            if a: candidates.append(str(a))

    for key in CANONICAL_LOCATIONS.keys():
        if key in text: candidates.append(key)

    lower = text.lower()
    for key in CANONICAL_LOCATIONS.keys():
        if key.lower() in lower: candidates.append(key)

    candidates.extend(extract_inline_location_candidates(text))

    if not candidates:
        return None, 0.0

    count = Counter(candidates)
    best_raw, _ = count.most_common(1)[0]
    loc_info = CANONICAL_LOCATIONS.get(best_raw)

    if not loc_info:
        loc_obj = {
            "district": None, "assembly": None, "block": None, "gp": None,
            "village": None, "ulb": None, "zone": None, "ward": None,
            "canonical_key": None, "canonical": best_raw, "aliases": [best_raw],
            "hierarchy_path": ["छत्तीसगढ़"], "visit_count": 1,
        }
        return loc_obj, 0.55

    canonical = loc_info["canonical"]
    aliases = sorted(set(loc_info.get("aliases", []) + [best_raw]))
    hierarchy = loc_info.get("hierarchy", [])
    district = None
    assembly = None

    for level in hierarchy:
        if "जिला" in level: district = level.replace(" जिला", "")
        if "विधानसभा" in level: assembly = level.replace(" विधानसभा", "")

    loc_obj = {
        "district": district, "assembly": assembly, "block": None, "gp": None,
        "village": None, "ulb": None, "zone": None, "ward": None,
        "canonical_key": f"CG_{canonical}", "canonical": canonical,
        "aliases": aliases, "hierarchy_path": hierarchy, "visit_count": 1,
    }
    return loc_obj, 0.88

# -------------------------
# Confidence (V6 Enhanced)
# -------------------------

def compute_confidence_base(c_event: float, c_location: float, schemes: List[str], event_type: str, location_obj: Optional[Dict[str, Any]]) -> float:
    good_event = event_type != "अन्य"
    good_loc = bool(location_obj and location_obj.get("canonical"))

    base = 0.4
    if good_event: base += 0.25
    if good_loc: base += 0.2
    if schemes: base += 0.05

    score = base * 0.7 + ((c_event + c_location) / 2) * 0.3
    return min(0.99, max(0.0, score))

def compute_confidence_v6(base_conf: float, pd6_extra: Dict[str, Any], base_pd: Dict[str, Any]) -> float:
    """
V6 Signal Multiplier: Boosts confidence based on signal triangulation.
    """
    final_conf = base_conf
    bonus = pd6_extra.get("rescue_confidence_bonus", 0.0)
    final_conf += bonus

    event_type = pd6_extra.get("event_type") or base_pd.get("event_type")
    has_location = bool(base_pd.get("location") and base_pd["location"].get("canonical"))
    has_person = len(base_pd.get("people_mentioned", [])) > 0
    content_mode = pd6_extra.get("content_mode")

    # 1. HIGH PRECISION EVENT BOOST
    # These events are rarely false positives if keywords match
    HIGH_PRECISION_EVENTS = [
        "शोक संदेश", "जन्मदिन शुभकामना", "आंतरिक सुरक्षा / पुलिस", 
        "खेल / गौरव", "आपदा / दुर्घटना"
    ]
    if event_type in HIGH_PRECISION_EVENTS:
        final_conf = max(final_conf, 0.92)

    # 2. TRIANGULATION BONUS (Event + Person + Location)
    if has_location and has_person and event_type != "अन्य":
        final_conf += 0.15

    # 3. DUAL SIGNAL BONUS
    elif (has_location or has_person) and event_type != "अन्य":
        final_conf += 0.08

    # 4. SPECIFIC CONTEXT BOOSTS
    if event_type == "बैठक" and content_mode == "मैदान-स्तर कार्यक्रम":
        final_conf += 0.05

    # 5. Rescue Confidence Integrity
    if pd6_extra.get("is_rescued_other"):
        # If rescued, ensure it meets a decent threshold
        final_conf = max(final_conf, 0.85)

    return round(min(final_conf, 0.99), 3)

def decide_review_status(conf: float) -> Tuple[str, bool]:
    if conf >= 0.9: return "auto_approved", False
    if conf >= 0.75: return "pending", False
    return "pending", True

# -------------------------
# "अन्य" Rescue – V6 Logic
# -------------------------

def _looks_like_sports_tweet(text_l: str) -> bool:
    SPORTS_KW = ["मैच", "जीत", "विजय", "टीम इंडिया", "world cup", "टी20", "ipl", "medal", "पदक"]
    return any(kw in text_l for kw in SPORTS_KW)

def _looks_like_policy_statement(text_l: str) -> bool:
    POLICY_KW = ["सबका साथ", "विकसित भारत", "प्रधानमंत्री", "गारंटी", "डबल इंजन", "कांग्रेस", "विपक्ष"]
    return any(kw in text_l for kw in POLICY_KW)

def _looks_like_security_context(text_l: str) -> bool:
    SECURITY_KW = ["माओवादी", "नक्सल", "आतंक", "शहीद", "जवान", "police", "बस्तर"]
    return any(kw in text_l for kw in SECURITY_KW)

def _looks_like_pure_greetings(text_l: str) -> bool:
    GREET_KW = ["शुभकामना", "बधाई", "मुबारक", "congratulations"]
    FESTIVAL_HINTS = ["दीपावली", "होली", "रक्षा बंधन", "स्वतंत्रता दिवस"]
    has_greet = any(kw in text_l for kw in GREET_KW) or any(kw in text_l for kw in FESTIVAL_HINTS)
    EVENT_HINTS = ["बैठक", "रैली", "उद्घाटन"]
    return has_greet and not any(e in text_l for e in EVENT_HINTS)

def _looks_like_digital_only(text_l: str, pd: Dict[str, Any]) -> bool:
    loc = pd.get("location") or {}
    DIGITAL_KW = ["online", "live", "जुड़ें", "link"]
    return (not loc.get("canonical")) and any(kw in text_l for kw in DIGITAL_KW)

def _looks_like_relief_humanitarian(text_l: str) -> bool:
    RELIEF_KW = ["सहायता", "राहत", "बाढ़", "सूखा", "मुआवजा", "क्षतिपूर्ति"]
    return any(kw in text_l for kw in RELIEF_KW)

# Other heuristics from V5 preserved
def _looks_like_scheme_impl(text_l: str, schemes: List[str]) -> bool:
    return bool(schemes) and ("लाभार्थी" in text_l or "वितरण" in text_l)

def rescue_other_events_v6(text: str, base_pd: Dict[str, Any]) -> Dict[str, Any]:
    """
V6 Rescue Logic: Maps detected patterns to specific V6 categories.
    """
    text_l = text.lower()
    original_event = base_pd.get("event_type")
    schemes = base_pd.get("schemes_mentioned") or []

    pd_extra: Dict[str, Any] = {
        "event_type": original_event,
        "content_mode": None,
        "is_other_original": (original_event == "अन्य"),
        "is_rescued_other": False,
        "rescue_tag": None,
        "rescue_confidence_bonus": 0.0,
    }

    # 1. Sports -> Now maps to "खेल / गौरव"
    if _looks_like_sports_tweet(text_l):
        pd_extra["content_mode"] = "खेल / उपलब्धि पर प्रतिक्रिया"
        if original_event == "अन्य":
            pd_extra["event_type"] = "खेल / गौरव"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "sports_v6"
            pd_extra["rescue_confidence_bonus"] = 0.18
        return pd_extra

    # 2. Security -> Now maps to "आंतरिक सुरक्षा / पुलिस"
    if _looks_like_security_context(text_l):
        pd_extra["content_mode"] = "नीति / वक्तव्य"
        if original_event == "अन्य":
            pd_extra["event_type"] = "आंतरिक सुरक्षा / पुलिस"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "security_v6"
            pd_extra["rescue_confidence_bonus"] = 0.20
        return pd_extra

    # 3. Relief -> Now maps to "आपदा / दुर्घटना"
    if _looks_like_relief_humanitarian(text_l):
        pd_extra["content_mode"] = "मैदान-स्तर कार्यक्रम"
        if original_event == "अन्य":
            pd_extra["event_type"] = "आपदा / दुर्घटना"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "disaster_v6"
            pd_extra["rescue_confidence_bonus"] = 0.18
        return pd_extra

    # 4. Policy -> Now maps to "राजनीतिक वक्तव्य"
    if _looks_like_policy_statement(text_l):
        pd_extra["content_mode"] = "नीति / वक्तव्य"
        if original_event == "अन्य":
            pd_extra["event_type"] = "राजनीतिक वक्तव्य"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "political_v6"
            pd_extra["rescue_confidence_bonus"] = 0.15
        return pd_extra

    # 5. Scheme Implementation -> "योजना घोषणा"
    if _looks_like_scheme_impl(text_l, schemes):
        pd_extra["content_mode"] = "मैदान-स्तर कार्यक्रम"
        if original_event == "अन्य":
            pd_extra["event_type"] = "योजना घोषणा"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "scheme_impl"
            pd_extra["rescue_confidence_bonus"] = 0.18
        return pd_extra

    # 6. Pure Greetings -> "शुभकामना / बधाई"
    if _looks_like_pure_greetings(text_l):
        pd_extra["content_mode"] = "सामान्य शुभकामनाएँ / पर्व"
        if original_event == "अन्य":
            pd_extra["event_type"] = "शुभकामना / बधाई"
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "greetings"
            pd_extra["rescue_confidence_bonus"] = 0.10
        return pd_extra

    # 7. Digital -> "अन्य" (but classified mode)
    if _looks_like_digital_only(text_l, base_pd):
        pd_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
        if original_event == "अन्य":
            pd_extra["is_rescued_other"] = True
            pd_extra["rescue_tag"] = "digital"
            pd_extra["rescue_confidence_bonus"] = 0.05
        return pd_extra

    # Fallback
    pd_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
    return pd_extra

# -------------------------
# Parsing Driver
# -------------------------

def parse_tweet_v6(record: Dict[str, Any]) -> Dict[str, Any]:
    text = record.get("raw_text") or record.get("text") or ""
    created_at = record.get("created_at")
    old_pd = record.get("parsed_data_v5") or record.get("parsed_data_v4") or {}

    # 1. Base Parse (Extraction + Keyword Clustering)
    schemes, c_schemes = extract_schemes(text)
    word_buckets, _ = make_word_buckets(text)
    target_groups, _ = extract_target_groups(text)
    communities, _ = extract_communities(text)
    orgs, _ = extract_orgs(text)

    # Base Event Detection (includes new V6 clusters)
    event_type, c_event = normalize_event_type_base(old_pd.get("event_type"), text, schemes)
    location_obj, c_location = normalize_location(text, old_pd.get("location"))

    base_confidence = compute_confidence_base(c_event, c_location, schemes, event_type, location_obj)

    base_pd = {
        "event_type": event_type,
        "event_date": created_at[:10] if created_at else None,
        "location": location_obj,
        "people_mentioned": old_pd.get("people_mentioned", []),
        "schemes_mentioned": schemes,
        "word_buckets": word_buckets,
        "target_groups": target_groups,
        "communities": communities,
        "organizations": orgs,
        "confidence": base_confidence
    }

    # 2. Rescue / Classification Layer (V6)
    pd_extra = rescue_other_events_v6(text, base_pd)

    # 3. Final Confidence (Signal Multiplier)
    final_conf = compute_confidence_v6(base_confidence, pd_extra, base_pd)
    review_status, needs_review = decide_review_status(final_conf)

    parsed_data_v6 = {
        **base_pd,
        "event_type": pd_extra["event_type"],
        "confidence": final_conf,
        "review_status": review_status,
        "needs_review": needs_review,
        "content_mode": pd_extra["content_mode"],
        "is_rescued_other": pd_extra["is_rescued_other"],
        "rescue_tag": pd_extra["rescue_tag"]
    }

    return {
        "tweet_id": record.get("tweet_id"),
        "created_at": created_at,
        "raw_text": text,
        "parsed_data_v6": parsed_data_v6,
        "metadata_v6": {"model": "rule-engine-v6-optimised"}
    }

def reparse_file_v6(input_path: Path, output_path: Path) -> None:
    print(f"🚀 Starting V6 Parsing on {input_path}...")
    total = 0
    stats = Counter()
    
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip(): continue
            try:
                rec = json.loads(line)
            except:
                continue

            total += 1
            new_rec = parse_tweet_v6(rec)
            pd = new_rec["parsed_data_v6"]
            
            # Stats
            if pd["confidence"] >= 0.9: stats["High Conf (>=0.9)"] += 1
            elif pd["confidence"] >= 0.7: stats["Med Conf (0.7-0.9)"] += 1
            else: stats["Low Conf (<0.7)"] += 1
            
            stats[f"Event: {pd['event_type']}"] += 1
            if pd["is_rescued_other"]: stats["Rescued Tweets"] += 1
            
            fout.write(json.dumps(new_rec, ensure_ascii=False) + "\n")

    print(f"\n✅ V6 Complete. Total: {total}")
    print(f"   High Conf: {stats['High Conf (>=0.9)']}")
    print(f"   Rescued: {stats['Rescued Tweets']}")
    print("\nEvent Distribution:")
    for k, v in stats.most_common(20):
        if k.startswith("Event:"): print(f"   {k}: {v}")

if __name__ == "__main__":
    import sys
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    reparse_file_v6(inp, out)
