"""Sequential batch indexing for pending books."""
import json, urllib.request, time, sys

BATCH_FILE = "/tmp/book_batches.json"
API = "http://localhost:4300"

with open(BATCH_FILE) as f:
    batches = json.load(f)

total = len(batches)
for i, (paths, count) in enumerate(batches):
    print(f"=== Batch {i+1}/{total}: {count} files, {len(paths)} books ===", flush=True)

    payload = json.dumps({"paths": paths, "force": True, "skip_backup": True})
    req = urllib.request.Request(
        f"{API}/index/ingest",
        data=payload.encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req)
    print("  Launched", flush=True)

    while True:
        time.sleep(30)
        status = json.loads(
            urllib.request.urlopen(f"{API}/index/status").read()
        )
        if not status["indexing"]:
            break
        p3d = status["phase_3_chunks_done"]
        p3t = status["phase_3_chunks_total"]
        pct = 100 * p3d / p3t if p3t else 0
        elapsed = status["elapsed_seconds"]
        print(f"  P3: {p3d}/{p3t} ({pct:.0f}%) elapsed {elapsed:.0f}s", flush=True)

    elapsed = status.get("elapsed_seconds", 0)
    print(f"  Done in {elapsed:.0f}s", flush=True)

print("=== ALL BATCHES COMPLETE ===", flush=True)
