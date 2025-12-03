import json
from datetime import datetime
from pathlib import Path
import os
import sys
import time
from typing import List, Dict, Tuple, Optional

# Add the project root directory to sys.path
# This allows Python to find 'KnowledgeBank' as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import orchestrator using its full package path
from KnowledgeBank.source_code.orchestrator import ParsingOrchestrator
from KnowledgeBank.source_code.normalization import fold_nukta, translit_basic, expand_hinglish_variants # Reusing for alias generation


# --- Event Type Translation Logic ---
# Global event type mapping (English simplified from orchestrator to canonical Hindi)
GLOBAL_EVENT_TYPE_MAPPING = {
    "inauguration": "उद्घाटन",
    "rally": "रैली",
    "meeting": "बैठक",
    "inspection": "निरीक्षण",
    "scheme_announcement": "योजना घोषणा",
    "samaj_function": "धार्मिक / सांस्कृतिक कार्यक्रम", # Closest match based on context
    "festival_event": "धार्मिक / सांस्कृतिक कार्यक्रम",
    "constituent_engagement": "जनसम्पर्क / जनदर्शन",
    "relief": "आपदा राहत",
    "protest": "आंदोलन / धरना / विरोध", # Added from event_types.json
    "election_campaign": "चुनाव प्रचार", # Added from event_types.json
    "other": "अन्य",
    "government_program": "योजना घोषणा", # As per user instruction
    "policy_announcement": "योजना घोषणा", # As per user instruction
    "community_meeting": "बैठक", # Default as per user instruction
    "political_rally": "रैली", # As per user instruction
    "infrastructure_inauguration": "उद्घाटन", # As per user instruction
    "jayanti": "शुभकामना / बधाई", # As per user instruction, primary
    "general": "अन्य", # As per user instruction, fallback from general
}

def translate_event_type(orchestrator_event_type: str, raw_text: str) -> Tuple[str, List[str]]:
    """
    Translates orchestrator's event type to canonical Hindi labels and applies rules for secondary tags.
    """
    primary_event_type = GLOBAL_EVENT_TYPE_MAPPING.get(orchestrator_event_type, "अन्य")
    secondary_event_types = []

    # Apply specific rules for old categories based on new instructions
    if orchestrator_event_type == "general":
        lower_text = raw_text.lower()
        if "शुभकामना" in lower_text or "बधाई" in lower_text:
            primary_event_type = "शुभकामना / बधाई"
        elif "धर्म" in lower_text or "त्योहार" in lower_text or "पूजा" in lower_text or "कार्यक्रम" in lower_text:
            primary_event_type = "धार्मिक / सांस्कृतिक कार्यक्रम"
        else:
            primary_event_type = "अन्य"
    elif orchestrator_event_type == "government_program":
        lower_text = raw_text.lower()
        if "सभा" in lower_text or "मंच" in lower_text or "लाभार्थी" in lower_text:
            primary_event_type = "योजना घोषणा"
            secondary_event_types.append("जनसम्पर्क / जनदर्शन")
        else:
            primary_event_type = "योजना घोषणा" # Default for government_program
    elif orchestrator_event_type == "community_meeting":
        lower_text = raw_text.lower()
        if "closed room" in lower_text or "office" in lower_text or "प्रशासन" in lower_text:
            primary_event_type = "प्रशासनिक समीक्षा बैठक"
        else: # जनता / समाज / प्रतिनिधि
            primary_event_type = "बैठक"
    elif orchestrator_event_type == "jayanti":
        lower_text = raw_text.lower()
        if "आयोजन" in lower_text or "संबोधन" in lower_text:
            primary_event_type = "धार्मिक / सांस्कृतिक कार्यक्रम"
        else:
            primary_event_type = "शुभकामना / बधाई"
            secondary_event_types.append("जयंती संदेश") # As secondary

    # Ensure 'general' is never the final event_type
    if primary_event_type == "general":
        primary_event_type = "अन्य"
    
    return primary_event_type, secondary_event_types


# --- Keyword-based Entity Extraction ---
import re

GLOBAL_WORD_BUCKETS_KEYWORDS = {
    "सकारात्मक": ["विकास", "समृद्धि", "प्रगति", "खुशहाली", "बेहतर", "नवाचार", "आत्मनिर्भर", "कल्याण", "उत्सव", "सफलता"],
    "नकारात्मक": ["समस्या", "समस्याएँ", "शिकायत", "मुश्किल", "चुनौती", "बाधा", "परेशानी", "संकट", "विफलता", "आंदोलन", "विरोध", "हानि", "पीड़ा"],
    "सरकारी_कार्य": ["योजना", "कार्यक्रम", "परियोजना", "नीति", "अधिनियम", "शासन", "प्रशासन", "मंत्रालय", "विभाग", "बैठक", "निरीक्षण", "उद्घाटन", "लोकार्पण", "कार्य"],
    "जन_सहभागिता": ["जनता", "ग्रामीण", "लाभार्थी", "नागरिक", "समाज", "समुदाय", "जनभागीदारी", "संवाद", "जनदर्शन"]
}

GLOBAL_TARGET_GROUPS_KEYWORDS = {
    "किसान": ["किसान", "कृषक", "अन्नदाता"],
    "युवा": ["युवा", "नौजवान", "छात्र", "विद्यार्थी"],
    "महिला": ["महिला", "नारी", "बहन", "महतारी"],
    "आदिवासी": ["आदिवासी", "जनजाति", "वनवासी", "अनुसूचित जनजाति"],
    "दलित": ["दलित", "अनुसूचित जाति", "एससी"],
    "पिछड़ा वर्ग": ["पिछड़ा वर्ग", "ओबीसी"],
    "गरीब": ["गरीब", "निर्धन", "वंचित"],
    "व्यापारी": ["व्यापारी", "कारोबारी"],
    "कर्मचारी": ["कर्मचारी", "सेवक"],
    "पेंशनभोगी": ["पेंशनभोगी"]
}

GLOBAL_COMMUNITIES_KEYWORDS = {
    "हिन्दू": ["हिन्दू", "सनातन"],
    "मुस्लिम": ["मुस्लिम", "मुसलमान"],
    "सिख": ["सिख"],
    "ईसाई": ["ईसाई"],
    "जैन": ["जैन"],
    "बौद्ध": ["बौद्ध"],
    "अन्य_समुदाय": ["समाज", "समुदाय", "वर्ग"] # General terms for communities
}

GLOBAL_SCHEMES_KEYWORDS = {
    "आयुष्मान भारत": ["आयुष्मान भारत", "आयुष्मान योजना", "प्रधानमंत्री जन आरोग्य योजना"],
    "प्रधानमंत्री आवास योजना": ["प्रधानमंत्री आवास योजना", "पीएम आवास योजना", "आवास योजना"],
    "जल जीवन मिशन": ["जल जीवन मिशन", "हर घर जल", "नल जल योजना"],
    "प्रधानमंत्री किसान सम्मान निधि": ["प्रधानमंत्री किसान सम्मान निधि", "पीएम किसान"],
    "मनरेगा": ["मनरेगा", "महात्मा गांधी नरेगा"],
    "मुख्यमंत्री": ["मुख्यमंत्री योजना", "सीएम योजना", "मुख्यमंत्री जन सेवा"], # Generic for CM schemes
    "प्रधानमंत्री": ["प्रधानमंत्री योजना", "पीएम योजना", "प्रधानमंत्री जनधन"], # Generic for PM schemes
    "राशन": ["राशन योजना", "खाद्य सुरक्षा"],
    "बिजली": ["बिजली योजना", "सौर सुजला योजना"],
    "शिक्षा": ["शिक्षा योजना", "सरस्वती साइकिल योजना"],
    "स्वास्थ्य": ["स्वास्थ्य योजना", "संजीवनी एक्सप्रेस"]
}

def extract_entities(text: str, keywords_dict: Dict[str, List[str]]) -> List[str]:
    found_entities = set()
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            if re.search(r'(?<!\S)' + re.escape(keyword) + r'(?!\S)', text, re.IGNORECASE | re.UNICODE):
                found_entities.add(category)
    return sorted(list(found_entities))

def extract_word_buckets(text: str) -> List[str]:
    found_buckets = set()
    for category, keywords in GLOBAL_WORD_BUCKETS_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'(?<!\S)' + re.escape(keyword) + r'(?!\S)', text, re.IGNORECASE | re.UNICODE):
                found_buckets.add(category)
    return sorted(list(found_buckets))

def extract_target_groups(text: str) -> List[str]:
    found_groups = set()
    for category, keywords in GLOBAL_TARGET_GROUPS_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'(?<!\S)' + re.escape(keyword) + r'(?!\S)', text, re.IGNORECASE | re.UNICODE):
                found_groups.add(category)
    return sorted(list(found_groups))

def extract_communities(text: str) -> List[str]:
    found_communities = set()
    for category, keywords in GLOBAL_COMMUNITIES_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'(?<!\S)' + re.escape(keyword) + r'(?!\S)', text, re.IGNORECASE | re.UNICODE):
                found_communities.add(category)
    return sorted(list(found_communities))

def extract_schemes_mentioned(text: str) -> List[str]:
    found_schemes = set()
    for scheme_name, keywords in GLOBAL_SCHEMES_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'(?<!\S)' + re.escape(keyword) + r'(?!\S)', text, re.IGNORECASE | re.UNICODE):
                found_schemes.add(scheme_name)
    return sorted(list(found_schemes))

# --- Location Hierarchy and Aliases Logic ---
GLOBAL_GEO_HIERARCHY = {}
GLOBAL_LOCATION_LOOKUP = {} # Stores all levels of hierarchy
GLOBAL_ALIAS_TO_CANONICAL = {} # Maps all aliases to canonical Hindi name and type

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
    folded = fold_nukta(name).lower().strip()
    variants.add(folded)
    
    # Transliterated
    if any('\u0900' <= c <= '\u097F' for c in name):  # Contains Hindi
        translit = translit_basic(folded).lower().strip()
        variants.add(translit)
        
        # Hinglish variants
        hinglish = expand_hinglish_variants(translit)
        variants.update(v.lower().strip() for v in hinglish)
    
    # Remove empty strings
    variants.discard('')
    
    return list(variants)

def load_geo_data():
    global GLOBAL_GEO_HIERARCHY, GLOBAL_LOCATION_LOOKUP, GLOBAL_ALIAS_TO_CANONICAL
    geo_file = Path('KnowledgeBank/geo-data/chhattisgarh_complete_geography.json')
    with open(geo_file, 'r', encoding='utf-8') as f:
        GLOBAL_GEO_HIERARCHY = json.load(f)
    
    GLOBAL_LOCATION_LOOKUP, GLOBAL_ALIAS_TO_CANONICAL = build_location_lookup_tables(GLOBAL_GEO_HIERARCHY)

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
        if name_english:
            full_aliases.update(_generate_variants(name_english))
        
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
        district_name_english = translit_basic(district_name_hindi) # Simplified English
        canonical_key_district = f"{state_code}_{district_name_hindi.replace(' ','_')}"
        
        add_location_to_lookups(lookup, alias_to_canonical, district_name_hindi, district_name_english, "district", 
                                [state_name_hindi, f"{district_name_hindi} जिला"], canonical_key_district, district)
        
        for ac in district.get('acs', []):
            ac_name_hindi = ac.get('name', '')
            ac_name_english = translit_basic(ac_name_hindi)
            canonical_key_ac = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}"

            add_location_to_lookups(lookup, alias_to_canonical, ac_name_hindi, ac_name_english, "assembly", 
                                    [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा"], canonical_key_ac, ac)
            
            for block in ac.get('blocks', []):
                block_name_hindi = block.get('name', '')
                block_name_english = translit_basic(block_name_hindi)
                canonical_key_block = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}"

                add_location_to_lookups(lookup, alias_to_canonical, block_name_hindi, block_name_english, "block", 
                                        [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड"], canonical_key_block, block)
                
                for gp in block.get('gps', []):
                    gp_name_hindi = gp.get('name', '')
                    gp_name_english = translit_basic(gp_name_hindi)
                    canonical_key_gp = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}_{gp_name_hindi.replace(' ','_')}"

                    add_location_to_lookups(lookup, alias_to_canonical, gp_name_hindi, gp_name_english, "gp", 
                                            [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड", f"{gp_name_hindi} ग्राम पंचायत"], canonical_key_gp, gp)
                    
                    for village in gp.get('villages', []):
                        village_name_hindi = village.get('name', '')
                        village_name_english = translit_basic(village_name_hindi)
                        canonical_key_village = f"{state_code}_{district_name_hindi.replace(' ','_')}_{ac_name_hindi.replace(' ','_')}_{block_name_hindi.replace(' ','_')}_{gp_name_hindi.replace(' ','_')}_{village_name_hindi.replace(' ','_')}"

                        add_location_to_lookups(lookup, alias_to_canonical, village_name_hindi, village_name_english, "village", 
                                                [state_name_hindi, f"{district_name_hindi} जिला", f"{ac_name_hindi} विधानसभा", f"{block_name_hindi} विकासखंड", f"{gp_name_hindi} ग्राम पंचायत", f"{village_name_hindi} गाँव"], canonical_key_village, village)
    
    # Add cities from location_matcher's hardcoded list
    cities_from_matcher = ParsingOrchestrator().location_matcher.cities # Access hardcoded cities
    for city in cities_from_matcher:
        city_name_hindi = city.get('name', '')
        city_name_english = city.get('name_en', '')
        # Only add if not already covered by a more specific geo-entity
        if city_name_hindi and city_name_hindi not in lookup:
            canonical_key_city = f"{state_code}_{city_name_hindi.replace(' ','_')}_ULB"
            # Assuming ULB is equivalent to City for now, and doesn't have further hierarchy
            add_location_to_lookups(lookup, alias_to_canonical, city_name_hindi, city_name_english, "ulb", 
                                    [state_name_hindi, f"{city_name_hindi} नगर निगम"], canonical_key_city, city)

    return lookup, alias_to_canonical

def get_location_hierarchy_and_aliases(matched_location: Dict) -> Tuple[Dict, List[str], List[str]]:
    """
    Retrieves the full hierarchy, canonical form, and aliases for a given matched location,
    including deriving higher-level administrative boundaries for cities/ULBs.
    """
    structured_location = {
        "district": "",
        "assembly": "",
        "block": "",
        "gp": "",
        "village": "",
        "ulb": "",
        "zone": "",
        "ward": "",
        "canonical_key": "",
        "aliases": []
    }
    hierarchy_path = []
    all_aliases = set()

    canonical_name_hindi = matched_location.get('name', '')
    location_type = matched_location.get('type', '')

    if not canonical_name_hindi:
        return structured_location, hierarchy_path, []

    # First, try to find the location directly in our global lookup
    record = GLOBAL_LOCATION_LOOKUP.get(canonical_name_hindi)

    if record:
        structured_location[record['type']] = record['name_hindi']
        hierarchy_path = record['hierarchy_list']
        structured_location['canonical_key'] = record['canonical_key']
        all_aliases.update(record['aliases'])

        # Populate structured_location fields based on type
        if record['type'] == 'district':
            structured_location['district'] = record['name_hindi']
            # Attempt to find parent state from hierarchy_path
            if len(hierarchy_path) > 0:
                # The first element in hierarchy_path for a district should be the state
                state_name = hierarchy_path[0]
                structured_location['hierarchy_path'] = [state_name, f"{record['name_hindi']} जिला"]
            else:
                structured_location['hierarchy_path'] = [f"{record['name_hindi']} जिला"]


        elif record['type'] == 'assembly':
            structured_location['assembly'] = record['name_hindi']
            # From hierarchy_path, try to get district and state
            if len(hierarchy_path) >= 2:
                state_name = hierarchy_path[0]
                district_name = hierarchy_path[1].replace(" जिला", "")
                structured_location['district'] = district_name
                structured_location['hierarchy_path'] = [state_name, f"{district_name} जिला", f"{record['name_hindi']} विधानसभा"]

        elif record['type'] == 'block':
            structured_location['block'] = record['name_hindi']
            if len(hierarchy_path) >= 3:
                state_name = hierarchy_path[0]
                district_name = hierarchy_path[1].replace(" जिला", "")
                ac_name = hierarchy_path[2].replace(" विधानसभा", "")
                structured_location['district'] = district_name
                structured_location['assembly'] = ac_name
                structured_location['hierarchy_path'] = [state_name, f"{district_name} जिला", f"{ac_name} विधानसभा", f"{record['name_hindi']} विकासखंड"]

        elif record['type'] == 'gp':
            structured_location['gp'] = record['name_hindi']
            if len(hierarchy_path) >= 4:
                state_name = hierarchy_path[0]
                district_name = hierarchy_path[1].replace(" जिला", "")
                ac_name = hierarchy_path[2].replace(" विधानसभा", "")
                block_name = hierarchy_path[3].replace(" विकासखंड", "")
                structured_location['district'] = district_name
                structured_location['assembly'] = ac_name
                structured_location['block'] = block_name
                structured_location['hierarchy_path'] = [state_name, f"{district_name} जिला", f"{ac_name} विधानसभा", f"{block_name} विकासखंड", f"{record['name_hindi']} ग्राम पंचायत"]

        elif record['type'] == 'village':
            structured_location['village'] = record['name_hindi']
            if len(hierarchy_path) >= 5:
                state_name = hierarchy_path[0]
                district_name = hierarchy_path[1].replace(" जिला", "")
                ac_name = hierarchy_path[2].replace(" विधानसभा", "")
                block_name = hierarchy_path[3].replace(" विकासखंड", "")
                gp_name = hierarchy_path[4].replace(" ग्राम पंचायत", "")
                structured_location['district'] = district_name
                structured_location['assembly'] = ac_name
                structured_location['block'] = block_name
                structured_location['gp'] = gp_name
                structured_location['hierarchy_path'] = [state_name, f"{district_name} जिला", f"{ac_name} विधानसभा", f"{block_name} विकासखंड", f"{gp_name} ग्राम पंचायत", f"{record['name_hindi']} गाँव"]

        elif record['type'] == 'ulb': # This is likely a city that was directly matched
            structured_location['ulb'] = record['name_hindi']
            # Now, try to find its district from the GLOBAL_GEO_HIERARCHY
            found_district = None
            for district_entry in GLOBAL_GEO_HIERARCHY.get('districts', []):
                for ulb_entry in district_entry.get('ulbs', []): # Assuming ULBs are nested under districts
                    if ulb_entry.get('name') == canonical_name_hindi:
                        found_district = district_entry
                        break
                if found_district:
                    break
            
            if found_district:
                structured_location['district'] = found_district['name']
                # Reconstruct hierarchy_path more accurately for ULB
                hierarchy_path = [GLOBAL_GEO_HIERARCHY['state'], f"{found_district['name']} जिला", f"{canonical_name_hindi} नगर निगम"]
                structured_location['hierarchy_path'] = hierarchy_path
        
    else: # If not found directly in lookup (e.g., location_matcher returns a city that wasn't explicitly added as ULB)
        # Attempt to find district, AC, block for the matched city from raw geo data
        for district_entry in GLOBAL_GEO_HIERARCHY.get('districts', []):
            district_name = district_entry.get('name', '')
            
            # Check if the matched_location is a district itself
            if canonical_name_hindi == district_name:
                structured_location['district'] = district_name
                hierarchy_path = [GLOBAL_GEO_HIERARCHY['state'], f"{district_name} जिला"]
                structured_location['canonical_key'] = f"{GLOBAL_GEO_HIERARCHY['state_code']}_{district_name.replace(' ','_')}"
                all_aliases.update(_generate_variants(district_name))
                break

            # Check within ULBs of the district
            for ulb_entry in district_entry.get('ulbs', []):
                if ulb_entry.get('name') == canonical_name_hindi:
                    structured_location['ulb'] = canonical_name_hindi
                    structured_location['district'] = district_name
                    hierarchy_path = [GLOBAL_GEO_HIERARCHY['state'], f"{district_name} जिला", f"{canonical_name_hindi} नगर निगम"]
                    structured_location['canonical_key'] = f"{GLOBAL_GEO_HIERARCHY['state_code']}_{district_name.replace(' ','_')}_{canonical_name_hindi.replace(' ','_')}_ULB"
                    all_aliases.update(_generate_variants(canonical_name_hindi))
                    all_aliases.update(_generate_variants(district_name))
                    break
            if structured_location['district']:
                break
            
            # Check within ACs of the district
            for ac_entry in district_entry.get('acs', []):
                ac_name = ac_entry.get('name', '')
                if canonical_name_hindi == ac_name:
                    structured_location['assembly'] = ac_name
                    structured_location['district'] = district_name
                    hierarchy_path = [GLOBAL_GEO_HIERARCHY['state'], f"{district_name} जिला", f"{ac_name} विधानसभा"]
                    structured_location['canonical_key'] = f"{GLOBAL_GEO_HIERARCHY['state_code']}_{district_name.replace(' ','_')}_{ac_name.replace(' ','_')}"
                    all_aliases.update(_generate_variants(ac_name))
                    all_aliases.update(_generate_variants(district_name))
                    break
            if structured_location['district']:
                break

            # Check within Blocks of the district
            for block_entry in ac_entry.get('blocks', []):
                block_name = block_entry.get('name', '')
                if canonical_name_hindi == block_name:
                    structured_location['block'] = block_name
                    structured_location['assembly'] = ac_name
                    structured_location['district'] = district_name
                    hierarchy_path = [GLOBAL_GEO_HIERARCHY['state'], f"{district_name} जिला", f"{ac_name} विधानसभा", f"{block_name} विकासखंड"]
                    structured_location['canonical_key'] = f"{GLOBAL_GEO_HIERARCHY['state_code']}_{district_name.replace(' ','_')}_{ac_name.replace(' ','_')}_{block_name.replace(' ','_')}"
                    all_aliases.update(_generate_variants(block_name))
                    all_aliases.update(_generate_variants(ac_name))
                    all_aliases.update(_generate_variants(district_name))
                    break
            if structured_location['district']:
                break

    # If still no specific location found, default to Chhattisgarh state info
    if not structured_location['canonical_key']:
        cg_state_info = GLOBAL_LOCATION_LOOKUP.get("छत्तीसगढ़")
        if cg_state_info:
            structured_location['canonical_key'] = cg_state_info.get('canonical_key', '')
            hierarchy_path = cg_state_info.get('hierarchy_list', [])
            all_aliases.update(cg_state_info.get('aliases', []))
            
    structured_location['aliases'] = sorted(list(all_aliases))
    structured_location['hierarchy_path'] = hierarchy_path

    return structured_location, hierarchy_path, structured_location['aliases']


def parse_single_tweet_v2(raw_tweet: dict, orchestrator: ParsingOrchestrator) -> dict:
    """
    Parses a single raw tweet according to the new v2 schema.
    """
    tweet_id = raw_tweet['tweet_id']
    text = raw_tweet['text']
    created_at_dt = datetime.fromisoformat(raw_tweet['created_at'].replace('Z', '+00:00'))
    
    start_time = time.time() # Start time for processing_time_ms

    # Initialize new schema fields with defaults
    parsed_data_v2 = {
        "event_type": "अन्य", # Default, will be updated
        "event_type_secondary": [],
        "event_date": created_at_dt.strftime("%Y-%m-%d"), # Default to created_at date
        "location": {
            "district": "", "assembly": "", "block": "", "gp": "", "village": "",
            "ulb": "", "zone": "", "ward": "",
            "canonical_key": "CG", # Default to Chhattisgarh
            "aliases": []
        },
        "people_mentioned": [],
        "people_canonical": [],
        "word_buckets": [],
        "target_groups": [],
        "communities": [],
        "organizations": [],
        "schemes_mentioned": [],
        "hierarchy_path": [],
        "visit_count": 1,
        "vector_embedding_id": "faiss://CG", # Default to Chhattisgarh
        "confidence": 0.0,
        "needs_review": True,
        "review_status": "pending"
    }
    
    # Default location to Chhattisgarh - ensure GLOBAL_LOCATION_LOOKUP is loaded
    cg_state_info = GLOBAL_LOCATION_LOOKUP.get("छत्तीसगढ़")
    if cg_state_info:
        parsed_data_v2['location']['canonical_key'] = cg_state_info.get('canonical_key', '')
        parsed_data_v2['location']['aliases'] = sorted(list(set(cg_state_info.get('aliases', []))))
        parsed_data_v2['hierarchy_path'] = cg_state_info.get('hierarchy_list', [])
        parsed_data_v2['vector_embedding_id'] = f"faiss://{cg_state_info['canonical_key']}"

    metadata_v2 = {
        "processing_time_ms": 0,
        "model_used": "orchestrator_v1",
        "faiss_round_trips": 0, # Placeholder
        "rules_triggered": [],
        "validation_errors": []
    }

    # Initialize individual confidences
    event_type_confidence = 0.0
    location_confidence = 0.5 # Default confidence for fallback location
    word_buckets_confidence = 0.0
    target_groups_confidence = 0.0
    communities_confidence = 0.0
    schemes_mentioned_confidence = 0.0
    
    # Step 1: Orchestrator's initial parsing (will become old_parsed_data)
    old_parsed_data = orchestrator.parse_tweet(
        tweet_id=tweet_id,
        text=text,
        created_at=created_at_dt,
        tweet_date=created_at_dt
    )

    # Populate parsed_data_v2 from old_parsed_data (initial transfer)
    if old_parsed_data:
        # Event Type Translation and Confidence
        orchestrator_event_type = old_parsed_data.get('event_type', 'other')
        primary_et, secondary_ets = translate_event_type(orchestrator_event_type, text)
        parsed_data_v2['event_type'] = primary_et
        parsed_data_v2['event_type_secondary'] = secondary_ets
        event_type_confidence = old_parsed_data.get('event_type_confidence', 0.0)

        # Location Extraction and Hierarchy
        extracted_locations = orchestrator.location_matcher.extract_locations(text) # Use orchestrator's matcher
        if extracted_locations:
            top_location = extracted_locations[0] # Process the highest confidence location
            structured_loc, hierarchy_path, aliases = get_location_hierarchy_and_aliases(top_location)
            parsed_data_v2['location'] = structured_loc
            parsed_data_v2['hierarchy_path'] = hierarchy_path
            parsed_data_v2['location']['aliases'] = sorted(list(set(aliases))) # Ensure unique and sorted aliases
            location_confidence = top_location.get('confidence', 0.0)
            
            # For vector_embedding_id, if a canonical_key exists, use it
            if structured_loc.get('canonical_key'):
                parsed_data_v2['vector_embedding_id'] = f"faiss://{structured_loc['canonical_key']}"
        # No else needed here, as parsed_data_v2['location'] and related fields are already defaulted to CG
        
        # Extract other entities using the new functions and assign confidence
        parsed_data_v2['word_buckets'] = extract_word_buckets(text)
        if parsed_data_v2['word_buckets']:
            word_buckets_confidence = 0.7
        
        parsed_data_v2['target_groups'] = extract_target_groups(text)
        if parsed_data_v2['target_groups']:
            target_groups_confidence = 0.7
        
        parsed_data_v2['communities'] = extract_communities(text)
        if parsed_data_v2['communities']:
            communities_confidence = 0.7
        
        parsed_data_v2['schemes_mentioned'] = extract_schemes_mentioned(text)
        if parsed_data_v2['schemes_mentioned']:
            schemes_mentioned_confidence = 0.7

        # Transfer other fields directly for now
        parsed_data_v2['people_mentioned'] = old_parsed_data.get('people_mentioned', [])
        parsed_data_v2['organizations'] = old_parsed_data.get('organizations', [])
        # parsed_data_v2['schemes_mentioned'] is already populated by extract_schemes_mentioned
        
        parsed_data_v2['needs_review'] = old_parsed_data.get('needs_review', True)
        parsed_data_v2['review_status'] = old_parsed_data.get('review_status', 'pending')
    
    # Calculate composite overall confidence
    # Simple average for now, could be weighted later
    confidences = [c for c in [event_type_confidence, location_confidence, 
                               word_buckets_confidence, target_groups_confidence,
                               communities_confidence, schemes_mentioned_confidence] if c is not None and c > 0]
    
    if confidences:
        parsed_data_v2['confidence'] = round(sum(confidences) / len(confidences), 2)
    else:
        parsed_data_v2['confidence'] = 0.0 # No confidence if nothing was extracted/matched
    
    end_time = time.time() # End time for processing_time_ms
    metadata_v2['processing_time_ms'] = int((end_time - start_time) * 1000)

    # Ensure all required fields for `location` are present, even if empty
    for key in ["district", "assembly", "block", "gp", "village", "ulb", "zone", "ward"]:
        if key not in parsed_data_v2['location']:
            parsed_data_v2['location'][key] = ""

    # Debug print before returning
    # print(f"DEBUG: Returning from parse_single_tweet_v2 for tweet_id {tweet_id}")
    # print(f"DEBUG: parsed_data_v2: {parsed_data_v2}")
    # print(f"DEBUG: old_parsed_data: {old_parsed_data}")
    # print(f"DEBUG: metadata_v2: {metadata_v2}")

    return {
        "tweet_id": tweet_id,
        "created_at": created_at_dt.isoformat(),
        "raw_text": text,
        "parsed_data_v2": parsed_data_v2,
        "old_parsed_data": old_parsed_data, # This might be None if orchestrator.parse_tweet failed
        "metadata_v2": metadata_v2
    }



def main():
    # Load raw tweets from the specified .jsonl file
    raw_tweets = []
    with open('raw_tweets_from_db.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            raw_tweets.append(json.loads(line))

    # Take the first 100 tweets
    all_tweets = raw_tweets

    orchestrator = ParsingOrchestrator()
    parsed_results_v2 = []

    # Load geography data once
    load_geo_data()

    for tweet in all_tweets:
        parsed_results_v2.append(parse_single_tweet_v2(tweet, orchestrator))

    # Save the structured JSON output to a file
    output_file_path = 'parsed_tweets_output.json'
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_results_v2, f, indent=2, ensure_ascii=False)
    print(f"Parsed tweets saved to {output_file_path}")

if __name__ == '__main__':
    main()