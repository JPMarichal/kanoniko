#!/bin/bash
# Ingest biblical reference dictionaries into Alejandría
# Run AFTER docker compose is up and files are committed+synced
#
# These are the 5 external biblical dictionaries added from CCEL,
# internationalstandardbible.com, and bibleportal.com.
#
# Total: ~27K entries across 122 .txt files (A-Z per dictionary)
# Expected time: ~10 min on GPU (based on 779 files = 8 min benchmark)

API="http://localhost:4300"

echo "Ingesting biblical reference dictionaries..."
echo "============================================="

curl -s -X POST "$API/index/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": [
      "en/reference/easton-bible-dictionary",
      "en/reference/smith-bible-dictionary",
      "en/reference/hitchcock-bible-names",
      "en/reference/isbe",
      "en/reference/hastings-dictionary-of-the-bible"
    ]
  }' | python -m json.tool

echo ""
echo "Monitor progress: curl -s $API/index/status | python -m json.tool"
