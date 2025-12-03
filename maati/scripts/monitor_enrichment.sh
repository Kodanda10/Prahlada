#!/bin/bash
# Monitor enrichment progress in real-time

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATUS_FILE="$PROJECT_DIR/data/enrichment_status.json"
LOG_FILE="$PROJECT_DIR/data/enrichment_runner.log"
CHECKPOINT_FILE="$PROJECT_DIR/data/enrichment_checkpoint.json"

echo "📊 Enrichment Monitoring Dashboard"
echo "===================================="
echo ""

# Check if running
if [ -f "$PROJECT_DIR/data/enrichment_runner.pid" ]; then
    PID=$(cat "$PROJECT_DIR/data/enrichment_runner.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Status: RUNNING (PID: $PID)"
    else
        echo "⚠️  Status: STOPPED (stale PID)"
    fi
else
    echo "❌ Status: NOT RUNNING"
fi

echo ""

# Show current status
if [ -f "$STATUS_FILE" ]; then
    echo "📈 Current Status:"
    python3 -m json.tool "$STATUS_FILE" 2>/dev/null || cat "$STATUS_FILE"
    echo ""
fi

# Show checkpoint progress
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "💾 Checkpoint Info:"
    python3 -c "
import json
with open('$CHECKPOINT_FILE') as f:
    cp = json.load(f)
    print(f'  Last processed: {cp.get(\"last_tweet_id\", \"N/A\")}')
    stats = cp.get('stats', {})
    if stats:
        print(f'  Total: {stats.get(\"total\", 0)}')
        print(f'  Processed: {stats.get(\"processed\", 0)}')
        print(f'  Enriched: {stats.get(\"enriched\", 0)}')
        print(f'  Failed: {stats.get(\"failed\", 0)}')
        print(f'  Skipped: {stats.get(\"skipped\", 0)}')
" 2>/dev/null
    echo ""
fi

# Show recent log entries
if [ -f "$LOG_FILE" ]; then
    echo "📝 Recent Activity (last 10 lines):"
    tail -n 10 "$LOG_FILE"
    echo ""
fi

echo "Commands:"
echo "  Watch logs:   tail -f $LOG_FILE"
echo "  Full status:  cat $STATUS_FILE | python3 -m json.tool"
echo "  Stop:         kill \$(cat $PROJECT_DIR/data/enrichment_runner.pid)"
