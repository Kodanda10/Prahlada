#!/bin/bash
# Re-enrich specific tweets with corrected code
# 
# Usage: ./re_enrich_corrections.sh <tweet_ids_file>
#
# This script re-enriches tweets that were enriched with old code
# (word buckets only, no location/event corrections)

TWEET_IDS_FILE="${1:-data/tweets_need_recorrection.txt}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ ! -f "$TWEET_IDS_FILE" ]; then
    echo "❌ File not found: $TWEET_IDS_FILE"
    exit 1
fi

TWEET_COUNT=$(wc -l < "$TWEET_IDS_FILE")
echo "🔄 Re-enriching $TWEET_COUNT tweets with correction support..."
echo ""

export PHI_ENABLED=true

# Reset word_buckets for these specific tweets to force re-enrichment
"$PROJECT_DIR/venv/bin/python3" << EOF
import asyncio
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import ParsedEvent

async def reset_buckets():
    with open('$TWEET_IDS_FILE') as f:
        tweet_ids = [line.strip() for line in f if line.strip()]
    
    print(f'Resetting word_buckets for {len(tweet_ids)} tweets...')
    
    async with AsyncSessionLocal() as session:
        for tweet_id in tweet_ids:
            result = await session.execute(
                select(ParsedEvent).where(ParsedEvent.tweet_id == tweet_id)
            )
            tweet = result.scalars().first()
            if tweet:
                tweet.word_buckets = []  # Reset to force re-enrichment
        
        await session.commit()
        print(f'✅ Reset complete - tweets will be re-enriched')

asyncio.run(reset_buckets())
EOF

# Run enrichment (will process tweets with empty word_buckets)
echo ""
echo "🚀 Starting re-enrichment..."
"$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/scripts/enrich_semantic.py"

echo ""
echo "✅ Re-enrichment complete!"
echo "   Tweets now have location and event corrections applied"
