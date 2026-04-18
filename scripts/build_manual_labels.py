"""Build data/kg-diagnostic/manual_labels_300.csv from TSV + inline labels."""
import csv, io
from pathlib import Path

LABELS = [
    3,2,3,1,2,1,3,1,3,1, 1,1,4,1,1,1,1,1,3,1,
    1,1,3,1,1,5,2,1,3,3, 1,4,1,1,1,5,1,1,1,1,
    3,3,3,5,5,3,5,1,3,1, 3,1,4,4,2,3,1,2,2,4,
    3,4,5,5,3,1,1,1,1,3, 2,1,1,3,4,3,4,1,3,1,
    2,1,1,2,1,3,1,1,1,2, 1,2,3,2,4,3,3,2,1,2,
    3,5,2,3,1,5,5,5,1,3, 1,5,5,1,3,4,2,1,5,1,
    3,3,2,1,5,2,3,4,3,5, 2,4,3,5,4,4,5,1,1,3,
    1,3,3,3,3,5,3,3,5,5, 5,5,1,1,5,1,4,4,5,1,
    1,5,1,3,2,5,3,1,2,2, 3,3,1,1,1,4,3,5,1,2,
    4,2,1,1,1,5,1,1,1,2, 3,3,5,3,1,1,1,1,3,4,
    5,1,2,3,1,3,1,1,2,1, 1,2,1,3,1,2,3,1,5,1,
    2,3,1,2,1,3,3,5,1,1, 2,2,5,3,3,3,5,4,4,2,
    1,1,1,1,1,3,5,2,5,4, 2,4,1,3,3,4,5,1,5,1,
    1,3,3,5,3,5,4,1,1,2, 2,3,1,5,1,4,5,1,3,1,
    2,4,3,1,1,1,1,1,1,5, 1,2,5,1,1,1,1,3,3,5,
]
assert len(LABELS) == 300, len(LABELS)

src = Path("/app/data/sample_persons_300.tsv")
dst = Path("/app/data/kg-diagnostic/manual_labels_300.csv")
dst.parent.mkdir(parents=True, exist_ok=True)

rows = []
with src.open(encoding="utf-8") as f:
    text = f.read()
# cypher-shell plain outputs comma-separated with quotes. skipinitialspace handles leading spaces.
reader = csv.reader(io.StringIO(text), skipinitialspace=True)
header = next(reader)
for parts in reader:
    if len(parts) != 6:
        continue
    name, al, deg, fam, cooc, mentions = parts
    rows.append([name, int(al), int(deg), int(fam), int(cooc), int(mentions)])

assert len(rows) == 300, f"got {len(rows)} rows"

with dst.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "aliases", "degree", "fam", "cooc", "mentions", "manual_cat"])
    for (name, al, deg, fam, cooc, mentions), cat in zip(rows, LABELS):
        w.writerow([name, al, deg, fam, cooc, mentions, cat])

print(f"Wrote {dst} ({len(rows)} rows)")
