#!/bin/bash
# Add Zohran Mamdani as a manual trend via dashboard API

curl -X POST http://localhost:5001/api/set-trends \
  -H "Content-Type: application/json" \
  -d '{
    "trends": ["Zohran Mamdani"],
    "use_gemini": true
  }'

echo ""
echo "✅ Trend added! Check dashboard at http://localhost:5001"
