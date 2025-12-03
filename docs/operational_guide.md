# Operational Guide: Project Prahlada

## Overview
Project Prahlada is a dual-pipeline social media analytics system designed for Chhattisgarh. It combines a deterministic Regex Parser (V2) with a state-of-the-art LLM Cognitive Engine (Gemma 3) to provide deep insights into political discourse.

## System Architecture

### 1. Ingestion Layer
- **Source**: Twitter (X) API / Mock Data
- **Script**: `scripts/ingest_lite.py`
- **Storage**: `raw_tweets` table

### 2. Processing Layer (Dual Pipeline)

#### Pipeline A: V2 Regex Parser (Fast, Deterministic)
- **Script**: `scripts/gemini_parser_v2.py`
- **Output**: `parsed_events` table
- **Focus**: Location hierarchy, basic categorization, keyword extraction.

#### Pipeline B: Gemma 3 Cognitive Engine (Deep, Contextual)
- **Script**: `scripts/run_batch_enrichment.py`
- **Output**: `enriched_items` table
- **Focus**: Sentiment, 7-layer cognitive analysis, thematic extraction, Hindi summarization.

### 3. Analytics & Review Layer
- **Backend**: FastAPI (`backend/main.py`)
- **Frontend**: React Dashboard (`pages/Review.tsx`)
- **Features**:
    - **Review Tab**: Side-by-side comparison of Parser vs LLM.
    - **Analytics**: Charts based on approved "Golden Record" data.
    - **Ask AI**: NLQ powered by RAG over `enriched_items`.

## Daily Operations

### 1. Ingest Data
```bash
# Fetch latest tweets
./venv/bin/python scripts/ingest_lite.py
```

### 2. Run V2 Parser
```bash
# Parse raw tweets
./venv/bin/python scripts/gemini_parser_v2.py
```

### 3. Run Gemma 3 Enrichment
```bash
# Enrich pending tweets (requires M4 Mac Mini or GPU)
./venv/bin/python scripts/run_batch_enrichment.py --limit 50
```

### 4. Update Search Index (for Ask AI)
```bash
# Generate embeddings for new enriched items
./venv/bin/python scripts/generate_embeddings.py
```

### 5. Start Dashboard
```bash
# Backend
./venv/bin/python backend/main.py

# Frontend (in separate terminal)
npm run dev
```

## Troubleshooting

### Enrichment Stalled
- Check `data/gemma3_enrichment.log`.
- Ensure no other MLX process is hogging memory.
- Restart the script (it is idempotent).

### Ask AI Not Answering
- Verify `data/embeddings/multilingual_geography/faiss_index.bin` exists.
- Run `scripts/generate_embeddings.py` to refresh the index.

### Dashboard Data Missing
- Check `review_status` in `parsed_events`. Only 'approved' events show in Analytics.
- Use `scripts/check_counts_proper.py` to verify database counts.
