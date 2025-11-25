# Regression Testing Results - People Extraction Noise Fix

## Quick Win Summary
**Objective**: Reduce people extraction noise by filtering common non-name phrases

## Results

### Before Fix
- **Total Issues**: 703
- **People Extraction Noise**: 67 instances
- **Golden Standard**: 100% pass (100/100)

### After Fix
- **Total Issues**: 648 (-55, **7.8% reduction**)
- **People Extraction Noise**: 12 instances (-55, **82% reduction**)
- **Golden Standard**: 84% pass (84/100) ⚠️ **REGRESSION**

## People Noise Reduction Details

### Noise Eliminated (55 instances)
- "उप" (Deputy) - 24 occurrences → 0
- "के रूप में" (in the form of) - 7 occurrences → 0
- "के लोकप्रिय" (of popular) - 5 occurrences → 0
- "प्रत्याशी" (Candidate) - 1 occurrence → 0
- 18 other exact-match noise phrases

### Remaining Noise (12 instances)
New patterns not in original stopwords:
- "का पौधा रोपा।" (planted a tree)
- "के पूर्व" (former)
- "क्षेत्र के" (of area)
- "में रिकॉर्ड पांच" (record five in)
- 8 other unique phrases

## Golden Standard Regression Analysis

**16 failures** introduced by stopwords filter. Need to investigate:
1. Are these legitimate names being filtered?
2. Or are the Golden Standard expectations incorrect?

### Next Steps
1. **Investigate 16 Golden Standard failures** - identify which names are being incorrectly filtered
2. **Refine stopwords list** - remove any entries causing false positives
3. **Re-test** until Golden Standard returns to 100%
4. **Expand stopwords** - add the 12 remaining noise patterns
5. **Move to next issue category** - Location Detection (622 instances)

## Implementation Details

### Code Changes
- File: `scripts/gemini_parser_v2.py`
- Method: `EntityExtractorV2.extract_people()`
- Added: 24-item stopwords set with exact-match filtering
- Strategy: Conservative (exact matches only, no regex patterns)

### Stopwords Added
```python
noise_stopwords = {
    "उप", "प्रत्याशी", "के रूप में", "के लोकप्रिय",
    "निवास में", "के समिति कक्ष", "का छत्तीसगढ़ के",
    "में नगर निगम", "के लिए निकल", "में वित्तीय वर्ष",
    "में बजट प्रस्तुत", "में प्रस्तुत किया", "में नेता प्रतिपक्ष",
    "का बयान देखिये", "में उत्कृष्ट कार्य", "के पूर्व नेता",
    "के कोड़ातराई मंडल", "के विरुद्ध भूपेश", "के तौर पर",
    "से सम्मानित होने", "स्तरीय चर्चा के", "स्तरीय चर्चा में",
    "का छत्तीसगढ़", "महोदया का छत्तीसगढ़ के"
}
```

## Recommendation

**PAUSE** on adding more stopwords until Golden Standard regression is resolved. The 82% noise reduction is excellent, but we must maintain 100% Golden Standard accuracy as our quality gate.

**Action Required**: Debug the 16 Golden Standard failures to understand if they are:
- False positives (valid names being filtered) → Remove from stopwords
- True negatives (Golden Standard expectations wrong) → Update Golden Standard
