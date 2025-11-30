import sqlite3
import os

def check_db():
    db_path = "data/prahlada.db"
    if not os.path.exists(db_path):
        print(f"❌ DB file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT count(*) FROM parsed_events")
        count = cursor.fetchone()[0]
        print(f"✅ parsed_events count: {count}")
        
        if count > 0:
            cursor.execute("SELECT tweet_id, locations FROM parsed_events LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"   Row: {row}")
    except Exception as e:
        print(f"❌ Error querying DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
