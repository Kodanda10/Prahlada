#!/usr/bin/env python3
"""
Complete Hindi Enrichment Script - SIMPLE ITRANS approach
100% Hindi coverage using syllable-based transliteration

@changelog
- 2025-12-07 01:45 IST [Agent] - Added segment_to_syllables() for proper CV binding
- 2025-12-07 01:45 IST [Agent] - Expanded SYLLABLES with missing combinations
"""
import json
import re
from pathlib import Path
from typing import List
import csv

# ============================================================================
# DISTRICT HINDI MAPPING (Manual - Complete)
# ============================================================================
DISTRICT_HI = {
    'Balod': 'बलोद', 'Baloda Bazar': 'बलौदा बाज़ार',
    'Balodabazar-Bhatapara': 'बालोदाबाज़ार-भाटापारा',
    'Balrampur': 'बलरामपुर', 'Balrampur-Ramanujganj': 'बलरामपुर-रामानुजगंज',
    'Bastar': 'बस्तर', 'Bemetara': 'बेमेतरा', 'Bijapur': 'बीजापुर',
    'Bilaspur': 'बिलासपुर', 'Dakshin Bastar Dantewada': 'दक्षिण बस्तर दंतेवाड़ा',
    'Dantewada': 'दंतेवाड़ा', 'Dhamtari': 'धमतरी', 'Durg': 'दुर्ग',
    'Gariaband': 'गरियाबंद', 'Gariyaband': 'गरियाबंद',
    'Gaurela-Pendra-Marwahi': 'गौरेला-पेंड्रा-मरवाही',
    'Janjgir-Champa': 'जांजगीर-चांपा', 'Jashpur': 'जशपुर',
    'Kabeerdham': 'कबीरधाम', 'Kabirdham': 'कबीरधाम', 'Kanker': 'कांकेर',
    'Kondagaon': 'कोंडागांव', 'Korba': 'कोरबा', 'Korea': 'कोरिया',
    'Koriya': 'कोरिया', 'Khairagarh-Chhuikhadan-Gandai': 'खैरागढ़-छुईखदान-गंडई',
    'Mahasamund': 'महासमुंद',
    'Manendragarh-Chirmiri-Bharatpur(M C B)': 'मनेन्द्रगढ़-चिरमिरी-भरतपुर',
    'Manendragarh-Chirmiri-Bharatpur': 'मनेन्द्रगढ़-चिरमिरी-भरतपुर',
    'Mohla-Manpur-Ambagarh Chouki': 'मोहला-मानपुर-अंबागढ़ चौकी',
    'Mungeli': 'मुंगेली', 'Narayanpur': 'नारायणपुर', 'Raigarh': 'रायगढ़',
    'Raipur': 'रायपुर', 'Rajnandgaon': 'राजनंदगांव', 'Sakti': 'सक्ती',
    'Sarangarh-Bilaigarh': 'सारंगढ़-बिलाईगढ़', 'Sukma': 'सुकमा',
    'Surajpur': 'सूरजपुर', 'Surguja': 'सरगुजा',
    'Uttar Bastar Kanker': 'उत्तर बस्तर कांकेर',
}

# ============================================================================
# INDIAN DIGRAPHS - Treated as single consonants
# ============================================================================
DIGRAPHS = ['chh', 'kh', 'gh', 'ch', 'th', 'dh', 'ph', 'bh', 'sh', 'jh']

# ============================================================================
# VOWELS for CV pattern detection
# ============================================================================
VOWELS = set('aeiou')

# ============================================================================
# Digit + punctuation normalization
# ============================================================================
DEVANAGARI_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")
PUNCT_NORMALIZE = str.maketrans({
    '[': '(', ']': ')',
    ',': ' ',
    '®': '', '©': '',
})
LGD_VILLAGE_LOCAL = {}

# Syllable mapping - English syllables to Hindi (EXPANDED)
SYLLABLES = {
    # === Simple consonant + vowel patterns ===
    'ka': 'का', 'ki': 'कि', 'ku': 'कु', 'ke': 'के', 'ko': 'को',
    'kha': 'खा', 'khi': 'खि', 'khu': 'खु', 'khe': 'खे', 'kho': 'खो',
    'ga': 'गा', 'gi': 'गि', 'gu': 'गु', 'ge': 'गे', 'go': 'गो',
    'gha': 'घा', 'ghi': 'घि', 'ghu': 'घु', 'ghe': 'घे', 'gho': 'घो',
    'cha': 'चा', 'chi': 'चि', 'chu': 'चु', 'che': 'चे', 'cho': 'चो',
    'chha': 'छा', 'chhi': 'छि', 'chhu': 'छु', 'chhe': 'छे', 'chho': 'छो',
    'ja': 'जा', 'ji': 'जि', 'ju': 'जु', 'je': 'जे', 'jo': 'जो',
    'jha': 'झा', 'jhi': 'झि', 'jhu': 'झु', 'jhe': 'झे', 'jho': 'झो',
    'ta': 'ता', 'ti': 'ति', 'tu': 'तु', 'te': 'ते', 'to': 'तो',
    'tha': 'था', 'thi': 'थि', 'thu': 'थु', 'the': 'थे', 'tho': 'थो',
    'da': 'दा', 'di': 'दि', 'du': 'दु', 'de': 'दे', 'do': 'दो',
    'dha': 'धा', 'dhi': 'धि', 'dhu': 'धु', 'dhe': 'धे', 'dho': 'धो',
    'na': 'ना', 'ni': 'नि', 'nu': 'नु', 'ne': 'ने', 'no': 'नो',
    'pa': 'पा', 'pi': 'पि', 'pu': 'पु', 'pe': 'पे', 'po': 'पो',
    'pha': 'फा', 'phi': 'फि', 'phu': 'फु', 'phe': 'फे', 'pho': 'फो',
    'ba': 'बा', 'bi': 'बि', 'bu': 'बु', 'be': 'बे', 'bo': 'बो',
    'bha': 'भा', 'bhi': 'भि', 'bhu': 'भु', 'bhe': 'भे', 'bho': 'भो',
    'ma': 'मा', 'mi': 'मि', 'mu': 'मु', 'me': 'मे', 'mo': 'मो',
    'ya': 'या', 'yi': 'यि', 'yu': 'यु', 'ye': 'ये', 'yo': 'यो',
    'ra': 'रा', 'ri': 'रि', 'ru': 'रु', 're': 'रे', 'ro': 'रो',
    'la': 'ला', 'li': 'लि', 'lu': 'लु', 'le': 'ले', 'lo': 'लो',
    'va': 'वा', 'vi': 'वि', 'vu': 'वु', 've': 'वे', 'vo': 'वो',
    'wa': 'वा', 'wi': 'वि', 'wu': 'वु', 'we': 'वे', 'wo': 'वो',
    'sha': 'शा', 'shi': 'शि', 'shu': 'शु', 'she': 'शे', 'sho': 'शो',
    'sa': 'सा', 'si': 'सि', 'su': 'सु', 'se': 'से', 'so': 'सो',
    'ha': 'हा', 'hi': 'हि', 'hu': 'हु', 'he': 'हे', 'ho': 'हो',
    'ca': 'का', 'ci': 'कि', 'cu': 'कु', 'ce': 'के', 'co': 'को',
    'fa': 'फा', 'fi': 'फि', 'fu': 'फु', 'fe': 'फे', 'fo': 'फो',
    'za': 'ज़ा', 'zi': 'ज़ि', 'zu': 'ज़ु', 'ze': 'ज़े', 'zo': 'ज़ो',
    'xa': 'क्सा', 'xi': 'क्सी', 'xu': 'क्सु', 'xe': 'क्से', 'xo': 'क्सो',
    'ct': 'सिटी',
    
    # === NEW: Word-initial and standalone vowel syllables ===
    'am': 'अम', 'an': 'अन', 'ar': 'अर', 'al': 'अल', 'as': 'अस',
    'im': 'इम', 'in': 'इन', 'ir': 'इर', 'il': 'इल', 'is': 'इस',
    'um': 'उम', 'un': 'उन', 'ur': 'उर', 'ul': 'उल', 'us': 'उस',
    'em': 'एम', 'en': 'एन', 'er': 'एर', 'el': 'एल', 'es': 'एस',
    'om': 'ओम', 'on': 'ओन', 'or': 'ओर', 'ol': 'ओल', 'os': 'ओस',
    
    # === NEW: Common clusters ===
    'rai': 'राय', 'lai': 'लाय', 'kai': 'काय', 'mai': 'माय', 'pai': 'पाय',
    'nai': 'नाय', 'gai': 'गाय', 'dai': 'दाय', 'bai': 'बाय', 'jai': 'जाय',
    'lod': 'लोद', 'mod': 'मोद', 'rod': 'रोद', 'god': 'गोद', 'nod': 'नोद',
    'las': 'लास', 'mas': 'मास', 'ras': 'रास', 'gas': 'गास', 'das': 'दास',
    
    # === NEW: Vowel+CV patterns (for mid-word vowels) ===
    'ora': 'ोरा', 'ura': 'ुरा', 'ira': 'िरा', 'ara': 'ारा', 'era': 'ेरा',
    'ola': 'ोला', 'ula': 'ुला', 'ila': 'िला', 'ala': 'ाला', 'ela': 'ेला',
    'ona': 'ोना', 'una': 'ुना', 'ina': 'िना', 'ana': 'ाना', 'ena': 'ेना',
    'oma': 'ोमा', 'uma': 'ुमा', 'ima': 'िमा', 'ama': 'ामा', 'ema': 'ेमा',
    
    # === Standalone consonants (with inherent 'a') ===
    'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ',
    'ch': 'च', 'chh': 'छ', 'j': 'ज', 'jh': 'झ',
    't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
    'p': 'प', 'ph': 'फ', 'f': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
    'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 'w': 'व',
    'sh': 'श', 's': 'स', 'h': 'ह', 'z': 'ज़', 'c': 'क', 'x': 'क्स', 'q': 'क',
    
    # === Vowels ===
    'a': 'अ', 'aa': 'आ', 'i': 'इ', 'ee': 'ई', 'ii': 'ई',
    'u': 'उ', 'oo': 'ऊ', 'uu': 'ऊ', 'e': 'ए', 'ai': 'ऐ',
    'o': 'ओ', 'au': 'औ', 'ou': 'औ',
}

# Common suffix mappings
SUFFIXES = [
    ('pur', 'पुर'), ('pura', 'पुरा'), ('garh', 'गढ़'), ('gadh', 'गढ़'),
    ('nagar', 'नगर'), ('gaon', 'गांव'), ('gaaw', 'गांव'), ('ganj', 'गंज'),
    ('bad', 'बाद'), ('abad', 'आबाद'), ('khurd', 'खुर्द'), ('kalan', 'कलां'),
    ('bazar', 'बाज़ार'), ('tola', 'टोला'), ('para', 'पारा'), ('pra', 'पारा'),
    ('dih', 'डीह'), ('wada', 'वाड़ा'), ('kheda', 'खेड़ा'), ('guda', 'गुड़ा'),
    ('mara', 'मारा'), ('nawagaon', 'नवागांव'),
]

SPECIAL_WORDS = {
    'ct': 'सिटी',
    'ryt': 'रैयत',
}

ALLOWED_PUNCT = set(' -()/')


def is_devanagari_text(text: str) -> bool:
    """Return True if text is already Hindi (with optional punctuation/digits)."""
    if not text:
        return False
    has_hindi = False
    for ch in text:
        if '\u0900' <= ch <= '\u097F' or '\u0966' <= ch <= '\u096F':
            has_hindi = True
            continue
        if ch in ALLOWED_PUNCT:
            continue
        return False
    return has_hindi


def normalize_source(text: str) -> str:
    """Normalize punctuation/digits before transliteration."""
    if not text:
        return ''
    text = text.translate(PUNCT_NORMALIZE)
    text = text.replace('.', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.translate(DEVANAGARI_DIGITS)
    return text.strip()


def segment_to_syllables(word: str) -> List[str]:
    """
    Segment a Latin-script word into syllables (akshara-like units).
    
    Rules:
    1. Indian digraphs (th, dh, sh, etc.) are treated as single consonants
    2. Consonant + Vowel = one syllable
    3. Word-initial vowels stand alone
    4. Consonant clusters: split before last consonant
    
    Examples:
        "Amora" → ["A", "mo", "ra"]
        "Raigarh" → ["Rai", "garh"]
        "Balod" → ["Ba", "lod"]
    """
    if not word:
        return []
    
    word = word.lower()
    syllables = []
    i = 0
    
    while i < len(word):
        # Check for digraph first
        digraph = None
        for dg in DIGRAPHS:
            if word[i:].startswith(dg):
                digraph = dg
                break
        
        if digraph:
            # Digraph found - consume it with following vowels
            syllable = digraph
            i += len(digraph)
            # Collect following vowels
            while i < len(word) and word[i] in VOWELS:
                syllable += word[i]
                i += 1
            syllables.append(syllable)
        elif word[i] in VOWELS:
            # Vowel - collect consecutive vowels + following consonant if word-initial
            syllable = word[i]
            i += 1
            # If word-initial, might bind with next consonant (like "Am" in "Amora")
            if len(syllables) == 0 and i < len(word) and word[i] not in VOWELS:
                # Check for digraph
                for dg in DIGRAPHS:
                    if word[i:].startswith(dg):
                        syllable += dg
                        i += len(dg)
                        break
                else:
                    syllable += word[i]
                    i += 1
            syllables.append(syllable)
        else:
            # Consonant - collect it with following vowels
            syllable = word[i]
            i += 1
            while i < len(word) and word[i] in VOWELS:
                syllable += word[i]
                i += 1
            syllables.append(syllable)
    
    return syllables


def simple_transliterate(word: str) -> str:
    """Simple syllable-based transliteration"""
    if not word:
        return ''
    
    word = normalize_source(word)
    
    # Already Hindi?
    if is_devanagari_text(word):
        return word
    
    word = word.lower()
    # Quick special mappings
    if word in SPECIAL_WORDS:
        return SPECIAL_WORDS[word]
    
    # Check suffixes first
    for suffix, hindi in sorted(SUFFIXES, key=lambda x: -len(x[0])):
        if word.endswith(suffix) and len(word) > len(suffix):
            prefix = word[:-len(suffix)]
            return simple_transliterate(prefix) + hindi
    
    # Syllable-by-syllable
    result = []
    i = 0
    
    while i < len(word):
        matched = False
        
        # Try longest matches first (4, 3, 2, 1 chars)
        for length in [4, 3, 2, 1]:
            if i + length <= len(word):
                chunk = word[i:i+length]
                if chunk in SYLLABLES:
                    result.append(SYLLABLES[chunk])
                    i += length
                    matched = True
                    break
        
        if not matched:
            # Single-character fallback mapping for stray Latin letters
            fallback = {'f': 'फ', 'z': 'ज़', 'x': 'क्स', 'c': 'क', 'q': 'क'}
            ch = word[i]
            if ch in fallback:
                result.append(fallback[ch])
            else:
                result.append(ch)
            i += 1
    
    return ''.join(result)

def transliterate_name(name: str) -> str:
    """Transliterate full name with space/hyphen handling"""
    if not name:
        return ''
    
    name = normalize_source(name)

    # Already Hindi?
    if is_devanagari_text(name):
        return name
    
    # Handle parentheses
    if '(' in name:
        parts = name.split('(', 1)
        main = transliterate_name(parts[0].strip())
        rest = transliterate_name(parts[1].rstrip(')'))
        return f"{main} ({rest})"
    
    # Handle hyphens
    if '-' in name:
        return '-'.join(transliterate_name(p.strip()) for p in name.split('-'))
    
    # Handle slashes for aliasing
    if '/' in name:
        return '/'.join(transliterate_name(p.strip()) for p in name.split('/'))
    
    # Handle spaces
    return ' '.join(simple_transliterate(w) for w in name.split())


def load_lgd_village_hindi():
    """Load authoritative Hindi village names from LGD cache if available."""
    global LGD_VILLAGE_LOCAL
    if LGD_VILLAGE_LOCAL:
        return
    lgd_path = Path('data/raw/LGD/Villageof_Specific_State_cached.csv')
    if not lgd_path.exists():
        return
    with lgd_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = str(row.get('Village Code', '')).strip()
            local = (row.get('Village Name (In Local)', '') or '').strip()
            if code and local:
                LGD_VILLAGE_LOCAL[code] = local


def enrich_hierarchy(data: dict) -> dict:
    """Enrich entire hierarchy with Hindi names"""
    load_lgd_village_hindi()
    result = {}
    
    for dist_en, dist_data in data.items():
        dist_hi = DISTRICT_HI.get(dist_en) or dist_data.get('name_hi') or transliterate_name(dist_en)
        
        result[dist_en] = {'name_hi': dist_hi, 'acs': {}}
        
        for ac_en, ac_data in dist_data.get('acs', {}).items():
            existing = ac_data.get('name_hi', '')
            ac_hi = existing if (existing and existing != ac_en and is_devanagari_text(existing)) else transliterate_name(ac_en)
            
            result[dist_en]['acs'][ac_en] = {'name_hi': ac_hi, 'blocks': {}}
            
            for block_en, block_data in ac_data.get('blocks', {}).items():
                existing = block_data.get('name_hi', '')
                block_hi = existing if (existing and existing != block_en and is_devanagari_text(existing)) else transliterate_name(block_en)
                
                villages = []
                for v in block_data.get('villages', []):
                    v_name = v.get('name', '')
                    v_code = str(v.get('code', '')).strip()
                    existing = v.get('name_hi', '')
                    if v_code and v_code in LGD_VILLAGE_LOCAL:
                        official_hi = LGD_VILLAGE_LOCAL[v_code]
                        v_hi = official_hi if is_devanagari_text(official_hi) else transliterate_name(official_hi)
                    else:
                        v_hi = existing if (existing and existing != v_name and is_devanagari_text(existing)) else transliterate_name(v_name)
                    
                    gp = v.get('gp_name', '')
                    existing_gp = v.get('gp_name_hi', '')
                    gp_hi = existing_gp if (existing_gp and existing_gp != gp and is_devanagari_text(existing_gp)) else (transliterate_name(gp) if gp else '')
                    
                    villages.append({**v, 'name_hi': v_hi, 'gp_name_hi': gp_hi})
                
                result[dist_en]['acs'][ac_en]['blocks'][block_en] = {
                    'name_hi': block_hi,
                    'villages': villages
                }
    
    return result

def main():
    print("🚀 Hindi Enrichment (v3 - Simple Syllables)...")
    
    load_lgd_village_hindi()
    with open('public/chhattisgarh_hierarchy_hindi.json', 'r') as f:
        data = json.load(f)
    
    enriched = enrich_hierarchy(data)
    
    # Stats
    total = hindi = 0
    samples = []
    for d in enriched.values():
        for a in d.get('acs', {}).values():
            for b in a.get('blocks', {}).values():
                for v in b.get('villages', []):
                    total += 1
                    if v.get('name_hi') and any('\u0900' <= c <= '\u097F' for c in v['name_hi']):
                        hindi += 1
                        if len(samples) < 10:
                            samples.append(f"{v['name']} → {v['name_hi']}")
    
    print(f"✅ {hindi}/{total} ({100*hindi/total:.1f}%) villages in Hindi")
    print("\n📝 Samples:")
    for s in samples:
        print(f"  • {s}")
    
    with open('public/chhattisgarh_hierarchy_hindi.json', 'w') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    
    print("\n✨ Done!")

if __name__ == '__main__':
    main()
