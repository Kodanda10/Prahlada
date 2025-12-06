#!/usr/bin/env python3
"""
Build Hindi-enriched urban hierarchy (State -> ULB -> Ward) using the LGD ward mapping file:
/Users/abhijita/Documents/Project_Maati/LGD_Chhattisgarh Complete Geographical Data/Chhattisgarh_District to Ward Mapping_Ward Name Mapping.xlsx

Output: public/chhattisgarh_urban_hierarchy_hindi.json
Also validates Devanagari-only content.
"""
import json
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

DEV_RE = re.compile(r"^[\u0900-\u097F\u0966-\u096F\s\-/()]+$")

ROOT = Path(__file__).parent.parent
WARD_XLSX = Path("/Users/abhijita/Documents/Project_Maati/LGD_Chhattisgarh Complete Geographical Data/Chhattisgarh_District to Ward Mapping_Ward Name Mapping.xlsx")
OUTPUT = ROOT / "public" / "chhattisgarh_urban_hierarchy_hindi.json"


def is_devanagari(text: str) -> bool:
    return bool(text) and DEV_RE.match(text) is not None


def build_hierarchy(df: pd.DataFrame) -> Dict:
    # Standardize column names
    df = df.rename(
        columns={
            "संभाग": "division_hi",
            "जिला": "district_hi",
            "निकाय का प्रकार": "ulb_type_hi",
            "निकाय का नाम": "ulb_name_hi",
            "वार्ड क्रमांक": "ward_no",
            "वार्ड का नाम": "ward_name_hi",
        }
    )
    hierarchy: Dict[str, Dict] = {}
    for _, row in df.iterrows():
        district = str(row["district_hi"])
        ulb_name = str(row["ulb_name_hi"])
        ulb_type = str(row["ulb_type_hi"])
        ward_no = str(row["ward_no"]).strip()
        ward_name = str(row["ward_name_hi"]).strip()

        hierarchy.setdefault(district, {"ulbs": {}})
        district_obj = hierarchy[district]
        district_obj["ulbs"].setdefault(ulb_name, {"type": ulb_type, "wards": []})
        district_obj["ulbs"][ulb_name]["wards"].append(
            {"ward_no": ward_no, "name_hi": ward_name}
        )
    return hierarchy


def validate_hindi(hierarchy: Dict) -> List[str]:
    leaks = []
    for dist, dist_obj in hierarchy.items():
        if not is_devanagari(dist):
            leaks.append(f"district non-Hindi: {dist}")
        for ulb_name, ulb_obj in dist_obj.get("ulbs", {}).items():
            if not is_devanagari(ulb_name):
                leaks.append(f"ULB non-Hindi: {ulb_name}")
            for ward in ulb_obj.get("wards", []):
                if not is_devanagari(ward.get("name_hi", "")):
                    leaks.append(f"Ward non-Hindi: {ward.get('name_hi')}")
    return leaks


def main():
    assert WARD_XLSX.exists(), f"Missing ward file: {WARD_XLSX}"
    df = pd.read_excel(WARD_XLSX)
    hierarchy = build_hierarchy(df)
    leaks = validate_hindi(hierarchy)
    if leaks:
        print("⚠️ Hindi validation leaks (showing first 10):")
        for leak in leaks[:10]:
            print(" ", leak)
    else:
        print("✅ Urban hierarchy is Devanagari-only")
    OUTPUT.write_text(json.dumps(hierarchy, ensure_ascii=False, indent=2))
    print(f"✔️ Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
