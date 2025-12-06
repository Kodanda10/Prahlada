#!/usr/bin/env python3
"""
Test suite for Hindi transliteration and syllable segmentation.

@changelog
- 2025-12-07 01:50 IST [Agent] - Created initial test file for syllable matching
- 2025-12-07 02:20 IST [Agent] - Expanded coverage for ROCD syllable matching and suffix-based transliteration
- 2025-12-07 02:50 IST [Agent] - Added data quality guardrails and normalization tests for Hindi-only output
"""
import json
import re
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from complete_hindi_enrichment import (
    SYLLABLES,
    segment_to_syllables,
    simple_transliterate,
    transliterate_name,
)

DEV_RE = re.compile(r'^[\u0900-\u097F\u0966-\u096F\s\-/()]+$')
HIERARCHY_PATH = Path(__file__).parent.parent / "public" / "chhattisgarh_hierarchy_hindi.json"


class TestSyllableSegmentation:
    """Tests for segment_to_syllables function"""

    @pytest.mark.parametrize(
        "word, expected",
        [
            ("mora", ["mo", "ra"]),
            ("Amora", ["am", "o", "ra"]),
            ("BILASPUR", ["bi", "la", "s", "pu", "r"]),
            ("bhai", ["bhai"]),
            ("gond", ["go", "n", "d"]),
            ("chhola", ["chho", "la"]),
        ],
    )
    def test_core_segment_patterns(self, word, expected):
        assert segment_to_syllables(word) == expected

    def test_word_initial_vowel_binds_digraph(self):
        """Initial vowels should bind to the following digraph when present."""
        assert segment_to_syllables("Asha") == ["ash", "a"]

    def test_prefers_longest_digraph(self):
        """Ensures 3-letter digraphs are preferred over shorter overlaps."""
        assert segment_to_syllables("chhatarpur")[0] == "chha"

    def test_empty_word_returns_empty_list(self):
        assert segment_to_syllables("") == []

    @pytest.mark.parametrize(
        "word",
        [
            "raigarh",
            "balod",
            "bilaspur",
            "kheda",
        ],
    )
    def test_segments_are_known_syllables(self, word):
        for syllable in segment_to_syllables(word):
            assert syllable in SYLLABLES, f"{syllable} not in SYLLABLES"


class TestTransliteration:
    """Tests for simple_transliterate and transliterate_name functions"""

    @pytest.mark.parametrize(
        "syllable, expected",
        [
            ("ka", "का"),
            ("khi", "खि"),
            ("ghe", "घे"),
            ("chho", "छो"),
            ("rai", "राय"),
            ("ora", "ोरा"),
            ("uma", "ुमा"),
            ("ai", "ऐ"),
            ("oo", "ऊ"),
            ("am", "अम"),
            ("bh", "भ"),
        ],
    )
    def test_direct_syllable_mappings(self, syllable, expected):
        assert simple_transliterate(syllable) == expected

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("Amora", "अमोरा"),
            ("Raigarh", "रायगढ़"),
            ("Bilaspur", "बिलासपुर"),
            ("Nagpur", "नागपुर"),
            ("Islamabad", "इसलामआबाद"),
            ("Nawagaon", "नावागांव"),
            ("Jamkalan", "जामकलां"),
            ("Jamkhurd", "जामखुर्द"),
        ],
    )
    def test_common_place_name_transliteration(self, name, expected):
        assert simple_transliterate(name) == expected

    @pytest.mark.parametrize(
        "name",
        [
            "Faradfod",
            "Karezer",
            "B.Jamgaon",
            "Rawan (Ct)",
            "Chorhadih/Boirdih",
            "Kilepar-2",
        ],
    )
    def test_normalization_removes_latin_leakage(self, name):
        result = transliterate_name(name)
        assert DEV_RE.match(result), f"Latin leak in {name} -> {result}"
        assert any("\u0900" <= c <= "\u097F" for c in result), f"No Hindi in {result}"

    def test_case_insensitive_transliteration(self):
        assert simple_transliterate("BILASPUR") == simple_transliterate("bilaspur")

    def test_already_hindi_passthrough(self):
        hindi = "रायपुर"
        assert simple_transliterate(hindi) == hindi

    def test_empty_string(self):
        assert simple_transliterate("") == ""

    def test_transliterate_name_delimiters(self):
        assert transliterate_name("Raipur-Bilaspur") == "रायपुर-बिलासपुर"
        assert transliterate_name("Raipur (Bilaspur)") == "रायपुर (बिलासपुर)"


class TestDataQualityGuards:
    def test_hierarchy_is_devanagari_only(self):
        assert HIERARCHY_PATH.exists(), "Hierarchy file missing"
        data = json.loads(HIERARCHY_PATH.read_text())
        issues = []

        def check_text(kind, en_name, hi_value):
            if hi_value and not DEV_RE.match(hi_value):
                issues.append((kind, en_name, hi_value))

        for dist_en, dist in data.items():
            check_text("district", dist_en, dist.get("name_hi", ""))
            for ac_en, ac in dist.get("acs", {}).items():
                check_text("ac", ac_en, ac.get("name_hi", ""))
                for blk_en, blk in ac.get("blocks", {}).items():
                    check_text("block", blk_en, blk.get("name_hi", ""))
                    for v in blk.get("villages", []):
                        check_text("village", v.get("name", ""), v.get("name_hi", ""))
                        check_text("gp", v.get("gp_name", ""), v.get("gp_name_hi", ""))

        assert not issues, f"Found non-Devanagari entries (showing up to 5): {issues[:5]}"
