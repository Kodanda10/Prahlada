# Database Architecture - Project Prahlada

> [!CAUTION]
> **GUARDRAIL: NO AGENT MAY DELETE ANY TWEET DATA**
> All operations must use `ON CONFLICT DO UPDATE` or `ON CONFLICT DO NOTHING`.
> No `DELETE` or `TRUNCATE` commands allowed on tweet tables.

---

## Single Source of Truth

**Primary Database:** PostgreSQL (via Docker)

```
Host: postgres (Docker) / localhost:5432 (host machine)
Database: dhruv_db
Username: dhruv
Password: dhruv123
```

### Active Tables

| Table | Purpose | Records |
|-------|---------|---------|
| `raw_tweets` | Original tweet text | 2,611 |
| `parsed_events` | Extracted structured data (v8) | 2,611 |
| `enriched_items` | Gemma 3 deep analysis | 2,611 |
| `geo_locations` | Canonical location catalogue | - |
| `admin_users` | Dashboard authentication | 1 |

---

## Legacy Files (Reference Only)

These files exist for backup/reference but are NOT the source of truth:

| File | Purpose | Status |
|------|---------|--------|
| `data/parsed_tweets_v8.jsonl` | JSONL export (2,611 tweets) | Backup |
| `backend/dhruv.db` | Empty SQLite (not used) | Deprecated |
| `data/processed/chhattisgarh_geo.sqlite` | Geo hierarchy data | Active (geo only) |

---

## Connection Strings

```bash
# Docker (backend container)
DATABASE_URL=postgresql+asyncpg://dhruv:dhruv123@postgres:5432/dhruv_db

# Host machine direct
DATABASE_URL=postgresql+asyncpg://dhruv:dhruv123@localhost:5432/dhruv_db

# Other Mac (remote - if needed)
DATABASE_URL=postgresql+asyncpg://dhruv_user:dhruv_pass@<OTHER_MAC_IP>:5432/dhruv_db
```

---

## Guardrails

### 1. No Deletion Policy
```sql
-- NEVER run these on tweet tables:
-- DELETE FROM parsed_events;
-- TRUNCATE raw_tweets;
-- DROP TABLE enriched_items;
```

### 2. Upsert Pattern (Required)
```sql
INSERT INTO parsed_events (...) 
VALUES (...)
ON CONFLICT (tweet_id) DO UPDATE SET ...;
```

### 3. Backup Before Migration
```bash
# Always backup before any migration
docker-compose exec postgres pg_dump -U dhruv dhruv_db > backup_$(date +%Y%m%d).sql
```
