# API Reference: Project Prahlada

## Overview
This document outlines the key API endpoints for the Project Prahlada dashboard, including the new Cognitive Engine integrations.

## Base URL
`http://localhost:8000`

## Authentication
Most endpoints require a Bearer token.
Header: `Authorization: Bearer <token>`

---

## 1. Review & Arbitration

### `GET /api/events`
Fetches a list of events for review.
- **Query Params**: `limit` (default 50), `offset`
- **Response**: List of `ParsedEvent` objects, merged with `EnrichedItem` data if available.

### `GET /api/review/compare`
Fetches detailed comparison data for a specific tweet.
- **Query Params**: `tweet_id` (required)
- **Response**:
  ```json
  {
    "tweet_id": "123",
    "comparison": {
      "event_type": {
        "parser": { "value": "Rally", "confidence": 0.8 },
        "llm": { "value": "Public Meeting", "confidence": 0.95 },
        "conflict": true
      },
      ...
    }
  }
  ```

### `POST /api/events/approve`
Approves a tweet and saves the "Golden Record".
- **Body**:
  ```json
  {
    "tweet_id": "123",
    "final_data": { ... },
    "feedback": { ... },
    "exclude_from_analytics": false
  }
  ```

---

## 2. Cognitive Engine (NLQ)

### `POST /api/nlq/ask`
Ask a natural language question to the system.
- **Body**: `{"query": "What are the new schemes in Raipur?"}`
- **Response**:
  ```json
  {
    "query": "...",
    "answer": "The new schemes are...",
    "sources": [ ... ]
  }
  ```

---

## 3. Analytics

### `GET /api/analytics/dashboard`
Fetches aggregated data for the dashboard charts.
- **Filters**: Only includes tweets with `review_status = 'approved'`.
- **Response**:
  - `event_counts`: By category
  - `location_counts`: By district
  - `timeline`: Daily counts

---

## 4. Overlays (Maps)

### `GET /api/overlay/geojson`
Fetches GeoJSON data for map visualization.
- **Query Params**: `layer` (district, assembly)
- **Response**: Standard GeoJSON FeatureCollection.
