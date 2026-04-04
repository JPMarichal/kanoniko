#!/bin/bash
# Ingest new corpus material into Alejandría
# Run AFTER docker compose is up and files are committed+synced
#
# Batch 2026-04: 5 biblical reference dictionaries + 20 B.H. Roberts books
#
# Reference dictionaries (~27K entries, 122 .txt files):
#   - Easton's Bible Dictionary (CCEL ThML)
#   - Smith's Bible Dictionary (CCEL ThML)
#   - Hitchcock's Bible Names (CCEL plain text)
#   - ISBE (internationalstandardbible.com)
#   - Hastings' Dictionary of the Bible (bibleportal.com)
#
# B.H. Roberts books (20 books, 624 chapters):
#   - History of the Church vols 1-6
#   - Seventy's Course in Theology, Years 1-5
#   - New Witness for God vols 1-3
#   - Life of John Taylor, Mormon Doctrine of Deity,
#     Rise and Fall of Nauvoo, Missouri Persecutions,
#     Outlines of Ecclesiastical History, Corianton
#
# Expected time: ~20 min on GPU (based on 779 files = 8 min benchmark)

API="http://localhost:4300"

echo "Ingesting reference dictionaries + B.H. Roberts books..."
echo "========================================================="

curl -s -X POST "$API/index/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": [
      "en/reference/easton-bible-dictionary",
      "en/reference/smith-bible-dictionary",
      "en/reference/hitchcock-bible-names",
      "en/reference/isbe",
      "en/reference/hastings-dictionary-of-the-bible",
      "en/books/history-of-the-church-vol1",
      "en/books/history-of-the-church-vol2",
      "en/books/history-of-the-church-vol3",
      "en/books/history-of-the-church-vol4",
      "en/books/history-of-the-church-vol5",
      "en/books/history-of-the-church-vol6",
      "en/books/seventys-course-theology-1st",
      "en/books/seventys-course-theology-2nd",
      "en/books/seventys-course-theology-3rd",
      "en/books/seventys-course-theology-4th",
      "en/books/seventys-course-theology-5th",
      "en/books/new-witness-for-god-vol1",
      "en/books/new-witnesses-for-god-vol2",
      "en/books/new-witnesses-for-god-vol3",
      "en/books/life-of-john-taylor",
      "en/books/mormon-doctrine-of-deity",
      "en/books/rise-and-fall-of-nauvoo",
      "en/books/missouri-persecutions",
      "en/books/outlines-ecclesiastical-history",
      "en/books/corianton"
    ]
  }' | python -m json.tool

echo ""
echo "Monitor progress: curl -s $API/index/status | python -m json.tool"
