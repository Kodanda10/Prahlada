#!/usr/bin/env python3
"""
Generate FAISS-based suggestions for village names missing in the reference list.

Output: tmp/geography_missing_suggestions.csv with top-3 semantic matches
from data/embeddings/multilingual_geography/{locations.json, embeddings.npy}.

This is a QA aid; it does NOT modify the hierarchy. Review the suggestions and
apply authoritative Hindi names manually (or feed them back into enrichment).
"""
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import faiss  # type: ignore
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent.parent
HIERARCHY_PATH = ROOT / "public" / "chhattisgarh_hierarchy_hindi.json"
REFERENCE_DIR = ROOT / "data" / "embeddings" / "multilingual_geography"
OUT_PATH = ROOT / "tmp" / "geography_missing_suggestions.csv"


def normalize(name: str) -> str:
    if not name:
        return ""
    s = name.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"\b(alias|alis|urf|ryt\.?)\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def load_reference() -> Dict[str, str]:
    """Return norm -> first occurrence string map."""
    locations = json.loads((REFERENCE_DIR / "locations.json").read_text())
    out: Dict[str, str] = {}
    for loc in locations:
        n = normalize(loc)
        if n and n not in out:
            out[n] = loc
    return out


def load_hierarchy() -> Dict:
    return json.loads(HIERARCHY_PATH.read_text())


def find_missing(hierarchy: Dict, reference_norms: set) -> List[str]:
    missing = []
    for dist in hierarchy.values():
        for ac in dist.get("acs", {}).values():
            for blk in ac.get("blocks", {}).values():
                for v in blk.get("villages", []):
                    n = normalize(v.get("name", ""))
                    if n and n not in reference_norms:
                        missing.append(v.get("name", ""))
    return missing


def build_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    # Using L2 because embeddings are already unit-normalized; convert to cosine later.
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def cosine_from_l2(distances: np.ndarray) -> np.ndarray:
    # For unit-normalized vectors: d^2 = 2 - 2cos => cos = 1 - d^2/2
    return 1.0 - (distances / 2.0)


def suggest_matches(
    missing: List[str],
    index: faiss.Index,
    embeddings: np.ndarray,
    locations: List[str],
    model: SentenceTransformer,
    top_k: int = 3,
) -> List[Tuple[str, List[Tuple[str, float]]]]:
    results = []
    for name in missing:
        q_emb = model.encode([name], normalize_embeddings=True, convert_to_tensor=False)[0].astype(
            np.float32
        )
        dists, idxs = index.search(q_emb.reshape(1, -1), top_k)
        sims = cosine_from_l2(dists[0])
        suggestions = []
        for sim, idx in zip(sims, idxs[0]):
            if idx < len(locations):
                suggestions.append((locations[idx], float(sim)))
        results.append((name, suggestions))
    return results


def main():
    assert HIERARCHY_PATH.exists(), "Hierarchy file missing"
    assert (REFERENCE_DIR / "locations.json").exists(), "Reference locations missing"
    assert (REFERENCE_DIR / "embeddings.npy").exists(), "Reference embeddings missing"

    hierarchy = load_hierarchy()
    ref_map = load_reference()
    ref_norms = set(ref_map.keys())

    missing = find_missing(hierarchy, ref_norms)
    print(f"Missing against reference: {len(missing)}")

    embeddings = np.load(REFERENCE_DIR / "embeddings.npy")
    locations = json.loads((REFERENCE_DIR / "locations.json").read_text())
    index = build_index(embeddings)
    model = SentenceTransformer("intfloat/multilingual-e5-base")

    suggestions = suggest_matches(missing, index, embeddings, locations, model, top_k=3)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["missing_name", "cand1", "sim1", "cand2", "sim2", "cand3", "sim3"])
        for name, suggs in suggestions:
            row = [name]
            for cand, sim in suggs:
                row.extend([cand, f"{sim:.4f}"])
            # pad row to fixed length
            while len(row) < 7:
                row.append("")
            writer.writerow(row)

    print(f"Wrote suggestions to {OUT_PATH}")


if __name__ == "__main__":
    main()
