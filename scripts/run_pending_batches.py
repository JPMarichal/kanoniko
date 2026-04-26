"""Autonomous runner for the generated pending-index batch plan.

Reads the batch plan JSON produced under ``logs/indexing/`` and executes
each planned batch via ``POST /index/ingest``. Designed for the current
workflow where we want FTS + vectors only (``skip_kg=true``) and a fully
autonomous pass with basic self-healing on transient API issues.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_API = "http://127.0.0.1:4300"
DEFAULT_PLAN = Path("logs/indexing/pending-index-full-2026-04-25.json")


def _api_get_json(base_url: str, path: str) -> dict:
    with urllib.request.urlopen(f"{base_url}{path}", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _api_post_json(base_url: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_until_idle(base_url: str, poll_seconds: int) -> None:
    while True:
        status = _api_get_json(base_url, "/index/status")
        if not status.get("indexing"):
            return
        phase = status.get("phase_name") or status.get("phase") or "?"
        eta = status.get("eta_seconds")
        eta_text = f", eta={eta}s" if eta is not None else ""
        print(
            f"Indexer busy: phase={phase}, files={status.get('files_processed', 0)}/"
            f"{status.get('files_total', 0)}{eta_text}",
            flush=True,
        )
        time.sleep(poll_seconds)


def _launch_batch(base_url: str, batch: dict, retries: int, poll_seconds: int) -> dict:
    payload = {
        "paths": batch["paths"],
        "force": False,
        "skip_backup": True,
        "skip_kg": True,
    }

    for attempt in range(1, retries + 1):
        try:
            return _api_post_json(base_url, "/index/ingest", payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 409:
                print(
                    f"Batch {batch['id']:02d}: indexer already busy, waiting to retry...",
                    flush=True,
                )
                _wait_until_idle(base_url, poll_seconds)
                continue
            print(
                f"Batch {batch['id']:02d}: launch attempt {attempt}/{retries} failed with "
                f"HTTP {exc.code}: {body}",
                flush=True,
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            print(
                f"Batch {batch['id']:02d}: launch attempt {attempt}/{retries} failed: {exc}",
                flush=True,
            )
        time.sleep(min(10 * attempt, 30))

    raise RuntimeError(f"Unable to launch batch {batch['id']:02d} after {retries} attempts")


def _poll_batch(base_url: str, batch: dict, poll_seconds: int) -> dict:
    last_snapshot: tuple | None = None
    while True:
        status = _api_get_json(base_url, "/index/status")
        if not status.get("indexing"):
            return status

        phase = status.get("phase_name") or status.get("phase") or "?"
        eta = status.get("eta_seconds")
        snapshot = (
            phase,
            status.get("files_processed", 0),
            status.get("files_total", 0),
            status.get("phase_percent", 0.0),
            eta,
        )
        if snapshot != last_snapshot:
            eta_text = f", eta={eta}s" if eta is not None else ""
            print(
                f"Batch {batch['id']:02d}: phase={phase}, progress={status.get('phase_percent', 0.0)}%, "
                f"files={status.get('files_processed', 0)}/{status.get('files_total', 0)}{eta_text}",
                flush=True,
            )
            last_snapshot = snapshot
        time.sleep(poll_seconds)


def _load_batches(plan_path: Path, start_batch: int, end_batch: int | None) -> list[dict]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    batches = plan["batches"]
    selected = [batch for batch in batches if batch["id"] >= start_batch]
    if end_batch is not None:
        selected = [batch for batch in selected if batch["id"] <= end_batch]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all pending ingest batches autonomously.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--start-batch", type=int, default=1)
    parser.add_argument("--end-batch", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    batches = _load_batches(args.plan, args.start_batch, args.end_batch)
    if not batches:
        print("No batches selected.", flush=True)
        return 0

    print(
        f"Running {len(batches)} batches from {args.plan} against {args.api} "
        f"(skip_kg=true, retries={args.retries})",
        flush=True,
    )

    if args.dry_run:
        for batch in batches:
            print(
                f"B{batch['id']:02d}: files={batch['files']} est_chunks={batch['est_chunks']} "
                f"eta={batch['eta_skip_kg_min']}-{batch['eta_skip_kg_max']} min",
                flush=True,
            )
        return 0

    failed_batches: list[int] = []
    start = time.monotonic()

    _wait_until_idle(args.api, args.poll_seconds)

    for batch in batches:
        print(
            f"=== Batch {batch['id']:02d}: files={batch['files']}, est_chunks={batch['est_chunks']}, "
            f"eta={batch['eta_skip_kg_min']}-{batch['eta_skip_kg_max']} min ===",
            flush=True,
        )
        try:
            launch = _launch_batch(args.api, batch, args.retries, args.poll_seconds)
            print(f"Launch response: {launch}", flush=True)
            status = _poll_batch(args.api, batch, args.poll_seconds)
            print(
                f"Batch {batch['id']:02d} finished. elapsed={status.get('elapsed_seconds', 0)}s "
                f"errors={status.get('error_count', 0)}",
                flush=True,
            )
        except Exception as exc:  # pragma: no cover - defensive runner
            print(f"Batch {batch['id']:02d} failed: {exc}", flush=True)
            failed_batches.append(batch["id"])
            _wait_until_idle(args.api, args.poll_seconds)

    total_elapsed = time.monotonic() - start
    print(
        f"All selected batches processed in {total_elapsed / 60:.1f} min. "
        f"Failed batches: {failed_batches if failed_batches else 'none'}",
        flush=True,
    )
    return 1 if failed_batches else 0


if __name__ == "__main__":
    sys.exit(main())