# Gemini Parser V2 - Production Analysis Report
## 100 Tweet Test Results

### Executive Summary
Parser V2 processed 100 real tweets with **65% average confidence** (target: >90%). Critical gaps identified in location resolution (0% coverage) and event classification (56% marked as "Other").

---

## Performance Metrics

### Confidence Distribution
- **Average**: 65.15%
- **Range**: 50% - 85%
- **>90% confidence**: 0/100 (0.0%) ❌
- **80-90% confidence**: 44/100 (44.0%)
- **<70% confidence**: 56/100 (56.0%) ⚠️

### Feature Coverage
- **Locations**: 0/100 (0.0%) ❌ **CRITICAL ISSUE**
- **People**: 39/100 (39.0%)
  - Avg 1.3 people per tweet
- **Schemes**: 0/100 (0.0%) ❌

### Event Classification
| Event Type | Count | % |
|------------|-------|---|
| अन्य (Other) | 56 | 56% ⚠️ |
| धार्मिक / सांस्कृतिक | 11 | 11% |
| बैठक | 8 | 8% |
| आंतरिक सुरक्षा | 5 | 5% |
| उद्घाटन | 5 | 5% |
| निरीक्षण | 5 | 5% |

---

## Critical Issues Identified

### 🚨 Issue #1: Zero Location Resolution
**Impact**: 100% of tweets have `location_source: "none"`

**Root Causes**:
1. Input data format mismatch - Parser expects `parsed_data_v8` structure but `clean_tweets.jsonl` has raw tweet format
2. Deep-Location Engine not receiving preprocessed location candidates
3. Landmarks/dictionary lookups not being triggered

**Evidence**: All parsing traces show `"location_source": "none"`

### 🚨 Issue #2: Low Confidence Scores
**Impact**: 0% tweets meet >90% target, 56% below 70%

**Root Causes**:
1. Base confidence starts at 0.5 (too low)
2. No location bonus (should add +0.15-0.25)
3. Event classification defaulting to "अन्य" (no confidence boost)
4. People extraction not contributing to confidence

### 🚨 Issue #3: High "Other" Classification
**Impact**: 56% of events classified as generic "अन्य"

**Root Causes**:
1. Event keyword matching too strict
2. Multi-label classifier not aggregating scores properly
3. Missing common event patterns in keyword rules

---

## Improvement Recommendations

### Priority 1: Fix Location Resolution (CRITICAL)
**Actions**:
1. Add input data adapter to handle both raw tweets and parsed_data_v8 format
2. Implement text preprocessing to extract location candidates from raw text
3. Enable landmark matching on raw tweet text
4. Add fallback to constituency/district extraction from author metadata

**Expected Impact**: 60-80% location coverage

### Priority 2: Boost Confidence Scoring
**Actions**:
1. Increase base confidence from 0.5 to 0.65
2. Add location resolution bonus: +0.20
3. Add people extraction bonus: +0.05 per person (max +0.15)
4. Add event classification bonus: +0.10 for non-"अन्य"
5. Reduce "अन्य" penalty to -0.10

**Expected Impact**: Average confidence 80-85%

### Priority 3: Improve Event Classification
**Actions**:
1. Expand keyword rules with more common patterns
2. Implement fuzzy keyword matching (edit distance ≤2)
3. Add context-based classification (e.g., "विधानसभा" + "बैठक" = high confidence)
4. Lower threshold for multi-label scoring from 1.0 to 0.7

**Expected Impact**: Reduce "अन्य" to <30%

### Priority 4: Enhance People Extraction
**Actions**:
1. Fix people_mentioned to return structured objects (not just strings)
2. Add extraction_method tracking
3. Improve honorific patterns for better name boundaries
4. Add VIP list matching with fuzzy search

**Expected Impact**: 50-60% people coverage

---

## Quick Wins (Can implement immediately)

1. **Adjust Base Confidence**: Change line ~580 from `0.5` to `0.65`
2. **Add Event Bonus**: Add +0.10 when event_type != "अन्य"
3. **Fix Input Adapter**: Add check for `text` vs `raw_text` field
4. **Enable Raw Text Parsing**: Extract locations from `text` field directly

---

## Testing Recommendations

After implementing fixes:
1. Rerun on same 100 tweets
2. Target metrics:
   - Avg confidence: >80%
   - Location coverage: >60%
   - "अन्य" classification: <30%
   - People extraction: >50%
3. Compare V2 vs V1 on same dataset
4. Manual review of 10 random samples

---

## Conclusion

Parser V2 has strong foundation (Deep-Location Engine, Entity Resurrection, Multi-Label Classifier) but needs **input data adaptation** and **confidence tuning** to meet production targets. Location resolution is the critical blocker - fixing this will cascade improvements across all metrics.

**Recommended Next Step**: Implement Priority 1 (Location Resolution) first, then retest.
