# Tweet Parsing Plan

This document outlines the plan for parsing over 2700 tweets by leveraging the assets provided in the `KnowledgeBank`.

## Objective
To accurately parse tweets by re-implementing the parsing logic using the pre-built assets and logic from the `KnowledgeBank`.

## Current Status
We are actively working on improving the `parse_v5.py` script. The focus is on enhancing location parsing accuracy by integrating `chhattisgarh_complete_geography.json` and robust alias generation. We are currently integrating `fold_nukta` and `translit_basic` helper functions from `KnowledgeBank/source_code/normalization.py` into `parse_v5.py` to support this goal.

## Phase 1: Asset Ingestion & Setup
The first phase involves loading the necessary data from the `KnowledgeBank` to create a local parsing engine.

1.  **Load Geographic Data:** Ingest `KnowledgeBank/geo-data/chhattisgarh_complete_geography.json`. This will serve as the master database for building correct location hierarchies.
2.  **Load Location Aliases:** Ingest the alias maps from `KnowledgeBank/training-data/learning/`. This will allow for the normalization of different spellings of the same location (e.g., "Kharsiya" -> "खरसिया").
3.  **Load Event Types:** Ingest `KnowledgeBank/parsing-models/event_types.json` to get the master list of all possible event classifications.

## Phase 2: The Parsing Pipeline (`parse_v5.py` Enhancements)
The `parse_v5.py` script will process each tweet, incorporating the following enhancements:

1.  **Normalization Functions:** Integrate `fold_nukta` and `translit_basic` into `parse_v5.py` to create robust variants for location names.
2.  **Location Matching:** Find location names in the tweet, normalize them using the Location Aliases and the new normalization functions, and then look up the full, correct hierarchy in the Geographic Data.
3.  **Event Classification:** Match keywords in the tweet against the master list of Event Types to accurately classify the activity.
4.  **Entity Extraction:** Extract all other required entities (People, Organizations, Dates, Keywords, etc.) as per the original plan.

## Phase 3: Output for Review
For the initial set of 2-3 tweets, the following will be done to gather user feedback before processing the entire dataset.

1.  **Generate Structured Output:** For each of the initial tweets, generate a structured JSON output that matches the format of the examples found in `KnowledgeBank/parsing-models/parsed_tweets.json`.
2.  **Present for Feedback:** The resulting JSON objects will be presented for review and feedback.
