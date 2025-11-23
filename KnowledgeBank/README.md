# 🧠 KnowledgeBank - Project Prahlada Transfer Assets

This KnowledgeBank contains all critical assets from Project Dhruv that are essential for building Project Prahlada's parsing, ingestion, and geo-mapping capabilities.

## 📁 Directory Structure

### `/geo-data/` - Geographic Datasets
- `chhattisgarh_complete_geography.json` - Complete Chhattisgarh geography with full hierarchy (districts → blocks → gram panchayats → villages)
- `raigarh_assembly_constituency_detailed.json` - Detailed Raigarh Assembly Constituency data
- `Chhattisgarh_District_Vidhansabha List.xlsx` - District to Vidhansabha constituency mapping
- `cg_filters_hierarchy.json` - Location filtering hierarchy
- `CG_Geo_*.xlsx` - Source Excel files for Chhattisgarh geography
- `CG_Urban_Geo_*.xlsx` - Urban geography data

### `/parsing-models/` - Parsing Models & Examples
- `event_types.json` - Event classification types (Political Rally, Protest, etc.)
- `parsed_tweets.json` - Example parsed tweets with all extracted fields

### `/training-data/` - Machine Learning Training Data
- `learning/` - Complete learning directory with:
  - `alias_maps_*.json` - Location name aliases and mappings
  - `prompt_exemplars_*.json` - AI training examples
  - `rule_weights_*.json` - Learned parsing rules

### `/vector-search/` - FAISS Vector Search
- `embeddings/` - Complete FAISS embeddings directory:
  - `multilingual_geography/faiss_index.bin` - FAISS vector index
  - `multilingual_geography/locations.json` - Location metadata
  - `multilingual_geography/embeddings.npy` - Vector embeddings

### `/source-code/` - Core Implementation Code
- **Python Parsing Pipeline:**
  - `orchestrator.py` - Main parsing orchestrator
  - `location_matcher.py` - Location matching engine
  - `event_classifier.py` - Event type classification
  - `scheme_detector.py` - Government scheme detection
  - `semantic_location_linker.py` - FAISS-powered location linking
  - `preprocessor.py` - Text preprocessing
  - `normalization.py` - Text normalization utilities

- **Search & Indexing:**
  - `faiss_search_script.py` - FAISS search bridge for Next.js
  - `populate_milvus_multilingual.py` - Milvus vector database setup

- **TypeScript Components:**
  - `gazetteer.ts` - Location gazetteer management
  - `resolver.ts` - Location resolution API
  - `normalize.ts` - Location name normalization
  - `search.ts` - FAISS search interface
  - `config.ts` - FAISS configuration
  - `milvus/` - Milvus integration components

## 🎯 Mapping to Prahlada Requirements

| Prahlada Requirement | KnowledgeBank Assets |
|---------------------|---------------------|
| **Geo-Location Extraction** | `chhattisgarh_complete_geography.json`, `location_matcher.py`, `semantic_location_linker.py` |
| **Event Type Classification** | `event_types.json`, `event_classifier.py`, `orchestrator.py` |
| **Date Extraction** | `orchestrator.py` (date patterns) |
| **Entity Extraction (People, Orgs)** | `parsed_tweets.json`, parsing pipeline |
| **Keyword/Bucket Extraction** | Learning data, alias maps |
| **Vector Search** | FAISS embeddings, search scripts |
| **Geo-Hierarchy** | Complete geography JSON files |

## 🚀 How to Use in Prahlada

1. **Copy this entire `KnowledgeBank` folder** to your Project Prahlada root directory
2. **Set up data directory:** Copy `/geo-data/` contents to `prahlada/data/`
3. **Configure vector search:** Copy `/vector-search/embeddings/` to `prahlada/data/embeddings/`
4. **Adapt parsing code:** Use `/source-code/` Python files as templates for your parsing pipeline
5. **Initialize FAISS:** Use the FAISS scripts to set up location search in Prahlada

## ⚠️ Important Notes

- **Do not modify** the original files in Project Dhruv - this KnowledgeBank is a read-only copy
- **Preserve file structure** when copying to Prahlada
- **Test thoroughly** after integration - especially the FAISS embeddings path references
- **Update import paths** in source code to match Prahlada's project structure

## 📞 Support

This KnowledgeBank provides the complete foundation for Prahlada's parsing capabilities. The FAISS multilingual embeddings and complete Chhattisgarh geography hierarchy are your most valuable assets for accurate location matching in Hindi/English mixed content.