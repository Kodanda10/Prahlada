#!/bin/bash
# Live ingestion monitor

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         HYBRID MODE INGESTION - LIVE MONITOR                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Process status
    if ps aux | grep -q "[m]ass_ingest"; then
        echo "✅ Status: RUNNING"
        PID=$(cat data/ingestion.pid 2>/dev/null || echo "Unknown")
        echo "📊 PID: $PID"
    else
        echo "❌ Status: NOT RUNNING"
    fi
    echo ""
    
    # Checkpoint stats
    if [ -f data/ingestion_checkpoint.json ]; then
        echo "📈 Progress:"
        PROCESSED=$(python3 -c "import json; print(json.load(open('data/ingestion_checkpoint.json'))['stats']['processed'])" 2>/dev/null || echo "0")
        TOTAL=2611
        PERCENT=$((PROCESSED * 100 / TOTAL))
        AVG_CONF=$(python3 -c "import json; print(f\"{json.load(open('data/ingestion_checkpoint.json'))['stats']['avg_confidence']:.3f}\")" 2>/dev/null || echo "0.000")
        LLM_ENH=$(python3 -c "import json; print(json.load(open('data/ingestion_checkpoint.json'))['stats']['llm_enhanced'])" 2>/dev/null || echo "0")
        FAILED=$(python3 -c "import json; print(json.load(open('data/ingestion_checkpoint.json'))['stats']['failed'])" 2>/dev/null || echo "0")
        
        echo "  Processed: $PROCESSED / $TOTAL ($PERCENT%)"
        echo "  Avg Confidence: $AVG_CONF"
        echo "  LLM Enhanced: $LLM_ENH"
        echo "  Failed: $FAILED"
        
        # Progress bar
        BAR_WIDTH=50
        FILLED=$((PERCENT * BAR_WIDTH / 100))
        printf "  ["
        for ((i=0; i<FILLED; i++)); do printf "█"; done
        for ((i=FILLED; i<BAR_WIDTH; i++)); do printf "░"; done
        printf "] $PERCENT%%\n"
    else
        echo "⏳ Waiting for first checkpoint (first 100 tweets)..."
    fi
    echo ""
    
    # Recent log
    echo "📝 Recent Activity:"
    tail -5 data/ingestion_hybrid.log 2>/dev/null || echo "  No log yet"
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "Press Ctrl+C to exit monitor | Updates every 5 seconds"
    
    sleep 5
done
