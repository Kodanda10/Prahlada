#!/bin/bash
# Real-time NLQ Stress Test Monitor

clear
echo "🔄 NLQ Stress Test - Live Monitor"
echo "=================================="
echo ""

while true; do
    # Check if process is still running
    if ! pgrep -f "stress_test_nlq.py" > /dev/null; then
        echo "❌ Test process has stopped!"
        break
    fi
    
    # Get current stats (with defaults)
    TOTAL_LINES=$(wc -l < data/stress_test_output.log 2>/dev/null | tr -d ' ')
    TOTAL_LINES=${TOTAL_LINES:-0}
    
    QUESTIONS_STARTED=$(grep -c "TEST.*\[" data/stress_test_output.log 2>/dev/null)
    QUESTIONS_STARTED=${QUESTIONS_STARTED:-0}
    
    QUESTIONS_SUCCESS=$(grep -c "✅ SUCCESS" data/stress_test_output.log 2>/dev/null)
    QUESTIONS_SUCCESS=${QUESTIONS_SUCCESS:-0}
    
    QUESTIONS_FAILED=$(grep -c "❌ FAILED" data/stress_test_output.log 2>/dev/null)
    QUESTIONS_FAILED=${QUESTIONS_FAILED:-0}
    
    CURRENT_TIME=$(date "+%H:%M:%S")
    UPTIME=$(ps -p $(pgrep -f stress_test_nlq.py) -o etime= 2>/dev/null | tr -d ' ')
    UPTIME=${UPTIME:-"N/A"}
    
    # Calculate progress
    PROGRESS=$((QUESTIONS_SUCCESS + QUESTIONS_FAILED))
    REMAINING=$((20 - PROGRESS))
    
    # Clear and redraw
    tput cup 3 0
    echo "⏰ Current Time: $CURRENT_TIME"
    echo "⏱️  Test Running: $UPTIME"
    echo ""
    echo "📊 PROGRESS:"
    echo "   Questions Started: $QUESTIONS_STARTED / 20"
    echo "   Questions Completed: $PROGRESS / 20"
    echo "   ✅ Successful: $QUESTIONS_SUCCESS"
    echo "   ❌ Failed: $QUESTIONS_FAILED"
    echo "   ⏳ Remaining: $REMAINING"
    echo ""
    echo "📝 Log Lines: $TOTAL_LINES"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Press Ctrl+C to stop monitoring"
    echo "                                   "
    
    sleep 5
done
