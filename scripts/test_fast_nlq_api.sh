#!/bin/bash
# Test Fast NLQ API Endpoint

echo "🧪 Testing Fast NLQ API"
echo "======================="
echo ""

# Get auth token (assuming admin/admin login)
echo "1️⃣ Getting auth token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token. Is backend running?"
    exit 1
fi

echo "✅ Got auth token"
echo ""

# Test 1: Event Object Query (should be instant)
echo "2️⃣ TEST 1: Event Object Query (FAST MODE)"
echo "Query: भूमि सुधार योजना के बारे में बताओ"
echo ""

START=$(date +%s%N)
RESPONSE1=$(curl -s -X POST http://localhost:8000/api/nlq/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "भूमि सुधार योजना के बारे में बताओ", "mode": "fast"}')
END=$(date +%s%N)
TIME1=$(( ($END - $START) / 1000000 ))

echo "$RESPONSE1" | jq -r '.answer' | head -20
echo ""
echo "Response Mode: $(echo $RESPONSE1 | jq -r '.response_mode')"
echo "Quality Score: $(echo $RESPONSE1 | jq -r '.quality_score')/4"
echo "⏱️  API Response Time: ${TIME1}ms"
echo ""

# Test 2: Cache Hit (same query again)
echo "3️⃣ TEST 2: Cache Hit (same query)"
echo ""

START=$(date +%s%N)
RESPONSE2=$(curl -s -X POST http://localhost:8000/api/nlq/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "भूमि सुधार योजना के बारे में बताओ", "mode": "fast"}')
END=$(date +%s%N)
TIME2=$(( ($END - $START) / 1000000 ))

echo "Response Mode: $(echo $RESPONSE2 | jq -r '.response_mode')"
echo "⏱️  API Response Time: ${TIME2}ms"
echo ""

# Test 3: Vision 2047 (another event object)
echo "4️⃣ TEST 3: Vision 2047 Query"
echo "Query: छत्तीसगढ़ अंजोर Vision 2047 के milestones क्या हैं?"
echo ""

START=$(date +%s%N)
RESPONSE3=$(curl -s -X POST http://localhost:8000/api/nlq/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "छत्तीसगढ़ अंजोर Vision 2047 के milestones क्या हैं?", "mode": "fast"}')
END=$(date +%s%N)
TIME3=$(( ($END - $START) / 1000000 ))

echo "$RESPONSE3" | jq -r '.answer' | head -25
echo ""
echo "Response Mode: $(echo $RESPONSE3 | jq -r '.response_mode')"
echo "⏱️  API Response Time: ${TIME3}ms"
echo ""

# Summary
echo "═══════════════════════════════════════"
echo "📊 PERFORMANCE SUMMARY"
echo "═══════════════════════════════════════"
echo ""
echo "Test 1 (Event Object): ${TIME1}ms"
echo "Test 2 (Cache Hit):    ${TIME2}ms"
echo "Test 3 (Event Object): ${TIME3}ms"
echo ""
AVG=$(( ($TIME1 + $TIME2 + $TIME3) / 3 ))
echo "⚡ Average: ${AVG}ms"
echo ""
echo "🎯 Compared to old system (63,000ms avg):"
SPEEDUP=$(( 63000 / $AVG ))
echo "   ${SPEEDUP}x FASTER! 🔥"
echo ""
