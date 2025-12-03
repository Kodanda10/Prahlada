#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Dhruv – OpenAI_V1 Parser
(Best-of-3 + Think-Harder Merge)

- Hindi-first taxonomy
- Best-of-3 consensus: keyword rules + old parser hint + rescue logic
- Strong focus on:
  - Reducing "अन्य" safely
  - Keeping confidence >=0.90 only for truly strong cases
  - Better location coverage (जिला, तहसील, थाना, विकासखंड, चौकी...)

Usage:
  python3 parse_OpenAI_V1.py input.jsonl output.jsonl

If no args:
  input  = ../data/parsed_tweets_v52.jsonl
  output = ../data/parsed_tweets_OpenAI_V1.jsonl
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

DEFAULT_INPUT = Path(__file__).parent.parent / "data" / "parsed_tweets_v52.jsonl"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "data" / "parsed_tweets_OpenAI_V1.jsonl"

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

# High-precision & extended keyword clusters (merged)
EVENT_KEYWORD_CLUSTERS: List[Tuple[List[str], str]] = [
    # Security
    (
        [
            "माओवाद", "माओवादी", "नक्सल", "नक्सली", "लाल आतंक", "सुरक्षा बल",
            "जवानों", "जवान", "शहीद", "आत्मसमर्पण", "encounter", "ied",
            "police", "पुलिस", "उग्रवाद", "आतंकवाद"
        ],
        "आंतरिक सुरक्षा / पुलिस",
    ),
    # Sports / Pride (no standalone जीत/विजय)
    (
        [
            "क्रिकेट", "टीम इंडिया", "world cup", "वर्ल्ड कप", "t20", "टी20",
            "ipl", "odi", "वनडे", "bcci", "रणजी", "पदक", "medal",
            "स्वर्ण पदक", "रजत पदक", "कांस्य पदक", "championship"
        ],
        "खेल / गौरव",
    ),
    # Disaster / Accident
    (
        [
            "हादसा", "दुर्घटना", "रेल हादसा", "बस हादसा", "आगजनी",
            "प्राकृतिक आपदा", "बाढ़", "tragedy", "accident", "collision",
            "जनहानि"
        ],
        "आपदा / दुर्घटना",
    ),
    # Political statement (macro)
    (
        [
            "डबल इंजन", "कांग्रेस सरकार", "भ्रष्टाचार", "तुष्टिकरण", "आपातकाल",
            "विकसित भारत", "मोदी की गारंटी", "विपक्ष", "manifesto",
            "संकल्प पत्र", "सरकार की नीतियाँ"
        ],
        "राजनीतिक वक्तव्य",
    ),
    # Classical programme types
    (["बैठक", "बैठक ली", "बैठक में", "बैठक का", "भेंट", "मुलाकात", "अध्यक्षता की"], "बैठक"),
    (["जनसम्पर्क", "जनसंपर्क", "जन संपर्क", "जनदर्शन", "जन-दर्शन", "जन सुनवाई", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन"),
    (["समीक्षा बैठक", "समीक्षा की", "समीक्षा की गई", "अधिकारियों के साथ", "विभागीय बैठक", "कलेक्टर", "कलेक्टरेट"], "प्रशासनिक समीक्षा बैठक"),
    (["निरीक्षण", "निरीक्षण किया", "inspection"], "निरीक्षण"),
    (["रैली", "जनसभा", "public rally", "रोड शो", "road show"], "रैली"),
    (["चुनावी", "मतदाता", "मतदान", "वोट", "प्रचार", "poll campaign", "voting", "polling", "कैंपेन"], "चुनाव प्रचार"),
    (["उद्घाटन", "लोकार्पण", "inauguration", "inaugurated", "शिलान्यास", "dedication"], "उद्घाटन"),
    (["घोषणा", "नई योजना", "योजना की जानकारी", "योजना का लाभ", "scheme launch"], "योजना घोषणा"),
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "मस्जिद", "धार्मिक", "सांस्कृतिक कार्यक्रम", "जयंती", "महोत्सव", "पर्व"], "धार्मिक / सांस्कृतिक कार्यक्रम"),
    (["सम्मान", "सम्मानित", "शॉल", "श्रीफल", "felicitation", "award", "सम्मान समारोह"], "सम्मान / Felicitation"),
    (["प्रेस वार्ता", "प्रेस कॉन्फ़्रेंस", "मीडिया से बातचीत", "मीडिया ब्रिफिंग", "pc"], "प्रेस कॉन्फ़्रेंस / मीडिया"),
    (["शुभकामनाएं", "शुभकामनाएँ", "बधाई", "congratulations", "best wishes", "greetings", "मुबारक"], "शुभकामना / बधाई"),
    (["जन्मदिन", "birthday", "अवतरण दिवस"], "जन्मदिन शुभकामना"),
    (["श्रद्धांजलि", "शोक संदेश", "दिवंगत", "अंतिम यात्रा", "पुण्यतिथि", "condolence", "tribute", "rip"], "शोक संदेश"),
]

SCHEME_PATTERNS = {
    r"\bPMAY\b": "प्रधानमंत्री आवास योजना",
    r"प्रधानमंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"प्रधान मंत्री आवास योजना": "प्रधानमंत्री आवास योजना",
    r"PM Awas": "प्रधानमंत्री आवास योजना",
    r"आवास योजना": "प्रधानमंत्री आवास योजना",
    r"आयुष्मान भारत": "आयुष्मान भारत",
    r"\bAyushman\b": "आयुष्मान भारत",
    r"उज्ज्वला योजना": "प्रधानमंत्री उजस़्वला योजना",
    r"स्वच्छ भारत": "स्वच्छ भारत मिशन",
    r"जन धन": "प्रधानमंत्री जन धन योजना",
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
    "केंद्र सरकार": "केंद्र सरकार",
    "राज्य सरकार": "राज्य सरकार",
    "भारतीय सेना": "भारतीय सेना",
    "Indian Army": "भारतीय सेना",
}

# -------------------------
# Canonical locations (merged)
# -------------------------

CANONICAL_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "रायगढ़": {"canonical": "रायगढ़", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "Raigarh": {"canonical": "रायगढ़", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला"]},
    "खरसिया": {"canonical": "खरसिया", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "Kharsia": {"canonical": "खरसिया", "hierarchy": ["छत्तीसगढ़", "रायगढ़ जिला", "खरसिया विधानसभा"]},
    "रायपुर": {"canonical": "रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "Raipur": {"canonical": "रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "नया रायपुर": {"canonical": "नया रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
    "New Raipur": {"canonical": "नया रायपुर", "hierarchy": ["छत्तीसगढ़", "रायपुर जिला"]},
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
    "Surajpur": {"canonical": "सुरजपुर", "hierarchy": ["छत्तीसगढ़", "सुरजपुर जिला"]},
    "जगदलपुर": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "Jagdalpur": {"canonical": "जगदलपुर", "hierarchy": ["छत्तीसगढ़", "बस्तर जिला"]},
    "कोंडागाँव": {"canonical": "कोंडागाँव", "hierarchy": ["छत्तीसगढ़", "कोंडागाँव जिला"]},
    "Kondagaon": {"canonical": "कोंडागाँव", "hierarchy": ["छत्तीसगढ़", "कोंडागाँव जिला"]},
    "नारायणपुर": {"canonical": "नारायणपुर", "hierarchy": ["छत्तीसगढ़", "नारायणपुर जिला"]},
    "Narayanpur": {"canonical": "नारायणपुर", "hierarchy": ["छत्तीसगढ़", "नारायणपुर जिला"]},
    "जांजगीर": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "Janjgir": {"canonical": "जांजगीर", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "चंपा": {"canonical": "चंपा", "hierarchy": ["छत्तीसगढ़", "जांजगीर-चंपा जिला"]},
    "राजनांदगाँव": {"canonical": "राजनांदगाँव", "hierarchy": ["छत्तीसगढ़", "राजनांदगाँव जिला"]},
    "Mahasamund": {"canonical": "महासमुंद", "hierarchy": ["छत्तीसगढ़", "महासमुंद जिला"]},
    "महासमुंद": {"canonical": "महासमुंद", "hierarchy": ["छत्तीसगढ़", "महासमुंद जिला"]},
    "धमतरी": {"canonical": "धमतरी", "hierarchy": ["छत्तीसगढ़", "धमतरी जिला"]},
    "Dhamtari": {"canonical": "धमतरी", "hierarchy": ["छत्तीसगढ़", "धमतरी जिला"]},
    "बालोद": {"canonical": "बालोद", "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "Balod": {"canonical": "बालोद", "hierarchy": ["छत्तीसगढ़", "बालोदजिला"]},
    "गरियाबंद": {"canonical": "गरियाबंद", "hierarchy": ["छत्तीसगढ़", "गरियाबंद जिला"]},
    "Gariaband": {"canonical": "गरियाबंद", "hierarchy": ["छत्तीसगढ़", "गरियाबंद जिला"]},
    "बीजापुर": {"canonical": "बीजापुर", "hierarchy": ["छत्तीसगढ़", "बीजापुर जिला"]},
    "Bijapur": {"canonical": "बीजापुर", "hierarchy": ["छत्तीसगढ़", "बीजापुर जिला"]},
    "दंतेवाड़ा": {"canonical": "दंतेवाड़ा", "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ा जिला"]},
    "Dantewada": {"canonical": "दंतेवाड़ा", "hierarchy": ["छत्तीसगढ़", "दंतेवाड़ा जिला"]},
    "सुकमा": {"canonical": "सुकमा", "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
    "Sukma": {"canonical": "सुकमा", "hierarchy": ["छत्तीसगढ़", "सुकमाजिला"]},
    # Newer districts / splits
    "बलौदाबाजार": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजार जिला"]},
    "भाटापारा": {"canonical": "बलौदाबाजार", "hierarchy": ["छत्तीसगढ़", "बलौदाबाजार जिला"]},
    "कवर्धा": {"canonical": "कवर्धा", "hierarchy": ["छत्तीसगढ़", "कबीरधाम जिला"]},
    "कांकेर": {"canonical": "कांकेर", "hierarchy": ["छत्तीसगढ़", "कांकेरजिला"]},
    "कोरिया": {"canonical": "कोरिया", "hierarchy": ["छत्तीसगढ़", "कोरियाजिला"]},
    "जशपुर": {"canonical": "जशपुर", "hierarchy": ["छत्तीसगढ़", "जशपुरजिला"]},
    "मुंगेली": {"canonical": "मुंगेली", "hierarchy": ["छत्तीसगढ़", "मुंगेलीजिला"]},
    "बेमेतरा": {"canonical": "बेमेतरा", "hierarchy": ["छत्तीसगढ़", "बेमेतराजिला"]},
    "गौरेला": {"canonical": "गौरेला-पेंड्रा-मरवाही", "hierarchy": ["छत्तीसगढ़", "गौरेला-पेंड्रा-मरवाहीजिला"]},
    "पेंड्रा": {"canonical": "गौरेला-पेंड्रा-मरवाही", "hierarchy": ["छत्तीसगढ़", "गौरेला-पेंड्रा-मरवाहीजिला"]},
    "सारंगढ़": {"canonical": "सारंगढ़-बिलाईगढ़", "hierarchy": ["छत्तीसगढ़", "सारंगढ़-बिलाईगढ़जिला"]},
    "मोहला": {"canonical": "मोहला-मानपुर", "hierarchy": ["छत्तीसगढ़", "मोहला-मानपुरजिला"]},
    "शक्ति": {"canonical": "शक्ति", "hierarchy": ["छत्तीसगढ़", "शक्तिजिला"]},
    "खैरागढ़": {"canonical": "खैरागढ़", "hierarchy": ["छत्तीसगढ़", "खैरागढ़जिला"]},
    "मनेंद्रगढ़": {"canonical": "मनेंद्रगढ़", "hierarchy": ["छत्तीसगढ़", "मनेंद्रगढ़-चिरमिरी-भरतपुरजिला"]},
}

# -------------------------
# Utility
# -------------------------

def normalize_text_basic(text: str) -> str:
    text = re.sub(r"[–—\-_:“”\"'`]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

# -------------------------
# Feature extractors
# -------------------------

def extract_schemes(text: str) -> Tuple[List[str], float]:
    schemes = set()
    for pattern, canonical in SCHEME_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            schemes.add(canonical)
    if not schemes:
        return [], 0.0
    conf = min(0.95, 0.65 + 0.08 * len(schemes))
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
    lowered = text.lower()
    orgs = set()
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
        (["उद्योग", "उद्योगों", "फैक्ट्री", "industry"], "उद्योग / व्यापार"),
    ]
    lower = text.lower()
    for words, bucket in topic_map:
        if any(w.lower() in lower for w in words):
            buckets.append(bucket)

    buckets = sorted(set(buckets))
    if not buckets:
        return [], 0.0
    conf = min(0.9, 0.55 + 0.05 * len(buckets))
    return buckets, conf

# -------------------------
# Location helpers
# -------------------------

def extract_inline_location_candidates(text: str) -> List[str]:
    candidates: List[str] = []
    patterns = [
        r"([अ-हक़-य़A-Za-z]+)\s+जिला",
        r"([अ-हक़-य़A-Za-z]+)\s+विधानसभा",
        r"([अ-हक़-य़A-Za-z]+)\s+नगर निगम",
        r"([अ-हक़-य़A-Za-z]+)\s+नगर पालिका",
        r"([अ-हक़-य़A-Za-z]+)\s+नगर पंचायत",
        r"([अ-हक़-य़A-Za-z]+)\s+तहसील",
        r"([अ-हक़-य़A-Za-z]+)\s+थाना",
        r"([अ-हक़-य़A-Za-z]+)\s+विकासखंड",
        r"([अ-हक़-य़A-Za-z]+)\s+चौकी",
        r"([अ-हक़-य़A-Za-z]+)\s+ग्राम पंचायत",
        r"([अ-हक़-य़A-Za-z]+)\s+ग्राम",
        r"([अ-हक़-य़A-Za-z]+)\s+गाँव",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            name = m.group(1).strip()
            if len(name) >= 2:
                candidates.append(name)
    return candidates

def normalize_location(text: str, hint_location: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    candidates: List[str] = []
    if hint_location:
        can = hint_location.get("canonical") or hint_location.get("district")
        if can:
            candidates.append(str(can))

    for key in CANONICAL_LOCATIONS.keys():
        if key in text or key.lower() in text.lower():
            candidates.append(key)

    candidates.extend(extract_inline_location_candidates(text))

    if not candidates:
        return None, 0.0

    best_raw, _ = Counter(candidates).most_common(1)[0]
    loc_info = CANONICAL_LOCATIONS.get(best_raw)

    if not loc_info:
        loc_obj = {
            "district": None,
            "assembly": None,
            "block": None,
            "gp": None,
            "village": None,
            "ulb": None,
            "zone": None,
            "ward": None,
            "canonical_key": None,
            "canonical": best_raw,
            "aliases": [best_raw],
            "hierarchy_path": ["छत्तीसगढ़"],
            "visit_count": 1,
        }
        return loc_obj, 0.55

    canonical = loc_info["canonical"]
    hierarchy = loc_info.get("hierarchy", [])
    district = None
    assembly = None
    for level in hierarchy:
        if "जिला" in level:
            district = level.replace(" जिला", "")
        if "विधानसभा" in level:
            assembly = level.replace(" विधानसभा", "")

    loc_obj = {
        "district": district,
        "assembly": assembly,
        "block": None,
        "gp": None,
        "village": None,
        "ulb": None,
        "zone": None,
        "ward": None,
        "canonical_key": f"CG_{canonical}",
        "canonical": canonical,
        "aliases": [best_raw] if best_raw not in [canonical] else [canonical],
        "hierarchy_path": hierarchy,
        "visit_count": 1,
    }
    return loc_obj, 0.88

# -------------------------
# Event inference
# -------------------------

def infer_event_from_keywords(text: str) -> Tuple[str, float]:
    text_l = text.lower()
    candidate = None
    best = 0.0
    for keywords, label in EVENT_KEYWORD_CLUSTERS:
        if any(kw.lower() in text_l for kw in keywords):
            base = 0.70
            if label in [
                "शोक संदेश",
                "जन्मदिन शुभकामना",
                "प्रशासनिक समीक्षा बैठक",
                "आंतरिक सुरक्षा / पुलिस",
                "खेल / गौरव",
                "आपदा / दुर्घटना",
            ]:
                base = 0.80
            if base > best:
                best = base
                candidate = label
    if candidate is None:
        candidate = "अन्य"
        best = 0.30
    return candidate, best

def combine_event_signals(
    hint_event_v5: Optional[str],
    keyword_event: str,
    keyword_conf: float,
    rescue_event: Optional[str],
) -> Tuple[str, float, Dict[str, Any]]:
    meta: Dict[str, Any] = {
        "source_keyword": keyword_event,
        "source_hint_v5": hint_event_v5,
        "source_rescue": rescue_event,
        "agreement_score": 0.0,
    }

    def norm(e: Optional[str]) -> Optional[str]:
        if e is None:
            return None
        e = e.strip()
        if e not in ALLOWED_EVENT_TYPES_HI:
            return None
        return e

    hint = norm(hint_event_v5)
    resc = norm(rescue_event)
    kw = norm(keyword_event) or "अन्य"

    if hint and kw == hint and kw != "अन्य":
        chosen = kw
        agreement = 1.0
    elif resc and kw == resc and kw != "अन्य":
        chosen = kw
        agreement = 1.0
    elif resc and resc != "अन्य":
        chosen = resc
        agreement = 0.8
    elif hint and hint != "अन्य":
        chosen = hint
        agreement = 0.7
    else:
        chosen = kw
        agreement = 0.5 if kw != "अन्य" else 0.2

    base = keyword_conf
    if chosen != "अन्य":
        if agreement >= 1.0:
            base = max(base, 0.82)
        elif agreement >= 0.8:
            base = max(base, 0.78)
        elif agreement >= 0.7:
            base = max(base, 0.72)
        else:
            base = max(base, 0.65)
    else:
        base = min(base, 0.45)

    meta["agreement_score"] = agreement
    return chosen, round(base, 3), meta

# -------------------------
# Rescue detectors (ordered)
# -------------------------

def _looks_like_sports_tweet(text_l: str) -> bool:
    sports_specific = ["क्रिकेट", "टीम इंडिया", "world cup", "वर्ल्ड कप", "t20", "टी20", "ipl", "odi", "वनडे", "bcci", "रणजी"]
    if any(kw in text_l for kw in sports_specific):
        return True
    if "मैच" in text_l and any(kw in text_l for kw in ["जीत", "हार", "विकेट", "रन", "won", "lost"]):
        return True
    return False

def _looks_like_sports_achievement(text_l: str) -> bool:
    return any(kw in text_l for kw in ["स्वर्ण पदक", "रजत पदक", "कांस्य पदक", "medal", "championship"])

def _looks_like_security_context(text_l: str) -> bool:
    return any(kw in text_l for kw in ["माओवादी", "माओवाद", "नक्सल", "नक्सली", "आतंक", "उग्रवाद", "शहीद", "jawan", "encounter"])

def _looks_like_administrative_update(text_l: str) -> bool:
    return any(kw in text_l for kw in ["बैठक", "समीक्षा", "कलेक्टर", "निर्देश", "अधिकारी", "progress", "status", "निरीक्षण"])

def _looks_like_scheme_implementation(text_l: str, schemes: List[str]) -> bool:
    return bool(schemes) or any(kw in text_l for kw in ["लाभार्थी", "वितरण", "खाता", "subsidy", "dbt", "installments"])

def _looks_like_election_politics(text_l: str) -> bool:
    return any(kw in text_l for kw in ["चुनाव", "मतदान", "वोट", "प्रचार", "कैंपेन", "प्रत्याशी", "nomination", "polling", "रैली"])

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
    return any(kw in text_l for kw in ["बधाई", "शुभकामना", "best wishes", "greetings", "मुबारक"])

def _looks_like_digital_only(text_l: str, loc_obj: Optional[Dict[str, Any]]) -> bool:
    digital_kw = ["online", "ऑनलाइन", "live", "लाइव", "जुड़ें", "link", "लिंक", "stream"]
    no_loc = not (loc_obj and loc_obj.get("canonical"))
    return no_loc and any(kw in text_l for kw in digital_kw)

def rescue_other_events_OpenAI_V1(text: str, base_pd: Dict[str, Any]) -> Dict[str, Any]:
    text_l = normalize_text_basic(text)
    original_event = base_pd.get("event_type") or "अन्य"
    loc_obj = base_pd.get("location")
    schemes = base_pd.get("schemes_mentioned") or []

    pd_extra: Dict[str, Any] = {
        "event_type_rescue": None,
        "content_mode": None,
        "is_other_original": (original_event == "अन्य"),
        "is_rescued_other": False,
        "rescue_tag": None,
        "rescue_confidence_bonus": 0.0,
    }

    # 0. If original non-"अन्य": सिर्फ content_mode refine करेंगे
    if original_event != "अन्य":
        if _looks_like_digital_only(text_l, loc_obj):
            pd_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
        return pd_extra

    # --- Priority 1: High-specific categories ---
    if _looks_like_sports_tweet(text_l) or _looks_like_sports_achievement(text_l):
        pd_extra.update({
            "event_type_rescue": "खेल / गौरव",
            "content_mode": "खेल / उपलब्धि पर प्रतिक्रिया",
            "is_rescued_other": True,
            "rescue_tag": "sports_OpenAI_V1",
            "rescue_confidence_bonus": 0.06,
        })
        return pd_extra

    if _looks_like_security_context(text_l):
        pd_extra.update({
            "event_type_rescue": "आंतरिक सुरक्षा / पुलिस",
            "content_mode": "नीति / वक्तव्य",
            "is_rescued_other": True,
            "rescue_tag": "security_OpenAI_V1",
            "rescue_confidence_bonus": 0.07,
        })
        return pd_extra

    # --- Priority 2: Governance ---
    if _looks_like_administrative_update(text_l):
        pd_extra.update({
            "event_type_rescue": "प्रशासनिक समीक्षा बैठक",
            "content_mode": "नीति / वक्तव्य",
            "is_rescued_other": True,
            "rescue_tag": "admin_OpenAI_V1",
            "rescue_confidence_bonus": 0.06,
        })
        return pd_extra

    if _looks_like_election_politics(text_l):
        pd_extra.update({
            "event_type_rescue": "चुनाव प्रचार",
            "content_mode": "मैदान-स्तर कार्यक्रम",
            "is_rescued_other": True,
            "rescue_tag": "election_OpenAI_V1",
            "rescue_confidence_bonus": 0.06,
        })
        return pd_extra

    # --- Priority 3: Development & Schemes ---
    if _looks_like_industrial_development(text_l) or _looks_like_infrastructure_work(text_l):
        pd_extra.update({
            "event_type_rescue": "उद्घाटन",
            "content_mode": "मैदान-स्तर कार्यक्रम",
            "is_rescued_other": True,
            "rescue_tag": "infra_dev_OpenAI_V1",
            "rescue_confidence_bonus": 0.06,
        })
        return pd_extra

    if _looks_like_scheme_implementation(text_l, schemes) or _looks_like_relief_humanitarian(text_l):
        pd_extra.update({
            "event_type_rescue": "योजना घोषणा",
            "content_mode": "मैदान-स्तर कार्यक्रम",
            "is_rescued_other": True,
            "rescue_tag": "scheme_OpenAI_V1",
            "rescue_confidence_bonus": 0.06,
        })
        return pd_extra

    # --- Priority 4: Political / Cultural / Greetings ---
    if _looks_like_general_political(text_l) or _looks_like_policy_statement(text_l):
        pd_extra.update({
            "event_type_rescue": "राजनीतिक वक्तव्य",
            "content_mode": "नीति / वक्तव्य",
            "is_rescued_other": True,
            "rescue_tag": "political_OpenAI_V1",
            "rescue_confidence_bonus": 0.05,
        })
        return pd_extra

    if _looks_like_cultural_religious(text_l):
        pd_extra.update({
            "event_type_rescue": "धार्मिक / सांस्कृतिक कार्यक्रम",
            "content_mode": "सामान्य शुभकामनाएँ / पर्व",
            "is_rescued_other": True,
            "rescue_tag": "cultural_OpenAI_V1",
            "rescue_confidence_bonus": 0.05,
        })
        return pd_extra

    if _looks_like_congratulatory_general(text_l):
        pd_extra.update({
            "event_type_rescue": "शुभकामना / बधाई",
            "content_mode": "सामान्य शुभकामनाएँ / पर्व",
            "is_rescued_other": True,
            "rescue_tag": "greetings_OpenAI_V1",
            "rescue_confidence_bonus": 0.04,
        })
        return pd_extra

    # --- Fallback: digital-mode only ---
    if _looks_like_digital_only(text_l, loc_obj):
        pd_extra.update({
            "content_mode": "डिजिटल / सोशल-मीडिया पोस्ट",
            "rescue_tag": "digital_mode_OpenAI_V1",
            "rescue_confidence_bonus": 0.02,
        })
        return pd_extra

    pd_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
    return pd_extra

# -------------------------
# Confidence & review
# -------------------------

def compute_confidence_OpenAI_V1(
    c_event_final: float,
    c_loc: float,
    c_schemes: float,
    c_topics: float,
    c_targets: float,
    c_comm: float,
    c_org: float,
    event_type: str,
    location_obj: Optional[Dict[str, Any]],
    people: List[Any],
    agreement_score: float,
    rescue_bonus: float,
    text_len: int,
) -> float:
    good_event = event_type != "अन्य"
    has_loc = bool(location_obj and location_obj.get("canonical"))
    has_people = bool(people)
    has_groups = c_targets > 0 or c_comm > 0
    has_schemes = c_schemes > 0
    has_topics = c_topics > 0
    has_org = c_org > 0

    base = 0.2
    if good_event:
        base += 0.25
    if has_loc:
        base += 0.2
    if has_schemes:
        base += 0.05
    if has_topics:
        base += 0.05
    if has_groups:
        base += 0.05
    if has_org:
        base += 0.03

    weighted = (
        2 * c_event_final
        + 2 * c_loc
        + c_schemes
        + c_topics
        + c_targets
        + c_comm
        + c_org
    ) / 9.0

    score = max(base, (base * 0.7 + weighted * 0.3))
    score += 0.05 * (agreement_score - 0.5)

    if good_event and has_loc and has_people:
        score += 0.05
    elif good_event and (has_loc or has_people):
        score += 0.02

    score += rescue_bonus

    HIGH_PRECISION = ["शोक संदेश", "जन्मदिन शुभकामना", "आंतरिक सुरक्षा / पुलिस", "खेल / गौरव", "आपदा / दुर्घटना"]
    substantial = text_len > 20

    if event_type in HIGH_PRECISION and substantial and good_event and (has_loc or has_people or has_schemes):
        score = max(score, 0.92)

    if text_len <= 20:
        score = min(score, 0.88)

    return round(min(0.99, max(0.0, score)), 3)

def decide_review_status(conf: float) -> Tuple[str, bool]:
    if conf >= 0.90:
        return "auto_approved", False
    if conf >= 0.75:
        return "pending", False
    return "pending", True

# -------------------------
# Main parsing
# -------------------------

def parse_tweet_OpenAI_V1(record: Dict[str, Any]) -> Dict[str, Any]:
    text = record.get("raw_text") or record.get("text") or ""
    created_at = record.get("created_at")
    old_v5 = record.get("parsed_data_v5") or {}
    old_v6 = record.get("parsed_data_v6") or {}
    hint_event_v5 = old_v6.get("event_type") or old_v5.get("event_type")

    schemes, c_schemes = extract_schemes(text)
    word_buckets, c_topics = make_word_buckets(text)
    target_groups, c_targets = extract_target_groups(text)
    communities, c_comm = extract_communities(text)
    orgs, c_org = extract_orgs(text)

    people_mentioned = old_v5.get("people_mentioned", []) or old_v6.get("people_mentioned", [])

    hint_loc = old_v6.get("location") or old_v5.get("location")
    loc_obj, c_loc = normalize_location(text, hint_loc)

    kw_event, c_kw = infer_event_from_keywords(text)
    base_pd_for_rescue = {
        "event_type": kw_event,
        "location": loc_obj,
        "schemes_mentioned": schemes,
    }
    rescue_info = rescue_other_events_OpenAI_V1(text, base_pd_for_rescue)
    rescue_event = rescue_info.get("event_type_rescue")

    event_type_final, c_event_final, event_meta = combine_event_signals(
        hint_event_v5=hint_event_v5,
        keyword_event=kw_event,
        keyword_conf=c_kw,
        rescue_event=rescue_event,
    )

    content_mode = rescue_info.get("content_mode")
    if not content_mode:
        if loc_obj and loc_obj.get("canonical"):
            content_mode = "मैदान-स्तर कार्यक्रम"
        else:
            content_mode = "डिजिटल / सोशल-मीडिया पोस्ट"

    rescue_bonus = rescue_info.get("rescue_confidence_bonus", 0.0)
    is_rescued_other = bool(rescue_info.get("is_rescued_other") and event_type_final != "अन्य")

    conf = compute_confidence_OpenAI_V1(
        c_event_final=c_event_final,
        c_loc=c_loc,
        c_schemes=c_schemes,
        c_topics=c_topics,
        c_targets=c_targets,
        c_comm=c_comm,
        c_org=c_org,
        event_type=event_type_final,
        location_obj=loc_obj,
        people=people_mentioned or [],
        agreement_score=event_meta.get("agreement_score", 0.5),
        rescue_bonus=rescue_bonus,
        text_len=len(text),
    )

    review_status, needs_review = decide_review_status(conf)

    parsed_data_OpenAI_V1 = {
        "event_type": event_type_final,
        "event_type_secondary": [],
        "event_date": created_at[:10] if created_at else None,
        "location": loc_obj,
        "people_mentioned": people_mentioned or [],
        "schemes_mentioned": schemes,
        "word_buckets": word_buckets,
        "target_groups": target_groups,
        "communities": communities,
        "organizations": orgs,
        "hierarchy_path": (loc_obj or {}).get("hierarchy_path", []),
        "visit_count": (loc_obj or {}).get("visit_count", 0),
        "confidence": conf,
        "review_status": review_status,
        "needs_review": needs_review,
        "content_mode": content_mode,
        "is_other_original": (kw_event == "अन्य"),
        "is_rescued_other": is_rescued_other,
        "rescue_tag": rescue_info.get("rescue_tag"),
        "source_hint_event": hint_event_v5,
        "source_keyword_event": kw_event,
        "source_rescue_event": rescue_event,
        "agreement_score": event_meta.get("agreement_score", 0.5),
    }

    return {
        "tweet_id": record.get("tweet_id"),
        "created_at": created_at,
        "raw_text": text,
        "parsed_data_v5": old_v5,
        "parsed_data_v6": old_v6,
        "parsed_data_OpenAI_V1": parsed_data_OpenAI_V1,
        "metadata_OpenAI_V1": {"model": "OpenAI_V1-rule-engine-consensus-think-harder"},
    }

def reparse_file_OpenAI_V1(input_path: Path, output_path: Path) -> None:
    print(f"🚀 OpenAI_V1 Parsing शुरू: {input_path} → {output_path}")
    total = 0
    stats = Counter()

    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            total += 1
            new_rec = parse_tweet_OpenAI_V1(rec)
            pd = new_rec["parsed_data_OpenAI_V1"]

            c = pd["confidence"]
            if c >= 0.90:
                stats["High (>=0.90)"] += 1
            elif c >= 0.70:
                stats["Medium (0.70-0.90)"] += 1
            else:
                stats["Low (<0.70)"] += 1

            if pd["event_type"] == "अन्य":
                stats["Event: अन्य"] += 1
            else:
                stats[f"Event: {pd['event_type']}"] += 1

            if pd["is_rescued_other"]:
                stats["Rescued Others"] += 1

            fout.write(json.dumps(new_rec, ensure_ascii=False) + "\n")

    print(f"\n✅ OpenAI_V1 Complete. Total tweets: {total}")
    print(f"   High  (>=0.90): {stats['High (>=0.90)']}")
    print(f"   Medium(0.70-0.90): {stats['Medium (0.70-0.90)']}")
    print(f"   Low   (<0.70): {stats['Low (<0.70)']}")
    print(f"   Rescued Others: {stats['Rescued Others']}")
    print("\n   Event distribution (top 20):")
    for k, v in list(stats.most_common(30)):
        if k.startswith("Event:"):
            print(f"     {k}: {v}")

if __name__ == "__main__":
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    reparse_file_OpenAI_V1(inp, out)
