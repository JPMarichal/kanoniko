#!/bin/bash
# Process a large PDF in 100-page chunks using Marker
PDF="/tmp/JFSDoctrinesofSalvationv1-3.pdf"
OUTDIR="/tmp/marker-out"
CHUNKS="/tmp/marker-chunks"
PAGES=691

mkdir -p "$CHUNKS"

START_TOTAL=$(date +%s)

for start in $(seq 0 100 $((PAGES - 1))); do
  end=$((start + 99))
  if [ $end -ge $PAGES ]; then end=$((PAGES - 1)); fi
  chunk_name=$(printf "chunk_%03d" $start)

  echo "=== Processing pages $start-$end ==="
  rm -rf "$OUTDIR/JFSDoctrinesofSalvationv1-3"

  SECONDS=0
  marker_single "$PDF" --output_dir "$OUTDIR" --output_format markdown --page_range "$start-$end" --disable_image_extraction 2>&1 | grep -E "(Saved|Total time|ERROR)"
  echo "$chunk_name done in ${SECONDS}s"

  cp "$OUTDIR/JFSDoctrinesofSalvationv1-3/JFSDoctrinesofSalvationv1-3.md" "$CHUNKS/${chunk_name}.md"
done

END_TOTAL=$(date +%s)

# Concatenate all chunks
cat "$CHUNKS"/chunk_*.md > "$OUTDIR/doctrines_of_salvation_full.md"

TOTAL_LINES=$(wc -l < "$OUTDIR/doctrines_of_salvation_full.md")
echo "=== DONE ==="
echo "Total time: $((END_TOTAL - START_TOTAL)) seconds"
echo "Total lines: $TOTAL_LINES"
echo "Chunks: $(ls $CHUNKS/chunk_*.md | wc -l)"
