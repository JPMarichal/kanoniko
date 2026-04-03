#!/usr/bin/env python3
"""Orchestrator for all Alejandría corpus downloads.

Runs every download script in parallel (bounded concurrency) and reports
a summary of successes, failures, and skips.

Usage:
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py --group scriptures
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py --group manuals music
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py --dry-run
    REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_all.py --workers 4

Groups:
    scriptures   Canonical scriptures (EN + ES)
    conference   General conference — requires --period YYYYMM
    manuals      All manuals (CFM, Seminary, ToP, Gospel Topics, Saints, etc.)
    music        All music collections (hymns, children's songbook, youth, etc.)
    study-aids   Harmony, abbreviations, Bible chronology, TG, BD, GS, JST
    special      Jesus the Christ, Easter plan, Christmas plan, PME

Default: all groups except 'conference' (which requires a specific period).
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Job definitions ────────────────────────────────────────────────────────────

@dataclass
class Job:
    name: str
    cmd: list[str]       # argv passed to subprocess (relative to repo root)
    group: str
    tags: list[str] = field(default_factory=list)


def _py(script: str, *args: str) -> list[str]:
    """Build a python invocation relative to repo root."""
    return [sys.executable, str(SCRIPTS / script), *args]


def _all_jobs() -> list[Job]:
    jobs: list[Job] = []

    # ── Scriptures ─────────────────────────────────────────────────────────────
    jobs.append(Job("scriptures/en+es", _py("download_scriptures.py"), group="scriptures"))

    # ── Music ──────────────────────────────────────────────────────────────────
    for collection in ["hymns", "hymns-home-church", "childrens-songbook", "youth-music", "hymn-helps"]:
        jobs.append(Job(
            f"music/{collection}",
            _py("download_music.py", "--collection", collection),
            group="music",
        ))

    # ── Study aids ─────────────────────────────────────────────────────────────
    jobs.append(Job("study-aids/harmony", _py("scrape_harmony.py"), group="study-aids"))
    jobs.append(Job("study-aids/abbreviations", _py("scrape_abbreviations.py"), group="study-aids"))
    jobs.append(Job("study-aids/bible-chronology", _py("scrape_bible_chronology.py"), group="study-aids"))
    for aid in ["gs", "tg", "bd", "jst"]:
        for lang in ["eng", "spa"]:
            jobs.append(Job(
                f"study-aids/{aid}/{lang}",
                _py("scrape_study_aids.py", "--aid", aid, "--lang", lang),
                group="study-aids",
            ))

    # ── Special standalone scripts ─────────────────────────────────────────────
    jobs.append(Job("special/jesus-the-christ", _py("download_jesus_the_christ.py"), group="special"))
    jobs.append(Job("special/easter-plan", _py("download_easter_study_plan.py"), group="special"))
    jobs.append(Job("special/christmas-plan", _py("download_christmas_study_plan.py"), group="special"))
    jobs.append(Job("special/pme", _py("download_pme.py"), group="special"))

    # ── Manuals: static ────────────────────────────────────────────────────────
    static_manuals = [
        "bom-institute-student", "bom-seminary-student",
        "dc-institute-student", "dc-seminary-teacher",
        "doctrinal-mastery", "doctrines-of-the-gospel",
        "eternal-family", "first-vision-accounts",
        "for-the-strength-of-youth", "foundations-restoration",
        "gospel-principles", "gospel-topics", "gospel-topics-essays",
        "jesus-christ-everlasting-gospel", "missionary-preparation",
        "nt-institute-teacher", "nt-seminary-student",
        "ot-seminary-student", "our-heritage", "pgp-institute-student",
        "saints-v1", "saints-v2", "saints-v3", "saints-v4",
        "true-to-the-faith",
    ]
    for key in static_manuals:
        jobs.append(Job(
            f"manuals/{key}",
            _py("download_manual.py", "--manual", key),
            group="manuals",
        ))

    # ── Manuals: Teachings of Presidents (individual prophets) ────────────────
    teachings_keys = [
        "teachings-brigham-young", "teachings-david-o-mckay",
        "teachings-doctrine-bom", "teachings-ezra-taft-benson",
        "teachings-george-albert-smith", "teachings-gordon-b-hinckley",
        "teachings-harold-b-lee", "teachings-heber-j-grant",
        "teachings-howard-w-hunter", "teachings-john-taylor",
        "teachings-joseph-f-smith", "teachings-joseph-fielding-smith",
        "teachings-joseph-smith", "teachings-lorenzo-snow",
        "teachings-russell-m-nelson", "teachings-spencer-w-kimball",
        "teachings-thomas-s-monson", "teachings-wilford-woodruff",
    ]
    for key in teachings_keys:
        jobs.append(Job(
            f"manuals/{key}",
            _py("download_manual.py", "--manual", key),
            group="manuals",
            tags=["teachings"],
        ))

    # ── Come Follow Me (all years) ─────────────────────────────────────────────
    for year in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        jobs.append(Job(
            f"manuals/come-follow-me-{year}",
            _py("download_manual.py", "--manual", "come-follow-me", "--cfm-year", str(year)),
            group="manuals",
            tags=["cfm"],
        ))

    return jobs


# ── Runner ─────────────────────────────────────────────────────────────────────

@dataclass
class Result:
    job: Job
    exit_code: int
    elapsed: float
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def _run_job(job: Job, dry_run: bool) -> Result:
    start = time.monotonic()
    if dry_run:
        logger.info("[DRY-RUN] %s: %s", job.name, " ".join(job.cmd))
        return Result(job=job, exit_code=0, elapsed=0.0, stdout="", stderr="")

    logger.info("START  %s", job.name)
    try:
        proc = subprocess.run(
            job.cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour max per job
        )
    except subprocess.TimeoutExpired:
        return Result(job=job, exit_code=-1, elapsed=time.monotonic() - start,
                      stdout="", stderr="TIMEOUT after 3600s")
    except Exception as exc:
        return Result(job=job, exit_code=-1, elapsed=time.monotonic() - start,
                      stdout="", stderr=str(exc))

    elapsed = time.monotonic() - start
    status = "OK" if proc.returncode == 0 else f"FAIL({proc.returncode})"
    logger.info("%-6s %s  (%.0fs)", status, job.name, elapsed)
    return Result(job=job, exit_code=proc.returncode, elapsed=elapsed,
                  stdout=proc.stdout, stderr=proc.stderr)


def main():
    all_groups = ["scriptures", "manuals", "music", "study-aids", "special"]

    parser = argparse.ArgumentParser(description="Download all Alejandría corpus materials")
    parser.add_argument(
        "--group", nargs="+", choices=all_groups + ["conference"],
        default=all_groups,
        help="Groups to run (default: all except 'conference')",
    )
    parser.add_argument(
        "--workers", type=int, default=6,
        help="Max parallel download jobs (default: 6)",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing")
    parser.add_argument("--list", action="store_true",
                        help="List all jobs and exit")
    args = parser.parse_args()

    selected_groups = set(args.group)
    jobs = [j for j in _all_jobs() if j.group in selected_groups]

    if args.list:
        for j in jobs:
            print(f"[{j.group}] {j.name}")
            print(f"    {' '.join(j.cmd)}")
        print(f"\nTotal: {len(jobs)} jobs")
        return

    logger.info("Alejandría corpus download — %d jobs, %d workers", len(jobs), args.workers)
    start_all = time.monotonic()

    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=args.workers, thread_name_prefix="dl") as ex:
        futures = {ex.submit(_run_job, job, args.dry_run): job for job in jobs}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                job = futures[future]
                logger.exception("Unexpected error in job %s: %s", job.name, exc)

    total_elapsed = time.monotonic() - start_all

    # ── Summary ────────────────────────────────────────────────────────────────
    ok = [r for r in results if r.ok]
    failed = [r for r in results if not r.ok]

    print(f"\n{'='*60}")
    print(f"SUMMARY  {len(ok)}/{len(results)} jobs succeeded  ({total_elapsed:.0f}s total)")
    if failed:
        print(f"\nFAILED ({len(failed)}):")
        for r in failed:
            print(f"  [{r.exit_code}] {r.job.name}")
            if r.stderr:
                # Print last 3 lines of stderr for quick diagnosis
                lines = r.stderr.strip().splitlines()
                for line in lines[-3:]:
                    print(f"        {line}")
    print("="*60)

    # Write full log to logs/
    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"download_all_{datetime.now():%Y%m%d_%H%M%S}.log"
    with log_file.open("w", encoding="utf-8") as f:
        for r in sorted(results, key=lambda x: x.job.name):
            f.write(f"[{'OK' if r.ok else 'FAIL':4}] {r.job.name}  ({r.elapsed:.0f}s)\n")
            f.write(f"  CMD: {' '.join(r.job.cmd)}\n")
            if r.stdout:
                f.write("  STDOUT:\n")
                for line in r.stdout.splitlines()[-20:]:
                    f.write(f"    {line}\n")
            if r.stderr:
                f.write("  STDERR:\n")
                for line in r.stderr.splitlines()[-20:]:
                    f.write(f"    {line}\n")
            f.write("\n")
    logger.info("Full log: %s", log_file)

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
