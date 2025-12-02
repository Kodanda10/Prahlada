#!/usr/bin/env python3
"""
Database Ingestion Script - Parser V2.1
Ingests parsed data into parsed_events table

Actual Schema (current DB):
- id (use tweet_id as primary key), tweet_id, event_type, locations,
- people_mentioned, schemes_mentioned, overall_confidence,
- needs_review, review_status, parsed_at
"""
import json
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_URL = os.getenv("DATABASE_URL")
if DB_URL and "postgresql+asyncpg://" in DB_URL:
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://")

# File paths
PARSED_FILE = Path("data/parsed_tweets_gemini_parser_v2.jsonl")
BACKUP_FILE = Path("data/backup_parsed_events.jsonl")
LOG_FILE = Path("data/ingestion_log.txt")

def log_message(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")

def backup_existing_data(conn):
    """Backup existing parsed_events"""
    log_message("Creating backup...")
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM parsed_events")
    count = cur.fetchone()[0]
    
    if count > 0:
        cur.execute("""
            SELECT id, tweet_id, event_type, locations, people_mentioned, 
                   schemes_mentioned
            FROM parsed_events
        """)
        
        backup_data = []
        for row in cur.fetchall():
            backup_data.append({
                "id": row[0],
                "tweet_id": row[1],
                "event_type": row[2],
                "locations": row[3],
                "people_mentioned": row[4],
                "schemes_mentioned": row[5]
            })
        
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            for item in backup_data:
                f.write(json.dumps(item, ensure_ascii=False, default=str) + "\n")
        
        log_message(f"Backed up {count} events")
    else:
        log_message("No existing data to backup")
    
    cur.close()
    return count

def delete_old_data(conn):
    """Delete old parsed_events"""
    log_message("Deleting old data...")
    
    cur = conn.cursor()
    cur.execute("DELETE FROM parsed_events")
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    
    log_message(f"Deleted {deleted} events")
    return deleted

def ingest_new_data(conn):
    """Ingest Parser V9 data"""
    log_message(f"Loading from {PARSED_FILE}...")
    
    # Load parsed tweets
    parsed_tweets = []
    with open(PARSED_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parsed_tweets.append(json.loads(line))
    
    log_message(f"Loaded {len(parsed_tweets)} tweets")
    
    # Insert
    cur = conn.cursor()
    inserted = 0
    skipped = 0
    
    for tweet in parsed_tweets:
        tweet_id = tweet.get("tweet_id")
        parsed_data = tweet.get("parsed_data_v9", {})
        
        if not tweet_id or not parsed_data:
            skipped += 1
            continue
        
        try:
            # 1. Insert Raw Tweet first
            # Note: v9 file uses 'text' instead of 'raw_text' in the root object
            raw_text = tweet.get("text") or tweet.get("raw_text", "")
            created_at = tweet.get("created_at")
            
            cur.execute("""
                INSERT INTO raw_tweets (tweet_id, text, created_at, processing_status, fetched_at, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (tweet_id) DO NOTHING
            """, (
                tweet_id, raw_text, created_at, 'processed', datetime.utcnow(), datetime.utcnow()
            ))

            # 2. Extract fields for Parsed Event
            event_type = parsed_data.get("event_type")
            location = parsed_data.get("location") # This is a dict or null
            
            # For JSONB locations column, we store the whole object
            locations_json = Json(location) if location else None
        
            people = parsed_data.get("people_mentioned", []) or []
            schemes = parsed_data.get("schemes_mentioned", []) or []
            # v9 might not have word_buckets explicitly, but let's check
            word_buckets = parsed_data.get("word_buckets", []) or []
            confidence = parsed_data.get("confidence", 0.0)
            
            # v9 might not have needs_review/review_status, so default them
            needs_review = parsed_data.get("needs_review", True) # Default to True for review
            review_status = parsed_data.get("review_status", "pending")

            categories_json = parsed_data
            metadata_json = tweet.get("metadata_v9", {})
        
            # Insert (use tweet_id as primary key for id)
            cur.execute("""
                INSERT INTO parsed_events (
                    id, tweet_id, event_type, locations, people_mentioned,
                    schemes_mentioned, word_buckets, overall_confidence,
                    needs_review, review_status, parsed_at,
                    categories, gemini_metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tweet_id) DO UPDATE SET
                    event_type = EXCLUDED.event_type,
                    locations = EXCLUDED.locations,
                    people_mentioned = EXCLUDED.people_mentioned,
                    schemes_mentioned = EXCLUDED.schemes_mentioned,
                    word_buckets = EXCLUDED.word_buckets,
                    overall_confidence = EXCLUDED.overall_confidence,
                    needs_review = EXCLUDED.needs_review,
                    review_status = EXCLUDED.review_status,
                    parsed_at = EXCLUDED.parsed_at,
                    categories = EXCLUDED.categories,
                    gemini_metadata = EXCLUDED.gemini_metadata
            """, (
                tweet_id, tweet_id, event_type, locations_json, people,
                schemes, word_buckets, confidence, needs_review, review_status,
                datetime.utcnow(), Json(categories_json), Json(metadata_json)
            ))
            conn.commit()  # Commit after each successful insert
            inserted += 1
            
        except Exception as e:
            conn.rollback()  # Rollback failed transaction
            log_message(f"Error: {tweet_id}: {e}")
            skipped += 1
            continue
    
    cur.close()
    
    log_message(f"Inserted {inserted}, skipped {skipped}")
    return inserted, skipped

def verify(conn):
    """Verify ingestion"""
    log_message("Verifying...")
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM parsed_events")
    count = cur.fetchone()[0]
    
    cur.execute("""
        SELECT tweet_id, event_type, locations, people_mentioned
        FROM parsed_events
        LIMIT 3
    """)
    
    for tweet_id, event_type, locations, people in cur.fetchall():
        log_message(f"✓ {tweet_id}: {event_type}, {locations}, {len(people) if people else 0} people")
    
    cur.close()
    log_message(f"Total: {count} events")
    return count

def main():
    log_message("="*60)
    log_message("Parser V2.1 Ingestion")
    log_message("="*60)
    
    try:
        conn = psycopg2.connect(DB_URL)
        log_message("Connected")
        
        backup_count = backup_existing_data(conn)
        deleted_count = delete_old_data(conn)
        inserted, skipped = ingest_new_data(conn)
        final_count = verify(conn)
        
        log_message("="*60)
        log_message(f"Backed up: {backup_count}")
        log_message(f"Deleted: {deleted_count}")
        log_message(f"Inserted: {inserted}")
        log_message(f"Skipped: {skipped}")
        log_message(f"Final: {final_count}")
        log_message("="*60)
        
        if final_count == inserted:
            log_message("✓ SUCCESS")
        else:
            log_message(f"⚠ WARNING: Expected {inserted}, got {final_count}")
        
        conn.close()
        
    except Exception as e:
        log_message(f"✗ ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
