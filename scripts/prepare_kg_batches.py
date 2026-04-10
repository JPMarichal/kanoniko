"""Prepare KG batches for files indexed with skip_kg."""
import sqlite3, os, json
from collections import defaultdict

db = sqlite3.connect("/app/data/sqlite/alejandria.db")
registered = [r[0] for r in db.execute("SELECT file_path FROM document_registry").fetchall()]

revistas = sorted([r for r in registered if "/revistas/" in r])
isbe = sorted([r for r in registered if "/reference/isbe/" in r])

rev_chunks = db.execute(
    "SELECT SUM(chunk_count) FROM document_registry WHERE file_path LIKE '%revistas%'"
).fetchone()[0] or 0
isbe_chunks = db.execute(
    "SELECT SUM(chunk_count) FROM document_registry WHERE file_path LIKE '%reference/isbe%'"
).fetchone()[0] or 0
db.close()

print(f"Revistas: {len(revistas)} files, {rev_chunks} chunks")
print(f"ISBE: {len(isbe)} files, {isbe_chunks} chunks")
print(f"Total: {len(revistas)+len(isbe)} files, {rev_chunks+isbe_chunks} chunks")

books = defaultdict(list)
for p in revistas:
    books[os.path.dirname(p)].append(p)

BATCH_SIZE = 1000
batches = []
current_paths = []
current_count = 0
for book, files in sorted(books.items()):
    current_paths.append(book)
    current_count += len(files)
    if current_count >= BATCH_SIZE:
        batches.append((current_paths, current_count))
        current_paths = []
        current_count = 0
if current_paths:
    batches.append((current_paths, current_count))

# ISBE last
isbe_dirs = list(set(os.path.dirname(p) for p in isbe))
if isbe_dirs:
    batches.append((isbe_dirs, len(isbe)))

print(f"\nBatches: {len(batches)}")
total_files = 0
for i, (paths, count) in enumerate(batches):
    total_files += count
    print(f"  Batch {i+1}: {count} files, {len(paths)} dirs")
print(f"Total files in batches: {total_files}")

with open("/tmp/book_batches.json", "w") as f:
    json.dump(batches, f)
print("Saved to /tmp/book_batches.json")
