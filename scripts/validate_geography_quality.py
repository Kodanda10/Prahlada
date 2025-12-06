#!/usr/bin/env python3
"""
QA helper for Hindi geography data.

Cross-checks the enriched hierarchy against the reference location list used by
FAISS (data/embeddings/multilingual_geography/locations.json), reports:
- Hindi-only validation (no Latin leakage)
- Coverage of English names present in reference list
- Sample nearest matches for missing names to speed manual fixes
"""
import json
import re
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List, Set, Tuple


ROOT = Path(__file__).parent.parent
HIERARCHY_PATH = ROOT / "public" / "chhattisgarh_hierarchy_hindi.json"
REFERENCE_PATH = ROOT / "data" / "embeddings" / "multilingual_geography" / "locations.json"
LGD_VILLAGE_PATH = ROOT / "data" / "raw" / "LGD" / "Villageof_Specific_State_cached.csv"

DEV_RE = re.compile(r"^[\u0900-\u097F\u0966-\u096F\s\-/()]+$")


def normalize(name: str) -> str:
    """Lowercase, drop punctuation/aliases to align with reference list."""
    if not name:
        return ""
    s = name.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"\b(alias|alis|urf|ryt\.?)\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def load_reference() -> Set[str]:
    ref_raw = json.loads(REFERENCE_PATH.read_text())
    return {normalize(x) for x in ref_raw if normalize(x)}


def load_lgd_english() -> Set[str]:
    if not LGD_VILLAGE_PATH.exists():
        return set()
    import pandas as pd  # Optional dependency for this QA script

    df = pd.read_csv(LGD_VILLAGE_PATH)
    names = set()
    for val in df.get("Village Name (In English)", []):
        normed = normalize(str(val))
        if normed:
            names.add(normed)
    return names


def load_hierarchy() -> Dict:
    return json.loads(HIERARCHY_PATH.read_text())


def find_latin_leaks(data: Dict) -> List[Tuple[str, str, str]]:
    issues = []

    def check(kind: str, name_en: str, val: str):
        if val and not DEV_RE.match(val):
            issues.append((kind, name_en, val))

    for dist_en, dist in data.items():
        check("district", dist_en, dist.get("name_hi", ""))
        for ac_en, ac in dist.get("acs", {}).items():
            check("ac", ac_en, ac.get("name_hi", ""))
            for blk_en, blk in ac.get("blocks", {}).items():
                check("block", blk_en, blk.get("name_hi", ""))
                for v in blk.get("villages", []):
                    check("village", v.get("name", ""), v.get("name_hi", ""))
                    check("gp", v.get("gp_name", ""), v.get("gp_name_hi", ""))
    return issues


def coverage_report(data: Dict, reference: Set[str]) -> Tuple[int, int, List[str]]:
    missing = []
    total = 0
    for dist in data.values():
        for ac in dist.get("acs", {}).values():
            for blk in ac.get("blocks", {}).values():
                for v in blk.get("villages", []):
                    total += 1
                    name_norm = normalize(v.get("name", ""))
                    if name_norm and name_norm not in reference:
                        missing.append(v.get("name", ""))
    return total, len(missing), missing


def suggest_matches(missing: List[str], reference: Set[str], limit: int = 10):
    ref_list = list(reference)
    suggestions = []
    for name in missing[:limit]:
        normed = normalize(name)
        matches = get_close_matches(normed, ref_list, n=3, cutoff=0.65)
        suggestions.append((name, matches))
    return suggestions


def main():
    assert HIERARCHY_PATH.exists(), f"Missing hierarchy at {HIERARCHY_PATH}"
    assert REFERENCE_PATH.exists(), f"Missing reference list at {REFERENCE_PATH}"

    hierarchy = load_hierarchy()
    reference = load_reference()
    lgd_reference = load_lgd_english()
    merged_reference = reference | lgd_reference

    leaks = find_latin_leaks(hierarchy)
    total, missing_count, missing = coverage_report(hierarchy, reference)
    merged_total, merged_missing_count, merged_missing = coverage_report(hierarchy, merged_reference)
    suggestions = suggest_matches(missing, reference, limit=20)

    print("=== Hindi Integrity ===")
    print(f"Latin/punctuation leaks: {len(leaks)} (should be 0)")
    if leaks:
        for row in leaks[:5]:
            print("  ", row)

    print("\n=== Reference Coverage ===")
    print(f"Villages total: {total}")
    print(f"Missing in reference list: {missing_count} ({missing_count*100/total:.2f}%)")
    if lgd_reference:
        print(f"Missing after adding LGD English names: {merged_missing_count} ({merged_missing_count*100/merged_total:.2f}%)")

    print("\n=== Sample Suggestions (missing vs reference) ===")
    for name, matches in suggestions:
        print(f"  {name} -> {matches or 'no close match'}")


if __name__ == "__main__":
    main()
