# Project Restructuring Change Log

## 2025-01-25 12:36 - Phase 1: Project Organization Started

### Step 1: Create Archive Structure
**Action**: Created archive/ folder with subdirectories
```bash
mkdir -p archive/docs archive/scripts archive/data
```
**Rollback**: `rm -rf archive/`

---

## Files to Move

### Docs to Archive (Analysis/Design - Not Production)
- parser_v2_analysis_report.md
- parser_v2_refinements_report.md
- parser_v31_final_summary.md
- parsing_issues_report.md
- regression_test_results.md
- user_sample_analysis_report.md
- golden_standard_design.md

### Scripts to Archive (Debug/Analysis - Not Production)
- analyze_golden_failures.py
- analyze_sample_results.py
- debug_landmark.py
- debug_people.py
- generate_gold_standard.py
- generate_refinements_report.py
- identify_parsing_issues.py
- measure_batch1_impact.py
- measure_v21_complete.py
- measure_v25_semantic.py

### Data to Archive (Test/Analysis Data)
- demo_tweets.jsonl
- sample_10_tweets.jsonl
- sample_100_db_tweets.jsonl
- sample_100_real_tweets.jsonl
- user_sample_analysis.jsonl
- parsed_user_sample_v2.jsonl
- semantic_richness_data.py

### Root Files to Archive
- test_output.txt
- test_output_v2.txt

---

## Production Files (Keep in Main Folders)

### Scripts (Production)
- gemini_parser_v2.py (Parser V2.1)
- export_db_tweets.py (DB export)
- test_parser_golden.py (Golden Standard tests)

### Docs (Production)
- PARSER_V2.1_PRODUCTION.md

### Data (Production)
- datasets/ (reference data)
- gold_standard_tweets.csv
- vip_list.json
- db_tweets_for_parser_v2.jsonl
- parsed_tweets_gemini_parser_v2.jsonl

---

## Rollback Instructions

### Full Rollback
```bash
# Restore all files from archive
cp -r archive/docs/* docs/
cp -r archive/scripts/* scripts/
cp -r archive/data/* data/
cp archive/*.txt ./
rm -rf archive/
```

### Partial Rollback (Specific File)
```bash
# Example: Restore specific file
cp archive/docs/parser_v2_analysis_report.md docs/
```

---

## Git Commits
Each phase will be committed separately for easy rollback:
- Commit 1: Archive creation and file moves
- Commit 2: Parser V2.1 integration
- Commit 3: Database update
- Commit 4: Testing implementation
