"""Sequential batch indexing for pending files."""
import json, urllib.request, time, sys

BATCH_FILE = "/tmp/book_batches.json"
API = "http://localhost:4300"

# Parse CLI args
skip_kg = "--skip-kg" in sys.argv
force = "--force" in sys.argv
kg_flush_interval = 15
for arg in sys.argv:
    if arg.startswith("--kg-flush-interval="):
        kg_flush_interval = int(arg.split("=", 1)[1])

with open(BATCH_FILE) as f:
    batches = json.load(f)

total = len(batches)
mode = "FTS+vectors" if skip_kg else "full (FTS+vectors+KG)"
print(f"=== {total} batches, mode: {mode}, force: {force}, kg_flush_interval: {kg_flush_interval} ===", flush=True)

for i, (paths, count) in enumerate(batches):
    print(f"=== Batch {i+1}/{total}: {count} files, {len(paths)} dirs ===", flush=True)

    payload = json.dumps({
        "paths": paths,
        "force": force,
        "skip_backup": True,
        "skip_kg": skip_kg,
        "kg_flush_interval": kg_flush_interval,
    })
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
        phase = status.get("phase", 0)
        phase_name = status.get("phase_name", "")
        fp = status["files_processed"]
        ft = status["files_total"]
        elapsed = status["elapsed_seconds"]
        if phase == 3:
            p3d = status["phase_3_chunks_done"]
            p3t = status["phase_3_chunks_total"]
            pct = 100 * p3d / p3t if p3t else 0
            print(f"  P3: {p3d}/{p3t} ({pct:.0f}%) files={fp}/{ft} elapsed={elapsed:.0f}s", flush=True)
        else:
            pct = status.get("phase_percent", 0) or 0
            print(f"  P{phase} ({phase_name}): {pct:.0f}% files={fp}/{ft} elapsed={elapsed:.0f}s", flush=True)

    elapsed = status.get("elapsed_seconds", 0)
    print(f"  Done in {elapsed:.0f}s", flush=True)

print("=== ALL BATCHES COMPLETE ===", flush=True)
