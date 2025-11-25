#!/usr/bin/env python3
"""
Database Ingestion Script - Parser V2.1
Ingests parsed data into parsed_events table

Actual Schema:
- id, tweet_id, event_type, locations, people_mentioned, 
- schemes_mentioned, organizations, overall_confidence,
- needs_review, review_status, parsed_at
"""
import json
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import uuid

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
                   schemes_mentioned, organizations
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
                "schemes_mentioned": row[5],
                "organizations": row[6]
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
    """Ingest Parser V2.1 data"""
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
            # Extract fields
            event_type = parsed_data.get("event_type")
            location = parsed_data.get("location", {})
            locations = []
            if location:
                ulb = location.get("ulb_name")
                district = location.get("district")
                if ulb:
                    locations.append(ulb)
                elif district:
                    locations.append(district)
            
            people = parsed_data.get("people_mentioned", [])
            schemes = parsed_data.get("schemes_mentioned", [])
            orgs = parsed_data.get("organizations", [])
            confidence = parsed_data.get("confidence", 0.0)
            
            # Insert (let DB auto-generate id)
            try:
                cur.execute("""
                    INSERT INTO parsed_events (
                        tweet_id, event_type, locations, people_mentioned,
                        schemes_mentioned, organizations, overall_confidence,
                        needs_review, review_status, parsed_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tweet_id) DO UPDATE SET
                        event_type = EXCLUDED.event_type,
                        locations = EXCLUDED.locations,
                        people_mentioned = EXCLUDED.people_mentioned,
                        schemes_mentioned = EXCLUDED.schemes_mentioned,
                        organizations = EXCLUDED.organizations,
                        overall_confidence = EXCLUDED.overall_confidence,
                        parsed_at = EXCLUDED.parsed_at
                """, (
                    tweet_id, event_type, Json(locations), people,
                    schemes, orgs, confidence, confidence < 0.8, 'pending',
                    datetime.utcnow()
                ))
                conn.commit()  # Commit after each successful insert
                inserted += 1
                
            except Exception as e:
                conn.rollback()  # Rollback failed transaction
                log_message(f"Error: {tweet_id}: {e}")
                skipped += 1
                continue
            
        except Exception as e:
            log_message(f"Parse error: {tweet_id}: {e}")
            skipped += 1
    
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
