# Parser V2 Refinements - Analysis Report

## Overview
- **Total Tweets Parsed**: 2,611
- **Average Confidence**: 74.53%
- **High Confidence (>0.9)**: 453 (17.3%)

## Location Resolution Statistics
- **temporal_inference**: 1,848 (70.8%)
- **hierarchy_resolver**: 763 (29.2%)

## Event Classification Statistics
- **अन्य**: 1,399 (53.6%)
- **शुभकामना / बधाई**: 352 (13.5%)
- **धार्मिक / सांस्कृतिक कार्यक्रम**: 181 (6.9%)
- **योजना घोषणा**: 157 (6.0%)
- **बैठक**: 114 (4.4%)
- **आंतरिक सुरक्षा / पुलिस**: 102 (3.9%)
- **राजनीतिक वक्तव्य**: 56 (2.1%)
- **उद्घाटन**: 50 (1.9%)
- **खेल / गौरव**: 49 (1.9%)
- **सम्मान / Felicitation**: 48 (1.8%)

---

# Refinement Examples

## 1. Patna/Bankipur Resolution

**Before**: Patna tweets were incorrectly inferred as Bilaspur via temporal inference.

**After**: Explicit detection via Static Landmarks.

### Example 1
```json
{
  "tweet_id": "1991428224157708480",
  "text": "छत्तीसगढ़ भाजपा के प्रदेश प्रभारी एवं बांकीपुर विधायक माननीय श्री नितिन नबीन जी को बिहार सरकार में कैबिनेट मंत्री के रूप में शपथ ग्रहण करने पर हार्दिक बधाई एवं शुभकामनायें।\n\n@NitinNabin  \n\n#विकसित_बिहार_का_शपथ",
  "created_at": "2025-11-19T21:47:42",
  "author_handle": "OPChoudhary_Ind",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264178",
  "parsed_data_v9": {
    "event_type": "शुभकामना / बधाई",
    "event_date": "2025-11-19",
    "location": {
      "district": "Patna",
      "assembly": [],
      "parliamentary": [],
      "hierarchy_path": [
        "Bihar",
        "Patna"
      ],
      "canonical": "Patna",
      "canonical_key": "CG_DISTRICT_Patna",
      "location_type": "district",
      "source": "hierarchy_resolver",
      "landmark_trigger": "बांकीपुर"
    },
    "people_mentioned": [
      "के रूप में",
      "नितिन नबीन"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.95,
    "parsing_trace": {
      "triggered_keywords": [
        "शुभकामना / बधाई",
        "राजनीतिक वक्तव्य"
      ],
      "location_source": "landmark_oracle",
      "event_score_matrix": {
        "शुभकामना / बधाई": 1,
        "राजनीतिक वक्तव्य": 1
      },
      "timeline_used": false
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "Patna",
      "assembly": [],
      "parliamentary": [],
      "hierarchy_path": [
        "Bihar",
        "Patna"
      ],
      "canonical": "Patna",
      "canonical_key": "CG_DISTRICT_Patna",
      "location_type": "district",
      "source": "hierarchy_resolver",
      "landmark_trigger": "बांकीपुर"
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

### Example 2
```json
{
  "tweet_id": "1991419570394132565",
  "text": "बिहार के मुख्यमंत्री पद की शपथ ग्रहण करने पर माननीय श्री नीतीश कुमार जी और उपमुख्यमंत्री पद की शपथ लेने पर माननीय श्री सम्राट चौधरी जी और माननीय श्री विजय सिन्हा जी को हार्दिक बधाई एवं शुभकामनायें।  \nआदरणीय प्रधानमंत्री श्री नरेंद्र मोदी जी के यशस्वी मार्गदर्शन में 'विकसित बिहार' की दिशा में यह नई शुरुआत प्रदेश को नई ऊँचाइयों तक ले जाये, यही मंगलकामना है।\n@narendramodi @NitishKumar @samrat4bjp @VijayKrSinhaBih @BJP4Bihar",
  "created_at": "2025-11-19T21:13:19",
  "author_handle": "OPChoudhary_Ind",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264178",
  "parsed_data_v9": {
    "event_type": "शुभकामना / बधाई",
    "event_date": "2025-11-19",
    "location": {
      "district": "Patna",
      "assembly": [],
      "parliamentary": [],
      "hierarchy_path": [
        "Bihar",
        "Patna"
      ],
      "canonical": "Patna",
      "canonical_key": "CG_DISTRICT_Patna",
      "location_type": "district",
      "source": "temporal_inference",
      "landmark_trigger": "बांकीपुर",
      "confidence_penalty": 0.4
    },
    "people_mentioned": [
      "नरेंद्र मोदी",
      "नीतीश कुमार",
      "पद की शपथ",
      "विजय सिन्हा",
      "सम्राट चौधरी"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.85,
    "parsing_trace": {
      "triggered_keywords": [
        "शुभकामना / बधाई"
      ],
      "location_source": "temporal_inference",
      "event_score_matrix": {
        "शुभकामना / बधाई": 1
      },
      "timeline_used": true
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "Patna",
      "assembly": [],
      "parliamentary": [],
      "hierarchy_path": [
        "Bihar",
        "Patna"
      ],
      "canonical": "Patna",
      "canonical_key": "CG_DISTRICT_Patna",
      "location_type": "district",
      "source": "temporal_inference",
      "landmark_trigger": "बांकीपुर",
      "confidence_penalty": 0.4
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

## 2. Nava Raipur Landmark Detection

**Before**: 'Vidhan Sabha' resolved to generic 'Raipur'.

**After**: Landmark triggers resolve to specific 'Nava Raipur'.

### Example 1
```json
{
  "tweet_id": "1891387657889997006",
  "text": "आज महानदी भवन, मंत्रालय में वर्ष 2025-26 के बजट व नवीन मद प्रस्तावों पर मंत्री स्तरीय चर्चा के तहत माननीय उप मुख्यमंत्री श्री अरुण साव जी से लोक निर्माण, लोक स्वास्थ्य यांत्रिकी, विधि-विधायी कार्य एवं नगरीय प्रशासन विभाग से संबंधित प्रस्तावों पर चर्चा की।",
  "created_at": "2025-11-13T14:42:51.532000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264152",
  "parsed_data_v9": {
    "event_type": "अन्य",
    "event_date": "2025-11-13",
    "location": {
      "district": "रायपुर",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "नवा रायपुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायपुर जिला",
        "नवा रायपुर"
      ],
      "canonical": "नवा रायपुर",
      "canonical_key": "CG_ULB_नवा रायपुर",
      "location_type": "urban",
      "source": "hierarchy_resolver",
      "landmark_trigger": "मंत्रालय"
    },
    "people_mentioned": [
      "अरुण साव",
      "उप",
      "स्तरीय चर्चा के"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.7,
    "parsing_trace": {
      "triggered_keywords": [],
      "location_source": "landmark_oracle",
      "event_score_matrix": {},
      "timeline_used": false
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "रायपुर",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "नवा रायपुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायपुर जिला",
        "नवा रायपुर"
      ],
      "canonical": "नवा रायपुर",
      "canonical_key": "CG_ULB_नवा रायपुर",
      "location_type": "urban",
      "source": "hierarchy_resolver",
      "landmark_trigger": "मंत्रालय"
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

### Example 2
```json
{
  "tweet_id": "1891439760981283186",
  "text": "आज वर्ष 2025-26 के बजट व नवीन मद प्रस्तावों पर मंत्री स्तरीय चर्चा में माननीय मंत्री श्री केदार कश्यप जी से संसदीय कार्य,वन एवं जलवायु परिवर्तन, जल संसाधन, कौशल विकास, सहकारिता विभागों के संबंध में चर्चा हुई।",
  "created_at": "2025-11-13T14:42:51.531000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264151",
  "parsed_data_v9": {
    "event_type": "अन्य",
    "event_date": "2025-11-13",
    "location": {
      "district": "रायपुर",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "नवा रायपुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायपुर जिला",
        "नवा रायपुर"
      ],
      "canonical": "नवा रायपुर",
      "canonical_key": "CG_ULB_नवा रायपुर",
      "location_type": "urban",
      "source": "temporal_inference",
      "landmark_trigger": "मंत्रालय",
      "confidence_penalty": 0.4
    },
    "people_mentioned": [
      "केदार कश्यप",
      "स्तरीय चर्चा में"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.6,
    "parsing_trace": {
      "triggered_keywords": [],
      "location_source": "temporal_inference",
      "event_score_matrix": {},
      "timeline_used": true
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "रायपुर",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "नवा रायपुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायपुर जिला",
        "नवा रायपुर"
      ],
      "canonical": "नवा रायपुर",
      "canonical_key": "CG_ULB_नवा रायपुर",
      "location_type": "urban",
      "source": "temporal_inference",
      "landmark_trigger": "मंत्रालय",
      "confidence_penalty": 0.4
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

## 3. Sports Event Classification

**New Keywords**: मैच, जीत, पदक, खिलाड़ी, ओलंपिक, match, jeet, medal, won, winner

### Example 1
```json
{
  "tweet_id": "1890431461016080876",
  "text": "भारत वर्ष 2036 में ओलंपिक की मेजबानी के लिए तैयार है।",
  "created_at": "2025-11-13T14:42:51.567000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264171",
  "parsed_data_v9": {
    "event_type": "खेल / गौरव",
    "event_date": "2025-11-13",
    "location": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    },
    "people_mentioned": [],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.85,
    "parsing_trace": {
      "triggered_keywords": [
        "खेल / गौरव"
      ],
      "location_source": "temporal_inference",
      "event_score_matrix": {
        "खेल / गौरव": 2
      },
      "timeline_used": true
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

### Example 2
```json
{
  "tweet_id": "1890645345245266055",
  "text": "लैलूंगा नगर पंचायत में भाजपा अध्यक्ष प्रत्याशी श्री कपिल सिंघानिया जी को 2484 वोटों से शानदार जीत पर हार्दिक बधाई एवं शुभकामनायें। https://t.co/4nuA28NXZo",
  "created_at": "2025-11-13T14:42:51.561000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264168",
  "parsed_data_v9": {
    "event_type": "खेल / गौरव",
    "event_date": "2025-11-13",
    "location": {
      "district": "रायगढ़",
      "assembly": "लैलूंगा",
      "parliamentary": "रायगढ़ (एसटी)",
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "लैलूंगा",
      "ulb_type": "ULB",
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायगढ़ जिला",
        "लैलूंगा"
      ],
      "canonical": "लैलूंगा",
      "canonical_key": "CG_ULB_लैलूंगा",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    },
    "people_mentioned": [
      "कपिल सिंघानिया",
      "प्रत्याशी"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.95,
    "parsing_trace": {
      "triggered_keywords": [
        "खेल / गौरव",
        "शुभकामना / बधाई",
        "राजनीतिक वक्तव्य"
      ],
      "location_source": "hierarchy_resolver",
      "event_score_matrix": {
        "खेल / गौरव": 2,
        "शुभकामना / बधाई": 1,
        "राजनीतिक वक्तव्य": 1
      },
      "timeline_used": false
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "रायगढ़",
      "assembly": "लैलूंगा",
      "parliamentary": "रायगढ़ (एसटी)",
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "लैलूंगा",
      "ulb_type": "ULB",
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायगढ़ जिला",
        "लैलूंगा"
      ],
      "canonical": "लैलूंगा",
      "canonical_key": "CG_ULB_लैलूंगा",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

## 4. Security Event Classification

**New Keywords**: नक्सल, माओवाद, शहीद, जवान, encounter, naxal, maowad, shahid

### Example 1
```json
{
  "tweet_id": "1892074220844097819",
  "text": "आदरणीय प्रधानमंत्री श्री नरेंद्र मोदी जी व माननीय केंद्रीय गृह मंत्री श्री अमित शाह जी के दृढ़ संकल्प से छत्तीसगढ़ में माओवाद अंतिम सांस गिन रहा है। पंचायत चुनावों में ग्रामीणों ने निर्भीक होकर लोकतंत्र का समर्थक किया। प्रदेश का गौरव लौट रहा है।",
  "created_at": "2025-11-13T14:42:51.521000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264142",
  "parsed_data_v9": {
    "event_type": "आंतरिक सुरक्षा / पुलिस",
    "event_date": "2025-11-13",
    "location": {
      "district": "रायगढ़",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "रायगढ़",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायगढ़ जिला",
        "रायगढ़"
      ],
      "canonical": "रायगढ़",
      "canonical_key": "CG_ULB_रायगढ़",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    },
    "people_mentioned": [
      "अमित शाह",
      "केंद्रीय गृह",
      "नरेंद्र मोदी"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.85,
    "parsing_trace": {
      "triggered_keywords": [
        "आंतरिक सुरक्षा / पुलिस",
        "चुनाव प्रचार"
      ],
      "location_source": "temporal_inference",
      "event_score_matrix": {
        "आंतरिक सुरक्षा / पुलिस": 2,
        "चुनाव प्रचार": 1
      },
      "timeline_used": true
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "रायगढ़",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "रायगढ़",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "रायगढ़ जिला",
        "रायगढ़"
      ],
      "canonical": "रायगढ़",
      "canonical_key": "CG_ULB_रायगढ़",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

### Example 2
```json
{
  "tweet_id": "1894932636499616131",
  "text": "मां भारती के वीर सपूत अमर शहीद चंद्रशेखर आजाद जी की पुण्यतिथि पर कोटि-कोटि नमन। देश की स्वतंत्रता के लिए अपना सर्वस्व न्योछावर करने वाले इस महानायक का साहस व बलिदान हर भारतीय के हृदय में सदैव जीवित रहेगा।",
  "created_at": "2025-11-13T14:42:51.469000",
  "author_handle": "opchoudhary",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264109",
  "parsed_data_v9": {
    "event_type": "आंतरिक सुरक्षा / पुलिस",
    "event_date": "2025-11-13",
    "location": {
      "district": "गरियाबंद",
      "assembly": "राजिम",
      "parliamentary": "महासमुंद",
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "राजिम",
      "ulb_type": "ULB",
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "गरियाबंद जिला",
        "राजिम"
      ],
      "canonical": "राजिम",
      "canonical_key": "CG_ULB_राजिम",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    },
    "people_mentioned": [],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.85,
    "parsing_trace": {
      "triggered_keywords": [
        "आंतरिक सुरक्षा / पुलिस"
      ],
      "location_source": "temporal_inference",
      "event_score_matrix": {
        "आंतरिक सुरक्षा / पुलिस": 2
      },
      "timeline_used": true
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "गरियाबंद",
      "assembly": "राजिम",
      "parliamentary": "महासमुंद",
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "राजिम",
      "ulb_type": "ULB",
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "गरियाबंद जिला",
        "राजिम"
      ],
      "canonical": "राजिम",
      "canonical_key": "CG_ULB_राजिम",
      "location_type": "urban",
      "source": "temporal_inference",
      "confidence_penalty": 0.4
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

## 5. Improved People Extraction

**Improvements**:
- Chained honorifics (e.g., 'Mananiya Mukhyamantri Shri')
- Added 'महोदया', 'महोदय' to prevent extraction of 'Mahodaya ka Chhattisgarh'
- Handles excluded from people_mentioned (used only for inference)

### Example 1
```json
{
  "tweet_id": "1991470463206527328",
  "text": "आज अंबिकापुर में महामहिम राष्ट्रपति श्रीमती द्रौपदी मुर्मु जी के मुख्य आतिथ्य में आयोजित जनजातीय गौरव दिवस समारोह में आदरणीय केंद्रीय राज्य जनजातीय कार्य मंत्री श्री दुर्गा दास उइके जी, माननीय राज्यपाल श्री रमेन डेका जी, माननीय मुख्यमंत्री श्री विष्णु देव साय जी एवं माननीय केंद्रीय राज्य मंत्री श्री तोखन साहू जी के साथ सम्मिलित होना अत्यंत गर्व का विषय रहा।\nराष्ट्रपति महोदया का छत्तीसगढ़ के जनजातीय समाज के प्रति स्नेह, आत्मीयता और संवेदनशीलता ने इस दिवस की गरिमा को और भव्य बना दिया।\n\nइस अवसर पर भाजपा प्रदेश अध्यक्ष माननीय श्री किरण सिंह देव जी, कैबिनेट के साथीगण सहित अन्य गणमान्य उपस्थित रहे।\n\n@rashtrapatibhvn @DdUikey\n@vishnudsai @ramendeka16\n@tokhansahu_bjp @KiranDeoBJP\n@ramvicharnetam @KedarKashyapBJP\n\n#JanjatiyaGauravDiwas #Ambikapur #PresidentOfIndia",
  "created_at": "2025-11-20T00:35:32",
  "author_handle": "OPChoudhary_Ind",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264179",
  "parsed_data_v9": {
    "event_type": "धार्मिक / सांस्कृतिक कार्यक्रम",
    "event_date": "2025-11-20",
    "location": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    },
    "people_mentioned": [
      "का छत्तीसगढ़ के",
      "किरण सिंह देव",
      "केंद्रीय राज्य",
      "तोखन साहू",
      "दुर्गा दास उइके",
      "द्रौपदी मुर्मु",
      "रमेन डेका",
      "विष्णु देव साय"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.95,
    "parsing_trace": {
      "triggered_keywords": [
        "धार्मिक / सांस्कृतिक कार्यक्रम",
        "राजनीतिक वक्तव्य"
      ],
      "location_source": "hierarchy_resolver",
      "event_score_matrix": {
        "धार्मिक / सांस्कृतिक कार्यक्रम": 1,
        "राजनीतिक वक्तव्य": 1
      },
      "timeline_used": false
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

### Example 2
```json
{
  "tweet_id": "1991433908383060049",
  "text": "जनजातीय गौरव दिवस समारोह 2025 के अवसर पर अंबिकापुर में आयोजित कार्यक्रम में महामहिम राष्ट्रपति श्रीमती द्रौपदी मुर्मू जी, आदरणीय केंद्रीय राज्य जनजातीय कार्य मंत्री श्री दुर्गा दास उइके जी, माननीय राज्यपाल श्री रमेन डेका जी, माननीय मुख्यमंत्री श्री विष्णु देव साय जी, माननीय सांसद श्री चिंतामणि महाराज जी तथा मंत्रिमंडल के सदस्यों के साथ सामूहिक चित्र।\n@rashtrapatibhvn @DdUikey @ramendeka16 @vishnudsai",
  "created_at": "2025-11-19T22:10:17",
  "author_handle": "OPChoudhary_Ind",
  "processing_status": "pending",
  "fetched_at": "2025-11-21T19:31:30.264178",
  "parsed_data_v9": {
    "event_type": "धार्मिक / सांस्कृतिक कार्यक्रम",
    "event_date": "2025-11-19",
    "location": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    },
    "people_mentioned": [
      "चिंतामणि महाराज",
      "दुर्गा दास उइके",
      "द्रौपदी मुर्मू",
      "रमेन डेका",
      "विष्णु देव साय"
    ],
    "schemes_mentioned": [],
    "target_groups": [],
    "communities": [],
    "organizations": [],
    "confidence": 0.95,
    "parsing_trace": {
      "triggered_keywords": [
        "धार्मिक / सांस्कृतिक कार्यक्रम"
      ],
      "location_source": "hierarchy_resolver",
      "event_score_matrix": {
        "धार्मिक / सांस्कृतिक कार्यक्रम": 1
      },
      "timeline_used": false
    },
    "model_version": "gemini-parser-v2",
    "geo_hierarchy": {
      "district": "सरगुजा",
      "assembly": null,
      "parliamentary": null,
      "block": null,
      "gp": null,
      "village": null,
      "ulb": "अंबिकापुर",
      "ulb_type": null,
      "ward": null,
      "zone": null,
      "hierarchy_path": [
        "छत्तीसगढ़",
        "सरगुजा जिला",
        "अंबिकापुर"
      ],
      "canonical": "अंबिकापुर",
      "canonical_key": "CG_ULB_अंबिकापुर",
      "location_type": "urban",
      "source": "hierarchy_resolver"
    }
  },
  "metadata_v9": {
    "model": "gemini-parser-v2",
    "version": "2.0.0"
  }
}
```

