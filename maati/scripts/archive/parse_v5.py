#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Dhruv – Parsing Logic V5 (Hindi-first, robust, single script)

मुख्य विशेषताएँ:
- Hindi-first event_type taxonomy
- Location normalization + inline pattern based extraction
- Schemes, word buckets, target groups, communities, organizations
- Confidence model (base V4 style) + V5 rescue bonus
- "अन्य" tweets के लिए special rescue logic
- नया axis: content_mode (मैदान-स्तर कार्यक्रम / नीति / डिजिटल / खेल / शुभकामनाएँ)
- Review flags: is_other_original, is_rescued_other, rescue_tag

इनपुट JSONL (प्रति लाइन एक tweet record) – minimally:
{
  "tweet_id": "...",
  "created_at": "2025-11-20T10:30:00Z",
  "raw_text": "..."   # या "text"
  # वैकल्पिक:
  # "parsed_data_v4" / "parsed_data_v3" / "parsed_data_v2" ...
}

आउटपुट JSONL:
{
  "tweet_id": "...",
  "created_at": "...",
  "raw_text": "...",
  "parsed_data_v5": { ... },
  "metadata_v5": { ... },
  # वैकल्पिक रूप से पुराने parsed_data_x भी preserve हो सकते हैं अगर input में हैं
}
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict

# -------------------------
# Paths
# -------------------------

DEFAULT_INPUT = Path("/mnt/data/parsed_tweets_v4.jsonl")
DEFAULT_OUTPUT = Path("/mnt/data/parsed_tweets_v5.jsonl")

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
    # बैठक / मुलाक़ात / सत्र
    (["बैठक", "मुलाकात", "भेंट", "बैठक ली", "बैठक में", "बैठक का", "अध्यक्षता की", "सत्र", "सदन की कार्यवाही"], "बैठक"),
    # जनसम्पर्क / जनदर्शन
    (["जनसम्पर्क", "जन संपर्क", "जनसंपर्क", "जनदर्शन", "जन-दर्शन", "जन सुनवाई", "जनसुनवाई"], "जनसम्पर्क / जनदर्शन"),
    # प्रशासनिक समीक्षा / विभागीय
    (["समीक्षा बैठक", "समीक्षा की", "समीक्षा की गई", "अधिकारियों के साथ", "विभागीय बैठक", "कलेक्टर", "कलेक्टरेट", "समीक्षा कार्य"], "प्रशासनिक समीक्षा बैठक"),
    # निरीक्षण
    (["निरीक्षण", "निरीक्षण किया", "निरीक्षण हेतु", "inspection"], "निरीक्षण"),
    # रैली – political संदर्भ
    (["रैली", "जनसभा", "public rally", "road show", "रोड शो"], "रैली"),
    # चुनाव प्रचार
    (["चुनावी", "मतदाता", "मतदान", "चुनाव प्रचार", "poll campaign"], "चुनाव प्रचार"),
    # उद्घाटन / लोकार्पण
    (["उद्घाटन", "लोकार्पण", "inauguration", "inaugurated", "शिलान्यास"], "उद्घाटन"),
    # योजना घोषणा
    (["घोषणा", "नई योजना", "योजना की जानकारी", "योजना का लाभ"], "योजना घोषणा"),
    # धार्मिक / सांस्कृतिक
    (["मंदिर", "पूजा", "आरती", "गुरुद्वारा", "गुरु नानक", "मस्जिद", "धार्मिक", "सांस्कृतिक कार्यक्रम", "जयंती"], "धार्मिक / सांस्कृतिक कार्यक्रम"),
    # सम्मान / Felicitation
    (["सम्मान", "सम्मानित", "शॉल", "श्रीफल", "समारोह", "felicitation"], "सम्मान / Felicitation"),
    # प्रेस / मीडिया
    (["प्रेस वार्ता", "प्रेस कॉन्फ़्रेंस", "मीडिया ब्रिफिंग", "मीडिया से बातचीत"], "प्रेस कॉन्फ़्रेंस / मीडिया"),
    # शुभकामना / बधाई
    (["शुभकामनाएं", "शुभकामनाएँ", "बधाई", "congratulations"], "शुभकामना / बधाई"),
    # जन्मदिन शुभकामना
    (["जन्मदिन", "birthday"], "जन्मदिन शुभकामना"),
    # शोक संदेश
    (["श्रद्धांजलि", "शोक संदेश", "दिवंगत", "अंतिम यात्रा", "पुण्यतिथि", "condolence", "हादसे", "मृत्यु", "निधन", "बलिदान", "शहीद"], "शोक संदेश"),
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
    r"\bUjjwala\b": "प्रधानमंत्री उज्जला योजना",

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
    "INC": " भारतीय राष्ट्रीय कांग्रेस",
    "Indian National Congress": "भारतीय राष्ट्रीय कांग्रेस",
    "RSS": "राष्ट्रीय स्वयंसेवक संघ",
    "आरएसएस": "राष्ट्रीय स्वयंसेवक संघ",
    "सरकार": "सरकार",
    "केंद्र सरकार": "केंद्र सरकार",
    "राज्य सरकार": "राज्य सरकार",
    "भारतीय सेना": "भारतीय सेना",
    "Indian Army": "भारतीय सेना",
}

# --- Global Geo Data (Comprehensive) ---
GLOBAL_GEO_HIERARCHY_V5 = {}
GLOBAL_LOCATION_LOOKUP_V5 = {} # Stores all levels of hierarchy
GLOBAL_ALIAS_TO_CANONICAL_V5 = {} # Maps all aliases to canonical Hindi name and type

# Helper functions for text normalization
NUKTA_MAP = str.maketrans({
  'क़':'क','ख़':'ख','ग़':'ग','ज़':'ज','फ़':'फ','ड़':'ड','ढ़':'ढ','ऱ':'र','य़':'य'
})

COMBINING = re.compile(r"[\u093C\u094D\u200C\u200D\uFE00-\uFE0F]")
MATRA_MAP = {
  'ा': 'aa', 'ि': 'i', 'ी': 'ii', 'ु': 'u', 'ू': 'uu',
  'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ृ': 'ri',
  'ॉ': 'o', 'ॅ': 'ae'
}


def fold_nukta(s: str) -> str:
  return COMBINING.sub('', s.translate(NUKTA_MAP))


def translit_basic(dev: str) -> str:
  # Minimal conservative transliteration for bootstrap; improved later
  m = {
    'अ':'a','आ':'aa','इ':'i','ई':'ii','उ':'u','ऊ':'uu','ए':'e','ऐ':'ai','ओ':'o','औ':'au',
    'क':'k','ख':'kh','ग':'g','gh','च':'ch','छ':'chh','ज':'j','झ':'jh','ट':'t','ठ':'th','ड':'d','ढ':'dh','ण':'n',
    'त':'t','थ':'th','द':'d','ध':'dh','न':'n','प':'p','फ':'ph','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'v','श':'sh','ष':'sh','स':'s','ह':'h'
  }
  out = []
  for ch in dev:
    if ch in MATRA_MAP:
      out.append(MATRA_MAP[ch])
    else:
      out.append(m.get(ch, ch))
  return ''.join(out)

# Helper functions for location matching (adapted from location_matcher.py)
def _generate_variants(name: str) -> List[str]:
    """
    Generate all possible variants of a location name (adapted from location_matcher.py).
    """
    if not name or not name.strip():
        return []
    
    variants = set()
    
    # Original
    variants.add(name.lower().strip())
    
    # Nukta-folded
    variants.add(fold_nukta(name.lower().strip()))
    
    # Transliterated
    variants.add(translit_basic(name.lower().strip()))
    
    # Remove empty strings
    variants.discard('')
    
    return list(variants)

def build_location_lookup_tables(geo_data: dict) -> Tuple[Dict[str, dict], Dict[str, Tuple[str, str, str]]]:
    """
    Builds a comprehensive lookup for all geographical entities and their aliases.
    Returns (GLOBAL_LOCATION_LOOKUP, GLOBAL_ALIAS_TO_CANONICAL).
    Each entry in GLOBAL_LOCATION_LOOKUP will also store the full hierarchy details.
    Each entry in GLOBAL_ALIAS_TO_CANONICAL maps alias -> (canonical_hindi_name, type, canonical_key).
    """
    lookup = {}
    alias_to_canonical = {}
    
    state_name_hindi = geo_data.get('state', '')
    state_code = geo_data.get('state_code', '')

    # Helper to add to lookup and alias_to_canonical
    def add_location_to_lookups(lookup_dict, alias_dict, name_hindi, name_english, type_str, hierarchy_list, canonical_key, original_data={}):
        full_aliases = set()
        if name_hindi:
            full_aliases.update(_generate_variants(name_hindi))
        if name_english: # Add english name as an alias too
            full_aliases.add(name_english.lower().strip())
        
        record = {
            'type': type_str,
            'name_hindi': name_hindi,
            'name_english': name_english,
            'hierarchy_list': hierarchy_list,
            'canonical_key': canonical_key,
            'aliases': list(full_aliases),
            'original_data': original_data
        }
        
        lookup_dict[name_hindi] = record

        for alias in full_aliases:
            alias_dict[alias] = (name_hindi, type_str, canonical_key)
    
    # Add state itself
    canonical_key_state = f"{state_code}"
    add_location_to_lookups(lookup, alias_to_canonical, state_name_hindi, "Chhattisgarh", "state", 
                            [state_name_hindi], canonical_key_state, {})

    for district in geo_data.get('districts', []):
        district_name_hindi = district.get('name', '')
        district_name_english = "" # We don't have this in chhattisgarh_complete_geography.json
        canonical_key_district = f"{state_code}_{district_name_hindi.replace(' ','_')}"
        
        add_location_to_lookups(lookup, alias_to_canonical, district_name_hindi, district_name_english, "district", 
                                [state_name_hindi, f"{district_name_hindi} जिला"], canonical_key_district, district)
        
        for ac in district.get('acs', []):
            ac_name_hindi = ac.get('name', '')
            ac_name_english = "" # Not available
            canonical_key_ac = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}"

            add_location_to_lookups(lookup, alias_to_canonical, ac_name_hindi, ac_name_english, "assembly", 
                                    [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा"], canonical_key_ac, ac)
            
            for block in ac.get('blocks', []):
                block_name_hindi = block.get('name', '')
                block_name_english = "" # Not available
                canonical_key_block = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}"

                add_location_to_lookups(lookup, alias_to_canonical, block_name_hindi, block_name_english, "block", 
                                        [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड"], canonical_key_block, block)
                
                for gp in block.get('gps', []):
                    gp_name_hindi = gp.get('name', '')
                    gp_name_english = "" # Not available
                    canonical_key_gp = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}_{gp_name_hindi.replace(' ','_')}"

                    add_location_to_lookups(lookup, alias_to_canonical, gp_name_hindi, gp_name_english, "gp", 
                                            [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड", f"{gp_name_hindi} ग्राम पंचायत"], canonical_key_gp, gp)
                    
                    for village in gp.get('villages', []):
                        village_name_hindi = village.get('name', '')
                        village_name_english = "" # Not available
                        canonical_key_village = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}_{gp_name_hindi.replace(' ','_')}_{village_name_hindi.replace(' ','_')}"

                        add_location_to_lookups(lookup, alias_to_canonical, village_name_hindi, village_name_english, "village", 
                                                [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड", f"{gp_name_hindi} ग्राम पंचायत", f"{village_name_hindi} गाँव"], canonical_key_village, village)

        for ulb in district.get('ulbs', []): # Added ULBs under district
            ulb_name_hindi = ulb.get('name', '')
            ulb_name_english = "" # Not available
            canonical_key_ulb = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ulb_name_hindi.replace(' ','_')}_ULB"
            add_location_to_lookups(lookup, alias_to_canonical, ulb_name_hindi, ulb_name_english, "ulb",
                                    [state_name_hindi, f"{district_name_hindi} जिला", f"{ulb_name_hindi} नगर निगम"], canonical_key_ulb, ulb)
            
    return lookup, alias_to_canonical

def load_geo_data_v5():
    """
    Loads the comprehensive Chhattisgarh geography data and builds lookup tables.
    """
    global GLOBAL_GEO_HIERARCHY_V5, GLOBAL_LOCATION_LOOKUP_V5, GLOBAL_ALIAS_TO_CANONICAL_V5
    geo_file = Path('KnowledgeBank/geo-data/chhattisgarh_complete_geography.json')
    try:
        with open(geo_file, 'r', encoding='utf-8') as f:
            GLOBAL_GEO_HIERARCHY_V5 = json.load(f)
        GLOBAL_LOCATION_LOOKUP_V5, GLOBAL_ALIAS_TO_CANONICAL_V5 = build_location_lookup_tables(GLOBAL_GEO_HIERARCHY_V5)
        print(f"✅ Loaded comprehensive geo data from {geo_file}")
    except FileNotFoundError:
        print(f"⚠️ Geo data file not found: {geo_file}. Location features will be limited.")
        GLOBAL_GEO_HIERARCHY_V5 = {"state": "छत्तीसगढ़", "state_code": "CG", "districts": []}
        GLOBAL_LOCATION_LOOKUP_V5 = {"छत्तीसगढ़": {"canonical": "छत्तीसगढ़", "aliases": ["chhattisgarh", "छत्तीसगढ़"], "hierarchy": ["छत्तीसगढ़"], "canonical_key": "CG"}}
        GLOBAL_ALIAS_TO_CANONICAL_V5 = {}
        for alias in GLOBAL_LOCATION_LOOKUP_V5["छत्तीसगढ़"]["aliases"]:
             GLOBAL_ALIAS_TO_CANONICAL_V5[alias.lower()] = ("छत्तीसगढ़", "state", "CG")
    except json.JSONDecodeError:
        print(f"⚠️ Could not decode JSON from {geo_file}. Location features will be limited.")
        GLOBAL_GEO_HIERARCHY_V5 = {"state": "छत्तीसगढ़", "state_code": "CG", "districts": []}
        GLOBAL_LOCATION_LOOKUP_V5 = {"छत्तीसगढ़": {"canonical": "छत्तीसगढ़", "aliases": ["chhattisgarh", "छत्तीसगढ़"], "hierarchy": ["छत्तीसगढ़"], "canonical_key": "CG"}}
        GLOBAL_ALIAS_TO_CANONICAL_V5 = {}
        for alias in GLOBAL_LOCATION_LOOKUP_V5["छत्तीसगढ़"]["aliases"]:
             GLOBAL_ALIAS_TO_CANONICAL_V5[alias.lower()] = ("छत्तीसगढ़", "state", "CG")


# -------------------------
# Feature extractors (schemes, groups, buckets)
# -------------------------

def normalize_event_type_base(raw_event_type_hi: Optional[str], text: str, schemes: List[str]) -> Tuple[str, float]:
    """
    Base event detection (V4-style) – keyword clusters + पुराने label + schemes।
    """
    text_lower = text.lower()
    candidate: Optional[str] = None
    best_conf = 0.0

    # 1) keyword clusters
    for keywords, label in EVENT_KEYWORD_CLUSTERS:
        for kw in keywords:
            if kw.lower() in text_lower:
                base_conf = 0.8
                if label in ("प्रशासनिक समीक्षा बैठक", "जनसम्पर्क / जनदर्शन", "चुनाव प्रचार"):
                    base_conf = 0.87
                if base_conf > best_conf:
                    best_conf = base_conf
                    candidate = label
                break

    # 2) पुराने event_type को consider करो
    if raw_event_type_hi and raw_event_type_hi in ALLOWED_EVENT_TYPES_HI and raw_event_type_hi != "अन्य":
        if candidate is None:
            candidate = raw_event_type_hi
            best_conf = max(best_conf, 0.75)
        elif raw_event_type_hi == candidate:
            best_conf = max(best_conf, 0.93)

    # 3) schemes हों और event अभी भी empty/अन्य हो → योजना घोषणा
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

    # hashtags से buckets
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

    # text-based topics
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

    """

    "XYZ जिला", "XYZ ब्लॉक", "XYZ नगर निगम", "XYZ ग्राम पंचायत", "XYZ ग्राम/गाँव" से raw location phrases निकालो

    """

    candidates: List[str] = []

    patterns = [

        r"([अ-हक़-य़A-Za-z]+)\s+जिला",

        r"([अ-हक़-य़A-Za-z]+)\s+विधानसभा",

        r"([अ-हक़-य़A-Za-z]+)\s+ब्लॉक",

        r"([अ-हक़-य़A-Za-z]+)\s+नगर निगम",

        r"([अ-हक़-य़A-Za-z]+)\s+नगर पालिका",

        r"([अ-हक़-य़A-Za-z]+)\s+नगर पंचायत",

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



def normalize_location(text: str, old_location: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    text_lower = text.lower()
    
    # Stores tuples of (canonical_hindi_name, type_str, canonical_key, match_quality)
    found_locations_info = [] 

    # 1. Prioritize explicit inline location candidates
    inline_candidates = extract_inline_location_candidates(text)
    for candidate in inline_candidates:
        # Check canonical_key and canonical_hindi_name against candidates from the inline candidates
        for canonical_name_hindi, record in GLOBAL_LOCATION_LOOKUP_V5.items():
            if record["type"] not in ["district", "assembly", "block", "gp", "village", "ulb"]:
                continue
            
            # Check if the candidate exactly matches the canonical name or one of its aliases
            if candidate.lower() == canonical_name_hindi.lower() or candidate.lower() in [a.lower() for a in record.get('aliases', [])]:
                # Assign a very high match quality for explicit inline mentions
                match_quality = 2.0 
                found_locations_info.append((canonical_name_hindi, record["type"], record["canonical_key"], match_quality))
                
    # 2. Search GLOBAL_ALIAS_TO_CANONICAL_V5 for other matches (now with word boundaries)
    for alias, (canonical_hindi_name, type_str, canonical_key) in GLOBAL_ALIAS_TO_CANONICAL_V5.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", text_lower):
            # Assign match quality based on type for prioritization, lower than inline candidates
            match_quality = 1.0 # Default for direct alias match
            if type_str == "village": match_quality += 0.05
            elif type_str == "gp": match_quality += 0.04
            elif type_str == "block": match_quality += 0.03
            elif type_str == "assembly": match_quality += 0.02
            elif type_str == "district": match_quality += 0.01

            found_locations_info.append((canonical_hindi_name, type_str, canonical_key, match_quality))
    
    # If multiple matches, prioritize the one with highest match_quality (e.g., most specific type or explicit inline)
    if found_locations_info:
        found_locations_info.sort(key=lambda x: x[3], reverse=True)
        best_match_name_hindi, best_match_type, best_match_canonical_key, _ = found_locations_info[0]
        
        loc_record = GLOBAL_LOCATION_LOOKUP_V5.get(best_match_name_hindi)
        if loc_record:
            # Construct loc_obj from the detailed record
            hierarchy_path = loc_record.get('hierarchy_list', [])
            
            district = next((h.replace(" जिला", "") for h in hierarchy_path if "जिला" in h), None)
            assembly = next((h.replace(" विधानसभा", "") for h in hierarchy_path if "विधानसभा" in h), None)
            block = next((h.replace(" विकासखंड", "") for h in hierarchy_path if "विकासखंड" in h), None)
            gp = next((h.replace(" ग्राम पंचायत", "") for h in hierarchy_path if "ग्राम पंचायत" in h), None)
            village = next((h.replace(" गाँव", "") for h in hierarchy_path if "गाँव" in h), None)
            ulb = next((h.replace(" नगर निगम", "") for h in hierarchy_path if "नगर निगम" in h), None) # Assuming ULB is identified this way

            loc_obj = {
                "district": district,
                "assembly": assembly,
                "block": block,
                "gp": gp,
                "village": village,
                "ulb": ulb,
                "zone": None, # Not directly available from current hierarchy
                "ward": None, # Not directly available from current hierarchy
                "canonical_key": best_match_canonical_key,
                "canonical": best_match_name_hindi,
                "aliases": loc_record.get('aliases', []),
                "hierarchy_path": hierarchy_path,
                "visit_count": 1, # Placeholder, actual count logic might be needed
                "type": best_match_type # Add the type of location found
            }
            return loc_obj, 0.9 # High confidence for a direct match from geo data

    # Fallback to old_location hints if no new match found
    if old_location and old_location.get("canonical"):
        return old_location, 0.6 # Reduced confidence for old/unverified hint

    return None, 0.0

# -------------------------
# Confidence + Review (base)
# -------------------------

def compute_confidence_base(
    c_event: float,
    c_location: float,
    c_schemes: float,
    c_topics: float,
    c_targets: float,
    c_communities: float,
    c_orgs: float,
    event_type: str,
    location_obj: Optional[Dict[str, Any]],
    schemes: List[str],
    word_buckets: List[str],
    target_groups: List[str],
    communities: List[str],
    organizations: List[str],
) -> float:
    """
    V4-style base confidence (बिना rescue bonus)
    """
    good_event = event_type != "अन्य"
    good_loc = bool(location_obj and location_obj.get("canonical"))

    base = 0.4
    if good_event:
        base += 0.25
    if good_loc:
        base += 0.2
    if schemes:
        base += 0.05
    if word_buckets:
        base += 0.05
    if target_groups or communities:
        base += 0.05
    if organizations:
        base += 0.05

    avg_signals = (c_event + c_location + c_schemes + c_topics + c_targets + c_communities + c_orgs) / 7.0
    score = max(base, base * 0.7 + avg_signals * 0.3)
    score = min(0.99, max(0.0, score))
    return round(score, 3)


def decide_review_status(conf: float) -> Tuple[str, bool]:
    if conf >= 0.9:
        return "auto_approved", False
    if conf >= 0.75:
        return "pending", False
    return "pending", True

# -------------------------
# “अन्य” Rescue – helper detectors
# -------------------------

def _looks_like_sports_tweet(text_l: str) -> bool:
    SPORTS_KW = [
        "मैच", "जीत", "विजय", "टीम इंडिया",
        "world cup", "वर्ल्ड कप", "टी20", "t20",
        "ipl", "वनडे", "odi"
    ]
    EMOJIS = [" 🏏", "🏆", "🇮🇳"]
    return any(kw.lower() in text_l for kw in SPORTS_KW) or any(e in text_l for e in EMOJIS)


def _looks_like_policy_statement(text_l: str, pd4: Dict[str, Any]) -> bool:


    POLICY_KW = [


        "सबका साथ सबका विकास",


        "सबका साथ-सबका विकास", # Added hyphenated version


        "नया भारत",


        "विकसित भारत",


        "प्रधानमंत्री", "प्रधान मंत्री",


        "देशवासियों", "नागरिकों",


        "युवा शक्ति",


        "विकास के पथ पर", # Added new phrase


        "विकास की नई", # Added new phrase


        "आत्मनिर्भर", # Added new phrase


    ]


    has_policy_kw = any(kw.lower() in text_l for kw in POLICY_KW)


    EVENT_HINTS = ["बैठक", "रैली", "उद्घाटन", "निरीक्षण", "जनदर्शन"]


    has_hard_event = any(kw in text_l for kw in EVENT_HINTS)


    return has_policy_kw and not has_hard_event


def _looks_like_security_context(text_l: str) -> bool:
    SECURITY_KW = ["माओवादी", "माओवाद", "नक्सल", "नक्सलवाद", "आतंक", "आतंकवाद", "उग्रवाद"]
    return any(kw in text_l for kw in SECURITY_KW)


def _looks_like_pure_greetings(text_l: str, pd4: Dict[str, Any]) -> bool:
    GREET_KW = ["शुभकामन", "बधाई", "मुबारक", "शुभेच्छा", "best wishes", "congratulations"]
    FESTIVAL_HINTS = ["दीपावली", "होली", "रक्षा बंधन", "स्वतंत्रता दिवस", "गणतंत्र दिवस"]
    has_greet = any(kw.lower() in text_l for kw in GREET_KW)
    has_fest = any(kw.lower() in text_l for kw in FESTIVAL_HINTS)
    EVENT_HINTS = ["बैठक", "रैली", "उद्घाटन", "निरीक्षण", "जनदर्शन"]
    has_hard_event = any(kw in text_l for kw in EVENT_HINTS)
    return (has_greet or has_fest) and not has_hard_event


def _looks_like_digital_only(text_l: str, pd4: Dict[str, Any]) -> bool:
    loc = pd4.get("location") or {}
    has_loc = bool(loc.get("canonical"))
    DIGITAL_KW = ["online", "live", "जुड़ें", "join us live", "link in bio"]
    EVENT_HINTS = ["बैठक", "रैली", "उद्घाटन", "निरीक्षण", "जनदर्शन"]
    has_digital_kw = any(kw.lower() in text_l for kw in DIGITAL_KW)
    has_hard_event = any(kw in text_l for kw in EVENT_HINTS)
    return (not has_loc) and has_digital_kw and not has_hard_event


def _guess_fallback_content_mode(text_l: str, pd4: Dict[str, Any]) -> str:
    EVENT_HINTS = ["बैठक", "रैली", "उद्घाटन", "निरीक्षण", "जनदर्शन"]
    loc = pd4.get("location") or {}
    has_loc = bool(loc.get("canonical"))
    if has_loc and any(kw in text_l for kw in EVENT_HINTS):
        return "मैदान-स्तर कार्यक्रम"
    return "डिजिटल / सोशल-मीडिया पोस्ट"

# -------------------------
# “अन्य” Rescue core
# -------------------------

def rescue_other_events_v5(text: str, base_pd: Dict[str, Any]) -> Dict[str, Any]:
    """
    सिर्फ़ event_type/content_mode/conf bonus की responsibility यहाँ है।
    बाकी fields (location, buckets, groups...) base_pd से ही आते हैं।
    """
    text_l = text.lower()
    original_event = base_pd.get("event_type")
    pd5_extra: Dict[str, Any] = {
        "event_type": original_event,
        "content_mode": None,
        "is_other_original": (original_event == "अन्य"),
        "is_rescued_other": False,
        "rescue_tag": None,
        "rescue_confidence_bonus": 0.0,
    }

    # 1) Sports / Match
    if _looks_like_sports_tweet(text_l):
        pd5_extra["content_mode"] = "खेल / उपलब्धि पर प्रतिक्रिया"
        if original_event == "अन्य":
            pd5_extra["event_type"] = "शुभकामना / बधाई"
            pd5_extra["is_rescued_other"] = True
            pd5_extra["rescue_tag"] = "sports"
            pd5_extra["rescue_confidence_bonus"] = 0.15
        return pd5_extra

    # 2) Policy / Narrative
    if _looks_like_policy_statement(text_l, base_pd):
        pd5_extra["content_mode"] = "नीति / वक्तव्य"
        has_scheme = bool(base_pd.get("schemes_mentioned"))
        if original_event == "अन्य":
            if has_scheme:
                pd5_extra["event_type"] = "योजना घोषणा"
                pd5_extra["rescue_tag"] = "policy_scheme"
                pd5_extra["rescue_confidence_bonus"] = 0.12
            else:
                # यहाँ taxonomy stable रखना है, इसलिए event_type "अन्य" रहने दे सकते हैं
                pd5_extra["event_type"] = "अन्य"
                pd5_extra["rescue_tag"] = "policy_statement"
                pd5_extra["rescue_confidence_bonus"] = 0.06
            pd5_extra["is_rescued_other"] = True
        return pd5_extra

    # 3) Security / Naxal / Terror
    if _looks_like_security_context(text_l):
        pd5_extra["content_mode"] = "नीति / वक्तव्य"
        if original_event == "अन्य":
            pd5_extra["event_type"] = "अन्य"
            pd5_extra["is_rescued_other"] = True
            pd5_extra["rescue_tag"] = "security"
            pd5_extra["rescue_confidence_bonus"] = 0.05
        return pd5_extra

    # 4) Pure greetings / festival
    if _looks_like_pure_greetings(text_l, base_pd):
        pd5_extra["content_mode"] = "सामान्य शुभकामनाएँ / पर्व"
        if original_event == "अन्य":
            pd5_extra["event_type"] = "शुभकामना / बधाई"
            pd5_extra["is_rescued_other"] = True
            pd5_extra["rescue_tag"] = "greetings"
            pd5_extra["rescue_confidence_bonus"] = 0.10
        return pd5_extra

    # 5) Digital-only social posts
    if _looks_like_digital_only(text_l, base_pd):
        pd5_extra["content_mode"] = "डिजिटल / सोशल-मीडिया पोस्ट"
        if original_event == "अन्य":
            pd5_extra["is_rescued_other"] = True
            pd5_extra["rescue_tag"] = "digital"
            pd5_extra["rescue_confidence_bonus"] = 0.04
        return pd5_extra

    # Fallback – अनुमानित content_mode
    pd5_extra["content_mode"] = _guess_fallback_content_mode(text_l, base_pd)
    return pd5_extra


def compute_confidence_v5(base_conf: float, pd5_extra: Dict[str, Any]) -> float:
    bonus = pd5_extra.get("rescue_confidence_bonus", 0.0)
    event_type = pd5_extra.get("event_type")
    content_mode = pd5_extra.get("content_mode")

    # अगर event_type अब भी "अन्य" है लेकिन content_mode साफ़ है (नीति/डिजिटल),
    # तो हल्का normalization बोनस।
    if event_type == "अन्य" and content_mode in ("नीति / वक्तव्य", "डिजिटल / सोशल-मीडिया पोस्ट"):
        bonus += 0.03

    conf = min(0.99, max(0.0, base_conf + bonus))
    return round(conf, 3)

# -------------------------
# Base parsing (V4 logic) – used inside V5
# -------------------------

def base_parse_v4(text: str, created_at: Optional[str], old_pd: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    V4-style base parse – event/location/groups/... + base_confidence.
    """
    old_loc = old_pd.get("location") or {}

    schemes, c_schemes = extract_schemes(text)
    word_buckets, c_topics = make_word_buckets(text)
    target_groups, c_targets = extract_target_groups(text)
    communities, c_communities = extract_communities(text)
    organizations, c_orgs = extract_orgs(text)

    old_event_hi = old_pd.get("event_type")
    event_type, c_event = normalize_event_type_base(old_event_hi, text, schemes)
    location_obj, c_location = normalize_location(text, old_loc)

    event_date = created_at[:10] if created_at else None

    people_mentioned = old_pd.get("people_mentioned") or []
    people_canonical = people_mentioned[:]

    validation_errors: List[str] = []
    if not event_type:
        validation_errors.append("ईवेंट प्रकार नहीं मिल सका")
    if not location_obj:
        validation_errors.append("स्थान नहीं मिल सका")

    base_confidence = compute_confidence_base(
        c_event=c_event,
        c_location=c_location,
        c_schemes=c_schemes,
        c_topics=c_topics,
        c_targets=c_targets,
        c_communities=c_communities,
        c_orgs=c_orgs,
        event_type=event_type,
        location_obj=location_obj,
        schemes=schemes,
        word_buckets=word_buckets,
        target_groups=target_groups,
        communities=communities,
        organizations=organizations,
    )

    base_pd = {
        "event_type": event_type,
        "event_type_secondary": [],
        "event_date": event_date,
        "location": location_obj,
        "people_mentioned": people_mentioned,
        "people_canonical": people_canonical,
        "word_buckets": word_buckets,
        "target_groups": target_groups,
        "communities": communities,
        "organizations": organizations,
        "schemes_mentioned": schemes,
        "hierarchy_path": location_obj.get("hierarchy_path") if location_obj else [],
        "visit_count": location_obj.get("visit_count") if location_obj else 0,
        "vector_embedding_id": (
            f"faiss://{location_obj.get('canonical_key')}"
            if location_obj and location_obj.get("canonical_key")
            else None
        ),
        "confidence": base_confidence,
        "review_status": "",   # later set
        "needs_review": True,  # later set
    }

    meta_v4 = {
        "model_used": "rule+dictionary-hindi-v4-base",
        "processing_time_ms": 0,
        "faiss_round_trips": 0,
        "validation_errors": validation_errors,
        "c_event": c_event,
        "c_location": c_location,
        "c_schemes": c_schemes,
        "c_topics": c_topics,
        "c_targets": c_targets,
        "c_communities": c_communities,
        "c_orgs": c_orgs,
    }

    return base_pd, meta_v4

# -------------------------
# Full V5 parsing per tweet
# -------------------------

def parse_tweet_v5(record: Dict[str, Any]) -> Dict[str, Any]:
    tweet_id = record.get("tweet_id")
    created_at = record.get("created_at")
    text = record.get("raw_text") or record.get("text") or ""

    # पुराने parsed data अगर हों तो hints के तौर पर लो
    old_pd = (
        record.get("parsed_data_v4")
        or record.get("parsed_data_v3")
        or record.get("parsed_data_v2")
        or record.get("parsed_data")
        or {}
    )

    # 1) Base V4-style parse
    base_pd, meta_v4 = base_parse_v4(text, created_at, old_pd)

    # 2) Rescue / content_mode layer (focus on "अन्य")
    pd5_extra = rescue_other_events_v5(text, base_pd)

    # 3) Confidence V5
    base_conf = base_pd.get("confidence", 0.0)
    final_conf = compute_confidence_v5(base_conf, pd5_extra)

    review_status, needs_review = decide_review_status(final_conf)

    # 4) Merge into final parsed_data_v5
    parsed_data_v5 = {
        **base_pd,
        "event_type": pd5_extra["event_type"],
        "confidence": final_conf,
        "review_status": review_status,
        "needs_review": needs_review,
        "content_mode": pd5_extra["content_mode"],
        "is_other_original": pd5_extra["is_other_original"],
        "is_rescued_other": pd5_extra["is_rescued_other"],
        "rescue_tag": pd5_extra["rescue_tag"],
        "rescue_confidence_bonus": pd5_extra["rescue_confidence_bonus"],
    }

    metadata_v5 = {
        "model_used": "rule+dictionary-hindi-v5",
        "processing_time_ms": 0,
        "faiss_round_trips": 0,
        "validation_errors": meta_v4.get("validation_errors", []),
        "base_confidence_v4": base_conf,
        "rescue_info": {
            "is_other_original": pd5_extra["is_other_original"],
            "is_rescued_other": pd5_extra["is_rescued_other"],
            "rescue_tag": pd5_extra["rescue_tag"],
            "rescue_confidence_bonus": pd5_extra["rescue_confidence_bonus"],
        },
    }

    # Output record – पुराने parsed_data_x को preserve करते हुए
    out: Dict[str, Any] = {
        "tweet_id": tweet_id,
        "created_at": created_at,
        "raw_text": text,
        "parsed_data_v5": parsed_data_v5,
        "metadata_v5": metadata_v5,
    }
    # पुराने parsed_data_x अगर हों तो साथ में रख दो
    for key in ("parsed_data_v4", "parsed_data_v3", "parsed_data_v2", "parsed_data"):
        if key in record:
            out[key] = record[key]
    for key in ("metadata_v4", "metadata_v3", "metadata_v2"):
        if key in record:
            out[key] = record[key]

    return out

# -------------------------
# File-level driver
# -------------------------

def reparse_file_v5(input_path: Path, output_path: Path) -> None:
    total = 0
    high_conf = mid_conf = low_conf = 0
    event_counter: Counter = Counter()
    loc_cov = scheme_cov = bucket_cov = tg_cov = comm_cov = 0
    other_original = rescued_other = hard_other = 0

    with input_path.open("r", encoding="utf-8") as fin, \
         output_path.open("w", encoding="utf-8") as fout:

        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            total += 1
            new_rec = parse_tweet_v5(rec)
            pd5 = new_rec["parsed_data_v5"]

            conf = pd5.get("confidence", 0.0)
            if conf >= 0.9:
                high_conf += 1
            elif conf >= 0.7:
                mid_conf += 1
            else:
                low_conf += 1

            et = pd5.get("event_type") or ""
            event_counter[et] += 1

            if pd5.get("location") and pd5["location"].get("canonical"):
                loc_cov += 1
            if pd5.get("schemes_mentioned"):
                scheme_cov += 1
            if pd5.get("word_buckets"):
                bucket_cov += 1
            if pd5.get("target_groups"):
                tg_cov += 1
            if pd5.get("communities"):
                comm_cov += 1

            if pd5.get("is_other_original"):
                other_original += 1
                if pd5.get("is_rescued_other"):
                    rescued_other += 1
                else:
                    hard_other += 1

            fout.write(json.dumps(new_rec, ensure_ascii=False) + "\n")

    # Summary print
    print("✅ V5 Re-parsing complete (single-pass robust parser)")
    print(f"  कुल ट्वीट: {total}")
    if total:
        print(f"  High confidence (>= 0.9): {high_conf} ({high_conf*100/total:.2f}%)")
        print(f"  Medium confidence (0.7–0.9): {mid_conf} ({mid_conf*100/total:.2f}%)")
        print(f"  Low confidence (< 0.7): {low_conf} ({low_conf*100/total:.2f}%)")
        print()
        print(f"  Location coverage (canonical मौजूद): {loc_cov} ({loc_cov*100/total:.2f}%)")
        print(f"  Schemes detected: {scheme_cov} ({scheme_cov*100/total:.2f}%)")
        print(f"  Word buckets non-empty: {bucket_cov} ({bucket_cov*100/total:.2f}%)")
        print(f"  Target groups non-empty: {tg_cov} ({tg_cov*100/total:.2f}%)")
        print(f"  Communities non-empty: {comm_cov} ({comm_cov*100/total:.2f}%)")
        print()
        print(f"  Original 'अन्य' tweets: {other_original}")
        print(f"    Rescued Others: {rescued_other}")
        print(f"    Hard Others (no pattern): {hard_other}")
        print()
        print("  Event type distribution (top):")
        for label, count in event_counter.most_common(15):
            if not label:
                continue
            print(f"    {label}: {count} ({count*100/total:.2f}%)")

# -------------------------
# Entrypoint
# -------------------------

def main(argv: List[str]) -> None:
    # Load comprehensive geo data once
    load_geo_data_v5()

    if len(argv) >= 2:
        input_path = Path(argv[1])
    else:
        input_path = DEFAULT_INPUT
    if len(argv) >= 3:
        output_path = Path(argv[2])
    else:
        output_path = DEFAULT_OUTPUT

    if not input_path.exists():
        print(f"⚠️ इनपुट फ़ाइल नहीं मिली: {input_path}")
        sys.exit(1)

    print(f"▶️ Input:  {input_path}")
    print(f"▶️ Output: {output_path}")
    reparse_file_v5(input_path, output_path)


if __name__ == "__main__":
    main(sys.argv)
