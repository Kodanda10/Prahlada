# Project Dhruv API Documentation

## Overview

Project Dhruv provides a comprehensive REST API for social media analytics, cognitive processing, and human-reviewed corrections (overlay service). The API is built with FastAPI and supports JWT authentication for protected endpoints.

## Base URL
```
https://api.dhruv.project/
```

## Authentication

### JWT Token Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Login Endpoint

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-123",
    "username": "admin",
    "roles": ["admin"],
    "display_name": "Administrator",
    "email": "admin@dhruv.project"
  }
}
```

### Token Verification

```http
GET /api/auth/verify
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user-123",
  "username": "admin",
  "roles": ["admin"],
  "display_name": "Administrator",
  "email": "admin@dhruv.project"
}
```

---

## Public Endpoints

### Root Health Check

```http
GET /
```

**Response:**
```json
{
  "status": "Project Dhruv API is running"
}
```

### UI Configuration

```http
GET /config
```

**Response:**
```json
{
  "titles": {
    "app_title": "सोशल मीडिया एनालिटिक्स",
    "app_subtitle": "छत्तीसगढ़ शासन",
    "home_tab": "होम",
    "review_tab": "समीक्षा",
    "analytics_tab": "एनालिटिक्स",
    "control_hub_tab": "कंट्रोल हब"
  },
  "modules": {
    "analytics": true,
    "review": true,
    "control_hub": true
  }
}
```

### System Health

```http
GET /health/system
```

**Response:**
```json
{
  "status": "healthy",
  "cpu_usage": 45.2,
  "memory_usage": 60.1,
  "memory_total_gb": 16,
  "parser_uptime_seconds": 3600,
  "p95_latency_ms": 120,
  "api_error_rate": 0.5,
  "services": {
    "ollama": {"status": "up", "details": "Running"},
    "cognitive_engine": {"status": "up", "details": "Ready"},
    "database_file": {"status": "up", "details": "Connected"},
    "mapbox_integration": {"status": "up", "details": "Active"}
  }
}
```

### Analytics Health

```http
GET /health/analytics
```

**Response:**
```json
{
  "data_freshness": {
    "status": "fresh",
    "last_updated": 1703123456,
    "source": "PostgreSQL"
  },
  "modules": {
    "controlhub_header_systemhealth": {"status": "fresh", "cache_hit": true},
    "controlhub_grid_analytics_sync": {"status": "fresh", "cache_hit": false}
  }
}
```

---

## Protected Endpoints

### Statistics

Get real-time summary statistics from the database.

```http
GET /api/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_tweets": 1250,
  "parsed_success": 1180,
  "pending": 45,
  "errors": 25
}
```

### Events

Retrieve parsed events with optional status filtering.

```http
GET /api/events?status=success
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by processing status
  - `success` / `processed` / `completed`: Successfully processed tweets
  - `pending`: Tweets awaiting processing
  - `failed` / `error`: Tweets that failed processing

**Response:**
```json
[
  {
    "tweet_id": "tweet-001",
    "created_at": "2024-01-15T10:30:00Z",
    "raw_text": "मुख्यमंत्री ने रायपुर में विकास कार्यों की समीक्षा की।",
    "clean_text": "मुख्यमंत्री ने रायपुर में विकास कार्यों की समीक्षा की।",
    "event_type": ["review_meeting"],
    "location_text": "Raipur, Chhattisgarh",
    "scheme_tags": ["infrastructure"],
    "parsing_status": "SUCCESS",
    "logs": ["parsed_at=2024-01-15T10:35:00Z"]
  }
]
```

### Analytics Data

Get aggregated data for analytics charts.

```http
GET /api/analytics/{chart_type}
Authorization: Bearer <token>
```

**Path Parameters:**
- `chart_type`: Type of analytics data
  - `event-types`: Event type distribution
  - `districts`: Location/district distribution

**Response:**
```json
[
  {"name": "review_meeting", "value": 45},
  {"name": "inauguration", "value": 32},
  {"name": "protest", "value": 18}
]
```

### Tweet Ingestion

Ingest parsed tweet data from the parsing pipeline.

```http
POST /api/ingest-parsed-tweet
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "tweet": {
    "id": "tweet-123",
    "text": "मुख्यमंत्री ने रायपुर में अस्पताल का उद्घाटन किया।",
    "created_at": "2024-01-15T14:30:00Z",
    "author_id": "user-456"
  },
  "categories": {
    "event": ["inauguration"],
    "locations": ["Raipur", "Chhattisgarh"],
    "people": ["Chief Minister"],
    "schemes": ["PM Awas Yojana"],
    "organisations": ["State Government"]
  },
  "gemini_metadata": {
    "model": "gemini-pro",
    "confidence": 0.92
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data for tweet tweet-123 ingested."
}
```

### Vector Indexing

Trigger batch indexing of tweets for semantic search.

```http
POST /api/vector/trigger-batch-indexing
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "tweetIds": ["tweet-001", "tweet-002", "tweet-003"]
}
```

**Response:**
```json
{
  "status": "success",
  "service": "faiss",
  "message": "Indexing triggered for 3 items."
}
```

### Cognitive Correction

Trigger the cognitive reasoning engine to analyze and learn from corrections.

```http
POST /api/cognitive/correct
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "tweet_id": "tweet-123",
  "text": "मुख्यमंत्री ने रायपुर में अस्पताल का उद्घाटन किया।",
  "old_data": {
    "event_type": "meeting",
    "location": "Raipur"
  },
  "correction": {
    "event_type": "inauguration",
    "location": "Raipur, Chhattisgarh"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "log_id": "cognitive-log-001",
  "decision": {
    "action": "approve",
    "confidence": 0.95
  },
  "details": {
    "reasoning": "Valid correction pattern detected",
    "improvement_suggestions": ["Better location parsing"]
  }
}
```

### Event Approval

Mark a parsed event as approved after human review.

```http
POST /api/events/{tweet_id}/approve
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Event tweet-123 approved"
}
```

### Semantic Search

Perform semantic search on indexed tweets.

```http
POST /api/search
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "मुख्यमंत्री विकास कार्य",
  "k": 10
}
```

**Response:**
```json
[
  {
    "tweet_id": "tweet-001",
    "text": "मुख्यमंत्री ने रायपुर में विकास कार्यों की समीक्षा की।",
    "score": 0.15,
    "metadata": {
      "tweet_id": "tweet-001",
      "text": "मुख्यमंत्री ने रायपुर में विकास कार्यों की समीक्षा की।"
    }
  }
]
```

### Telemetry Logging

Log frontend telemetry events (no authentication required).

```http
POST /api/telemetry
Content-Type: application/json
```

**Request Body:**
```json
{
  "type": "ui_interaction",
  "name": "button_click",
  "data": {
    "page": "analytics",
    "element": "export_button",
    "timestamp": 1703123456789
  }
}
```

**Response:**
```json
{
  "status": "success"
}
```

---

## Overlay Service API

The Overlay Service provides human-reviewed corrections without modifying original parser data.

### Add Overlay Correction

```http
POST /api/overlay/add
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "tweet_id": "tweet-123",
  "field": "event_type",
  "corrected_value": "inauguration",
  "reviewer_id": "reviewer-456",
  "reviewer_name": "Dr. Sharma",
  "notes": "Corrected from meeting to inauguration based on context"
}
```

**Response:**
```json
{
  "status": "success",
  "overlay": {
    "id": "overlay_tweet-123_event_type_1703123456",
    "tweet_id": "tweet-123",
    "field": "event_type",
    "corrected_value": "inauguration",
    "reviewer_id": "reviewer-456",
    "reviewer_name": "Dr. Sharma",
    "confidence": 1.0,
    "notes": "Corrected from meeting to inauguration based on context",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Overlays for Tweet

```http
GET /api/overlay/tweet/{tweet_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "overlay_tweet-123_event_type_1703123456",
    "tweet_id": "tweet-123",
    "field": "event_type",
    "corrected_value": "inauguration",
    "reviewer_id": "reviewer-456",
    "reviewer_name": "Dr. Sharma",
    "source": "human_review",
    "confidence": 1.0,
    "notes": "Corrected from meeting to inauguration based on context",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Apply Overlay Corrections

```http
POST /api/overlay/apply
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "tweet_id": "tweet-123",
  "parsed_data": {
    "event_type": "meeting",
    "location": "Raipur",
    "schemes": ["infrastructure"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "corrected_data": {
    "event_type": "inauguration",
    "location": "Raipur",
    "schemes": ["infrastructure"]
  },
  "applied_overlays": 1
}
```

### Get Overlay Statistics

```http
GET /api/overlay/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_overlays": 156,
  "tweets_with_overlays": 89,
  "field_distribution": {
    "event_type": 67,
    "location": 45,
    "schemes": 23,
    "people": 21
  },
  "reviewer_distribution": {
    "reviewer-456": 89,
    "reviewer-789": 45,
    "reviewer-101": 22
  }
}
```

### Clear Overlays for Tweet

```http
DELETE /api/overlay/tweet/{tweet_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "removed_overlays": 3
}
```

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error
- `503`: Service Unavailable

---

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- Authenticated endpoints: 1000 requests per hour
- Public health endpoints: 100 requests per minute
- Telemetry endpoint: 1000 requests per minute

---

## Data Models

### AuthRequest
```typescript
{
  username: string;
  password: string;
}
```

### AuthResponse
```typescript
{
  token: string;
  user: AuthUser;
}
```

### AuthUser
```typescript
{
  id: string;
  username: string;
  roles: string[];
  display_name: string;
  email: string;
}
```

### EventResponse
```typescript
{
  tweet_id: string;
  created_at: string;
  raw_text: string;
  clean_text: string;
  event_type: string[];
  location_text: string;
  scheme_tags: string[];
  parsing_status: string;
  logs: string[];
}
```

### SearchResult
```typescript
{
  tweet_id: string;
  text: string;
  score: number;
  metadata: Record<string, any>;
}
```

### OverlayRecord
```typescript
{
  id: string;
  tweet_id: string;
  field: string;
  corrected_value: any;
  reviewer_id: string;
  reviewer_name?: string;
  source: string;
  confidence: number;
  notes?: string;
  created_at: string;
}
```

---

## WebSocket Support

Real-time updates are available via WebSocket connections:

```
ws://api.dhruv.project/ws/events
```

**Supported message types:**
- `tweet_ingested`: New tweet processed
- `overlay_applied`: Human correction applied
- `cognitive_learning`: AI model updated

---

## SDKs and Libraries

### JavaScript/TypeScript Client

```bash
npm install @dhruv-project/api-client
```

```typescript
import { DhruvAPI } from '@dhruv-project/api-client';

const client = new DhruvAPI({
  baseURL: 'https://api.dhruv.project',
  token: 'your-jwt-token'
});

// Get statistics
const stats = await client.getStats();

// Search tweets
const results = await client.searchTweets('मुख्यमंत्री', 10);
```

### Python Client

```bash
pip install dhruv-api-client
```

```python
from dhruv_api import DhruvAPI

client = DhruvAPI(
    base_url='https://api.dhruv.project',
    token='your-jwt-token'
)

# Get events
events = client.get_events(status='success')

# Add overlay correction
overlay = client.add_overlay(
    tweet_id='tweet-123',
    field='event_type',
    corrected_value='inauguration'
)
```

---

## Changelog

### v1.0.0 (Current)
- Initial release with core API functionality
- JWT authentication system
- Cognitive reasoning engine integration
- Overlay service for human corrections
- Vector search capabilities
- Comprehensive analytics endpoints

---

## Support

For API support and questions:
- Documentation: https://docs.dhruv.project
- Issues: https://github.com/project-dhruv/api/issues
- Email: api-support@dhruv.project

---

*This documentation is automatically generated and kept in sync with the API implementation.*