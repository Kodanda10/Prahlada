#!/bin/bash
# Monitor NLQ Stress Test Progress

echo "📊 NLQ Stress Test Monitor"
echo "=========================="
echo ""
echo "Watching: data/stress_test_output.log"
echo "Press Ctrl+C to stop monitoring"
echo ""

tail -f data/stress_test_output.log | grep -E "(TEST|SUCCESS|FAILED|SUMMARY|Avg Response)"
