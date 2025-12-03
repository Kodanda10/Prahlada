#!/usr/bin/env python3
"""
Builds processed geo datasets for Chhattisgarh from the provided LGD extracts.

Inputs (already placed under data/raw/LGD):
- Villageof_Specific_State_*.xlsx
- Ulb_Specific_State_*.xlsx
- District_Subdistrict_Village_Gps_*.xlsx
- Village_Gram_Panchayat_Mapping_*.xlsx
- Subdistrict_Village_Block_Gps_Mapping_*.xlsx
- District_Village_Block_Gps_Mapping_*.xlsx
- Constituency_Report_*.xlsx

Outputs:
- data/processed/chhattisgarh_geo_master.json
- data/processed/chhattisgarh_geo_flat.csv
- data/processed/chhattisgarh_geo.sqlite
- data/processed/chhattisgarh_geo_aliases.json
- reports/validation/block_completeness_report.json
- reports/validation/missing_units_report.json
- reports/validation/ac_coverage_report.json
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_LGD = BASE_DIR / "data" / "raw" / "LGD"
PROCESSED = BASE_DIR / "data" / "processed"
REPORTS = BASE_DIR / "reports" / "validation"
MANUAL = BASE_DIR / "data" / "raw" / "manual"


def slugify(text: str) -> str:
    cleaned = (
        text.lower()
        .replace("(", " ")
        .replace(")", " ")
        .replace("/", " ")
        .replace("-", " ")
        .replace("'", " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace("’", " ")
        .replace("`", " ")
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ï", "i")
        .replace("ó", "o")
        .replace("ö", "o")
        .replace("ú", "u")
    )
    parts = cleaned.split()
    return "-".join(filter(None, parts))


def safe_slug(text: str) -> str:
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    slug_parts = slugify(text)
    return slug_parts or "unknown"


def read_excel_one_sheet(pattern: str, skip_rows: int = 1, usecols=None) -> pd.DataFrame:
    matches = list(RAW_LGD.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file matching {pattern} in {RAW_LGD}")
    # Use the latest file if multiple versions exist.
    matches.sort()
    path = matches[-1]
    df = pd.read_excel(path, skiprows=skip_rows, usecols=usecols)
    return df


def load_table_cached(pattern: str, csv_name: str, usecols: List[str]) -> pd.DataFrame:
    csv_path = RAW_LGD / csv_name
    if csv_path.exists():
        return pd.read_csv(csv_path)
    df = read_excel_one_sheet(pattern, usecols=usecols)
    df.to_csv(csv_path, index=False)
    return df


@dataclass
class GeoRecord:
    geo_id: str
    geo_type: str
    parent_geo_id: Optional[str]
    ancestors: List[str]
    names: Dict[str, Optional[str]]
    codes: Dict[str, Optional[int]]
    is_active: bool
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    created_from_source: str = "LGD"
    extras: Optional[Dict] = None
    coordinates: Optional[Dict[str, float]] = None


def build():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    MANUAL.mkdir(parents=True, exist_ok=True)

    villages_df = load_table_cached(
        "Villageof_Specific_State_*.xlsx",
        "Villageof_Specific_State_cached.csv",
        usecols=[
            "District Code",
            "District Name (In English)",
            "Sub-District Code",
            "Sub-District Name (In English)",
            "Village Code",
            "Village Version",
            "Village Name (In English)",
            "Village Name (In Local)",
            "Village Category",
            "Village Status",
            "Census 2001 Code",
            "Census 2011 Code",
        ],
    )
    ulb_df = read_excel_one_sheet(
        "Ulb_Specific_State_*.xlsx",
        usecols=[
            "Localbody Type Code",
            "Localbody Type Name",
            "Localbody Code",
            "Localbody Version",
            "Localbody Name (In English)",
            "Localbody Name (In Local)",
            "Census 2001 Code",
            "Census 2011 Code",
        ],
    )
    village_gp_df = load_table_cached(
        "Village_Gram_Panchayat_Mapping_*.xlsx",
        "Village_Gram_Panchayat_Mapping_cached.csv",
        usecols=[
            "District Code",
            "District Name (In English)",
            "District Census 2011 Code",
            "District Census 2001 Code",
            "Subdistrict Code",
            "Subdistrict Name (In English)",
            "Subdistrict Census 2011 Code",
            "Subdistrict Census 2001 Code",
            "Village Code",
            "Village Name (In English)",
            "Village Census 2011 Code",
            "Village Census 2001 Code",
            "Local Body Code",
            "Local Body Name (In English)",
        ],
    )
    subd_village_block_df = load_table_cached(
        "Subdistrict_Village_Block_Gps_Mapping_*.xlsx",
        "Subdistrict_Village_Block_Gps_Mapping_cached.csv",
        usecols=[
            "State Code",
            "State Name (In English)",
            "State Census 2011 Code",
            "District Code",
            "District Name  (In English)",
            "District Census 2011 Code",
            "Subdistrict Code",
            "Subdistrict Name (In English)",
            "Subdistrict Census 2011 Code",
            "Village Code",
            "Village Name (In English)",
            "Village Census 2011 Code",
            "Local Body Code",
            "Local Body Name (In English)",
            "Local Body 2011 Code",
            "Development Block Code",
            "Development Block Name  (In English)",
            "District Code of Development Block",
            "District Name of Development Block (In English)",
        ],
    )
    dist_village_block_df = load_table_cached(
        "District_Village_Block_Gps_Mapping_*.xlsx",
        "District_Village_Block_Gps_Mapping_cached.csv",
        usecols=[
            "State Code",
            "State Name (In English)",
            "District Code",
            "District Name  (In English)",
            "Development Block Code",
            "Development Block Name  (In English)",
            "Local Body Code",
            "Local Body Name (In English)",
            "Village Code",
            "Village Name (In English)",
        ],
    )
    constituency_df = read_excel_one_sheet(
        "Constituency_Report_*.xlsx",
        usecols=[
            "Parliament Constituency Code",
            "Parliament Constituency Name",
            "Assembly Constituency Code",
            "Assembly Constituency Name",
            "Entity Type",
            "Entity Code",
            "Entity Name",
            "Coverage Type",
        ],
    )
    ac_pc_manual = pd.read_csv(MANUAL / "ac_pc_district_mapping.csv")

    # Restrict to Chhattisgarh (State Code 22) where present to avoid processing all-India rows.
    for df_name, df in [
        ("villages_df", villages_df),
        ("village_gp_df", village_gp_df),
        ("subd_village_block_df", subd_village_block_df),
        ("dist_village_block_df", dist_village_block_df),
    ]:
        if "State Code" in df.columns:
            mask = df["State Code"] == 22
            globals()[df_name] = df.loc[mask].copy()

    records: Dict[str, GeoRecord] = {}
    aliases: Dict[str, str] = {}

    # Districts from villages file.
    for _, row in villages_df[["District Code", "District Name (In English)"]].drop_duplicates().iterrows():
        dist_code = int(row["District Code"])
        dist_name_en = row["District Name (In English)"]
        dist_id = f"cg:dist:{safe_slug(dist_name_en)}"
        record = GeoRecord(
            geo_id=dist_id,
            geo_type="district",
            parent_geo_id="cg:state:chhattisgarh",
            ancestors=["cg:state:chhattisgarh"],
            names={
                "hi": None,
                "hi_nukhta": None,
                "en": dist_name_en,
                "tr_iso": None,
            },
            codes={"lgd_code": dist_code, "census_code": None},
            is_active=True,
        )
        records[dist_id] = record
        aliases[dist_name_en] = dist_id

    # Subdistricts.
    for _, row in villages_df[
        ["District Code", "District Name (In English)", "Sub-District Code", "Sub-District Name (In English)"]
    ].drop_duplicates().iterrows():
        sub_code = int(row["Sub-District Code"])
        sub_name_en = row["Sub-District Name (In English)"]
        dist_name_en = row["District Name (In English)"]
        dist_id = f"cg:dist:{safe_slug(dist_name_en)}"
        sub_id = f"{dist_id}:subdistrict:{safe_slug(sub_name_en)}"
        record = GeoRecord(
            geo_id=sub_id,
            geo_type="subdistrict",
            parent_geo_id=dist_id,
            ancestors=["cg:state:chhattisgarh", dist_id],
            names={
                "hi": None,
                "hi_nukhta": None,
                "en": sub_name_en,
                "tr_iso": None,
            },
            codes={"lgd_code": sub_code, "census_code": None},
            is_active=True,
        )
        records[sub_id] = record
        aliases[sub_name_en] = sub_id

    # Blocks (Development Blocks).
    for _, row in subd_village_block_df[
        ["District Code of Development Block", "District Name of Development Block (In English)",
         "Development Block Code", "Development Block Name  (In English)"]
    ].drop_duplicates().iterrows():
        dist_code = int(row["District Code of Development Block"])
        dist_name = row["District Name of Development Block (In English)"]
        block_code = int(row["Development Block Code"])
        block_name = row["Development Block Name  (In English)"]
        dist_id = f"cg:dist:{safe_slug(dist_name)}"
        block_id = f"{dist_id}:block:{safe_slug(block_name)}"
        record = GeoRecord(
            geo_id=block_id,
            geo_type="block",
            parent_geo_id=dist_id,
            ancestors=["cg:state:chhattisgarh", dist_id],
            names={
                "hi": None,
                "hi_nukhta": None,
                "en": block_name,
                "tr_iso": None,
            },
            codes={"lgd_code": block_code, "census_code": None},
            is_active=True,
        )
        records[block_id] = record
        aliases[block_name] = block_id

    # Gram Panchayats from village-GP mapping.
    for _, row in village_gp_df[
        ["District Name (In English)", "Local Body Code", "Local Body Name (In English)"]
    ].drop_duplicates().iterrows():
        dist_name = row["District Name (In English)"]
        gp_code = int(row["Local Body Code"]) if not pd.isna(row["Local Body Code"]) else None
        gp_name = row["Local Body Name (In English)"]
        if not gp_name:
            continue
        dist_id = f"cg:dist:{safe_slug(dist_name)}"
        gp_id = f"{dist_id}:gp:{safe_slug(gp_name)}"
        record = GeoRecord(
            geo_id=gp_id,
            geo_type="gp",
            parent_geo_id=dist_id,
            ancestors=["cg:state:chhattisgarh", dist_id],
            names={
                "hi": None,
                "hi_nukhta": None,
                "en": gp_name,
                "tr_iso": None,
            },
            codes={"lgd_code": gp_code, "census_code": None},
            is_active=True,
        )
        records[gp_id] = record
        aliases[gp_name] = gp_id

    # Villages with links to subdistrict and GP where available.
    village_records = []
    gp_map = village_gp_df.set_index("Village Code")[
        ["Local Body Code", "Local Body Name (In English)"]
    ]
    block_map = subd_village_block_df.set_index("Village Code")[
        ["Development Block Code", "Development Block Name  (In English)"]
    ]

    for _, row in villages_df.iterrows():
        dist_name = row["District Name (In English)"]
        sub_name = row["Sub-District Name (In English)"]
        dist_id = f"cg:dist:{safe_slug(dist_name)}"
        sub_id = f"{dist_id}:subdistrict:{safe_slug(sub_name)}"
        village_code = int(row["Village Code"])
        village_name_en = row["Village Name (In English)"]
        village_name_local = row.get("Village Name (In Local)")
        census2011 = int(row["Census 2011 Code"]) if not pd.isna(row["Census 2011 Code"]) else None
        census2001 = int(row["Census 2001 Code"]) if not pd.isna(row["Census 2001 Code"]) else None
        category = row.get("Village Category")
        status = row.get("Village Status")

        gp_id = None
        gp_row = gp_map.loc[village_code] if village_code in gp_map.index else None
        if gp_row is not None:
            if isinstance(gp_row, pd.DataFrame):
                gp_row = gp_row.iloc[0]
            if not pd.isna(gp_row["Local Body Name (In English)"]):
                gp_id = f"{dist_id}:gp:{safe_slug(gp_row['Local Body Name (In English)'])}"

        block_id = None
        block_row = block_map.loc[village_code] if village_code in block_map.index else None
        if block_row is not None:
            if isinstance(block_row, pd.DataFrame):
                block_row = block_row.iloc[0]
            if not pd.isna(block_row["Development Block Name  (In English)"]):
                block_id = f"{dist_id}:block:{safe_slug(block_row['Development Block Name  (In English)'])}"

        ancestors = ["cg:state:chhattisgarh", dist_id]
        if sub_id in records:
            ancestors.append(sub_id)
        if block_id:
            ancestors.append(block_id)
        if gp_id:
            ancestors.append(gp_id)

        village_id = f"{dist_id}:village:{safe_slug(village_name_en)}"
        record = GeoRecord(
            geo_id=village_id,
            geo_type="village",
            parent_geo_id=gp_id or block_id or sub_id,
            ancestors=ancestors,
            names={
                "hi": village_name_local if isinstance(village_name_local, str) else None,
                "hi_nukhta": village_name_local if isinstance(village_name_local, str) else None,
                "en": village_name_en,
                "tr_iso": None,
            },
            codes={
                "lgd_code": village_code,
                "census_code": census2011 or census2001,
            },
            is_active=True,
            extras={
                "village_category": category,
                "village_status": status,
            },
        )
        records[village_id] = record
        aliases[village_name_en] = village_id
        if village_name_local:
            aliases[village_name_local] = village_id
        village_records.append(village_id)

    # Urban local bodies.
    for _, row in ulb_df.iterrows():
        ulb_type = row["Localbody Type Name"]
        ulb_code = int(row["Localbody Code"])
        ulb_name_en = row["Localbody Name (In English)"]
        ulb_name_local = row.get("Localbody Name (In Local)")
        ulb_id = f"cg:ulb:{safe_slug(ulb_name_en)}"
        record = GeoRecord(
            geo_id=ulb_id,
            geo_type="ulb",
            parent_geo_id="cg:state:chhattisgarh",
            ancestors=["cg:state:chhattisgarh"],
            names={
                "hi": ulb_name_local if isinstance(ulb_name_local, str) else None,
                "hi_nukhta": ulb_name_local if isinstance(ulb_name_local, str) else None,
                "en": ulb_name_en,
                "tr_iso": None,
            },
            codes={
                "lgd_code": ulb_code,
                "census_code": int(row["Census 2011 Code"]) if not pd.isna(row["Census 2011 Code"]) else None,
            },
            is_active=True,
            extras={"ulb_type": ulb_type},
        )
        records[ulb_id] = record
        aliases[ulb_name_en] = ulb_id
        if ulb_name_local:
            aliases[ulb_name_local] = ulb_id

    # Ward mapping data - load both ward files
    ward_mapping_df = pd.read_excel(BASE_DIR / "LGD_Chhattisgarh Complete Geographical Data" / "Chhattisgarh_District to Ward Mapping.xlsx")
    ward_names_df = pd.read_excel(BASE_DIR / "LGD_Chhattisgarh Complete Geographical Data" / "Chhattisgarh_District to Ward Mapping_Ward Name Mapping.xlsx")

    # Process wards - merge ward numbers and ward names
    for _, row in ward_mapping_df.iterrows():
        district_name = row.get("जिला", "").strip()
        ulb_name = row.get("निकाय का नाम", "").strip()
        ward_number = int(row["वार्ड क्रमांक"]) if not pd.isna(row["वार्ड क्रमांक"]) else None

        if not district_name or not ulb_name or not ward_number:
            continue

        # Find corresponding ward name from the names file
        ward_name = None
        ward_names_match = ward_names_df[
            (ward_names_df["जिला"] == district_name) &
            (ward_names_df["निकाय का नाम"] == ulb_name) &
            (ward_names_df["वार्ड क्रमांक"] == ward_number)
        ]
        if not ward_names_match.empty:
            ward_name = ward_names_match.iloc[0].get("वार्ड का नाम", "").strip()

        # Create ward ID
        ulb_id = f"cg:ulb:{safe_slug(ulb_name)}"
        ward_id = f"{ulb_id}:ward:{ward_number}"

        record = GeoRecord(
            geo_id=ward_id,
            geo_type="ward",
            parent_geo_id=ulb_id,
            ancestors=["cg:state:chhattisgarh", ulb_id],
            names={
                "hi": ward_name if ward_name else None,
                "hi_nukhta": ward_name if ward_name else None,
                "en": ward_name if ward_name else f"Ward {ward_number}",
                "tr_iso": None,
            },
            codes={"ward_number": ward_number},
            is_active=True,
            extras={
                "district": district_name,
                "ulb_name": ulb_name,
                "ward_name_hindi": ward_name,
            },
        )
        records[ward_id] = record

        # Add aliases for both Hindi and English names
        if ward_name:
            aliases[ward_name] = ward_id
        aliases[f"Ward {ward_number}"] = ward_id
        aliases[f"{ulb_name} Ward {ward_number}"] = ward_id

    # Assembly and Parliament Constituencies.
    # Parliament constituencies from LGD constituency report.
    for _, row in constituency_df[
        ["Parliament Constituency Code", "Parliament Constituency Name"]
    ].drop_duplicates().iterrows():
        pc_code = int(row["Parliament Constituency Code"])
        pc_name = row["Parliament Constituency Name"]
        pc_id = f"cg:pc:{safe_slug(pc_name)}"
        records[pc_id] = GeoRecord(
            geo_id=pc_id,
            geo_type="pc",
            parent_geo_id="cg:state:chhattisgarh",
            ancestors=["cg:state:chhattisgarh"],
            names={"hi": None, "hi_nukhta": None, "en": pc_name, "tr_iso": None},
            codes={"lgd_code": pc_code},
            is_active=True,
        )
        aliases[pc_name] = pc_id

    # Assembly constituencies from manual mapping to ensure district/PC linkage.
    for _, row in ac_pc_manual.iterrows():
        ac_name = row["ac_name_en"]
        pc_name = row["pc_name_en"]
        district_name = row["district_en"]
        reservation = row["reservation"]

        pc_id = f"cg:pc:{safe_slug(pc_name)}"
        if pc_id not in records:
            records[pc_id] = GeoRecord(
                geo_id=pc_id,
                geo_type="pc",
                parent_geo_id="cg:state:chhattisgarh",
                ancestors=["cg:state:chhattisgarh"],
                names={"hi": None, "hi_nukhta": None, "en": pc_name, "tr_iso": None},
                codes={"lgd_code": None},
                is_active=True,
            )
            aliases[pc_name] = pc_id

        ac_id = f"cg:ac:{safe_slug(ac_name)}"
        ancestors = ["cg:state:chhattisgarh", pc_id]
        district_id = f"cg:dist:{safe_slug(district_name)}"
        if district_id in records:
            ancestors.append(district_id)
        records[ac_id] = GeoRecord(
            geo_id=ac_id,
            geo_type="ac",
            parent_geo_id=pc_id,
            ancestors=ancestors,
            names={"hi": None, "hi_nukhta": None, "en": ac_name, "tr_iso": None},
            codes={"lgd_code": None},
            is_active=True,
            extras={"reservation": reservation, "district": district_name},
        )
        aliases[ac_name] = ac_id

    # Build master JSON.
    master_path = PROCESSED / "chhattisgarh_geo_master.json"
    with master_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(rec) for rec in records.values()], f, ensure_ascii=False, indent=2)

    # Flat CSV.
    flat_rows = []
    for rec in records.values():
        flat_rows.append(
            {
                "geo_id": rec.geo_id,
                "geo_type": rec.geo_type,
                "name_en": rec.names.get("en"),
                "name_hi": rec.names.get("hi"),
                "parent_geo_id": rec.parent_geo_id,
                "lgd_code": rec.codes.get("lgd_code"),
                "census_code": rec.codes.get("census_code"),
                "extras": json.dumps(rec.extras or {}, ensure_ascii=False),
            }
        )
    pd.DataFrame(flat_rows).to_csv(PROCESSED / "chhattisgarh_geo_flat.csv", index=False)

    # SQLite.
    sqlite_path = PROCESSED / "chhattisgarh_geo.sqlite"
    if sqlite_path.exists():
        sqlite_path.unlink()
    conn = sqlite3.connect(sqlite_path)
    pd.DataFrame(flat_rows).to_sql("geo_units", conn, index=False)
    conn.execute("CREATE INDEX idx_geo_id ON geo_units(geo_id);")
    conn.execute("CREATE INDEX idx_geo_type ON geo_units(geo_type);")
    conn.close()

    # Aliases.
    with (PROCESSED / "chhattisgarh_geo_aliases.json").open("w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2)

    # Validation: block mapping consistency.
    block_mismatch = []
    block_map_a = subd_village_block_df[["Village Code", "Development Block Code"]].dropna()
    block_map_b = dist_village_block_df[["Village Code", "Development Block Code"]].dropna()
    merged = block_map_a.merge(block_map_b, on="Village Code", how="outer", suffixes=("_a", "_b"))
    inconsistent = merged[(merged["Development Block Code_a"] != merged["Development Block Code_b"])]
    for _, row in inconsistent.iterrows():
        block_mismatch.append(
            {
                "village_code": int(row["Village Code"]),
                "block_code_a": int(row["Development Block Code_a"]) if not pd.isna(row["Development Block Code_a"]) else None,
                "block_code_b": int(row["Development Block Code_b"]) if not pd.isna(row["Development Block Code_b"]) else None,
            }
        )
    with (REPORTS / "block_completeness_report.json").open("w", encoding="utf-8") as f:
        json.dump({"inconsistent_block_mappings": block_mismatch}, f, indent=2)

    # Missing units report (placeholder for now – focuses on villages missing GP or block).
    missing_gp = [vid for vid in village_records if records[vid].parent_geo_id is None]
    with (REPORTS / "missing_units_report.json").open("w", encoding="utf-8") as f:
        json.dump({"villages_missing_gp_or_block": missing_gp}, f, indent=2)

    # AC coverage stub based on constituency file presence.
    with (REPORTS / "ac_coverage_report.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "total_ac": constituency_df["Assembly Constituency Code"].nunique(),
                "total_pc": constituency_df["Parliament Constituency Code"].nunique(),
                "note": "Mapping to villages/ULBs requires SEC/ECI polling-station data; not present in LGD extract.",
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    build()
