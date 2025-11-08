#!/bin/bash

# Test script for manual trend processing

echo "🧪 Testing Manual Trend Processing"
echo "=================================="
echo ""

TREND_NAME="${1:-Zohran Mamdani}"

echo "📝 Step 1: Adding manual trend via API..."
curl -X POST http://localhost:5001/api/session/trends \
  -H "Content-Type: application/json" \
  -d "{\"trends\": [\"$TREND_NAME\"], \"use_gemini\": true}" \
  -s | python3 -m json.tool

echo ""
echo ""
echo "✅ Trend added to session!"
echo ""
echo "📊 Step 2: Check session status..."
curl -s http://localhost:5001/api/session/status | python3 -m json.tool

echo ""
echo ""
echo "✨ Next Steps:"
echo "1. main.py is running → It will automatically process this trend"
echo "2. Check dashboard at http://localhost:5001 to see progress"
echo "3. Video will be created in output_videos/"
echo ""
echo "🔍 To monitor progress:"
echo "   tail -f trend_collector.log"
