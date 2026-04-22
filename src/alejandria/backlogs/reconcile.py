"""Reconcile engine — compare filesystem + Postgres state against the
backlogs and propose mutations.

Strategy pattern: the :class:`Reconciler` owns a list of :class:`Check`
objects, runs each, and aggregates their :class:`ReconcileFinding`
results. Adding a new rule is a new Check class — no surgery on the
orchestrator.

Dry-run contract:
* :meth:`Reconciler.scan` is read-only: it returns a list of findings
  and never mutates backlogs or the filesystem.
* :meth:`Reconciler.apply` takes a list of findings and materialises
  them. Exposed separately so the CLI can show findings and ask for
  confirmation before writing.

Aggressiveness level (design decision per §Level B discussion): MEDIUM.
Checks update status fields of **existing** entries. They do NOT
auto-create entries in a backlog where the slug isn't registered yet —
they flag such cases with ``kind="orphan"`` so a human can decide.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Protocol, runtime_checkable

from alejandria.backlogs.registry import BacklogRegistry


# --------------------------------------------------------------------------- #
# DTO: a proposed mutation
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ReconcileFinding:
    """One proposed change (or flag) emitted by a :class:`Check`.

    Kinds:
    * ``update``  — upsert ``patch`` into ``backlog`` entry for ``slug``.
    * ``orphan``  — filesystem artefact exists but no slug is registered.
                    Not auto-actionable; reported for human review.
    * ``info``    — informational (no mutation implied).
    """

    kind: str                                   # update | orphan | info
    backlog: str | None                         # None for orphan/info that isn't tied to a backlog
    slug: str | None
    patch: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def describe(self) -> str:
        head = f"[{self.kind}]"
        if self.backlog and self.slug:
            head += f" {self.backlog}/{self.slug}"
        elif self.slug:
            head += f" {self.slug}"
        if self.reason:
            head += f": {self.reason}"
        return head


# --------------------------------------------------------------------------- #
# Environment — things the checks need to observe
# --------------------------------------------------------------------------- #

@dataclass
class Environment:
    """Bundle of external state the checks read from.

    Explicit DI so tests can inject fakes (a temp corpus dir, a mocked
    Postgres client, a download cache at a custom path).
    """

    registry: BacklogRegistry
    corpus_root: Path
    downloads_root: Path
    reviews_root: Path                          # prods/reseñas/
    postgres_document_registry: Any | None = None  # object with all_records()

    @classmethod
    def from_repo(
        cls,
        repo_root: Path,
        *,
        include_postgres: bool = False,
    ) -> "Environment":
        registry = BacklogRegistry(root=repo_root / "backlogs")
        pg_client = None
        if include_postgres:
            try:
                from alejandria.ingestion.registry import make_document_registry
                pg_client = make_document_registry()
            except Exception:
                pg_client = None
        return cls(
            registry=registry,
            corpus_root=repo_root / "corpus",
            downloads_root=repo_root / "data" / "raw",
            reviews_root=repo_root / "prods" / "reseñas",
            postgres_document_registry=pg_client,
        )


# --------------------------------------------------------------------------- #
# Strategy: one check per rule
# --------------------------------------------------------------------------- #

@runtime_checkable
class Check(Protocol):
    """Strategy — inspects the environment and emits findings."""

    name: str

    def run(self, env: Environment) -> list[ReconcileFinding]: ...


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_of_paths(paths: Iterable[Path]) -> str:
    """Stable aggregate SHA over sorted paths — order-independent for
    the same set of files."""
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: str(x)):
        if p.is_file():
            h.update(p.name.encode("utf-8"))
            h.update(b"\0")
            h.update(_sha256_of_file(p).encode("ascii"))
            h.update(b"\n")
    return h.hexdigest()


# ----- Review file check ------------------------------------------------ #

class ReviewFileCheck:
    """If ``prods/reseñas/{slug}/reseña.md`` exists for a slug already in
    the research backlog with status != 'completa', propose
    status='completa' + review_path + completed_at."""

    name = "review-file"

    def run(self, env: Environment) -> list[ReconcileFinding]:
        findings: list[ReconcileFinding] = []
        for entry in env.registry.research.entries():
            slug = entry["slug"]
            review_md = env.reviews_root / slug / "reseña.md"
            if review_md.exists():
                if entry.get("status") != "completa":
                    from datetime import datetime, timezone
                    findings.append(ReconcileFinding(
                        kind="update",
                        backlog="research",
                        slug=slug,
                        patch={
                            "status": "completa",
                            "review_path": str(review_md.relative_to(
                                env.reviews_root.parent.parent
                            )),
                            "completed_at": datetime.now(timezone.utc)
                                .replace(microsecond=0).isoformat(),
                        },
                        reason=f"reseña.md found at {review_md}",
                    ))
            elif entry.get("status") == "completa":
                findings.append(ReconcileFinding(
                    kind="info",
                    backlog="research",
                    slug=slug,
                    reason="status='completa' but reseña.md missing on disk",
                ))

        # Orphan reseñas — directories in prods/reseñas/ not registered.
        if env.reviews_root.is_dir():
            registered = {e["slug"] for e in env.registry.research.entries()}
            for child in env.reviews_root.iterdir():
                if not child.is_dir():
                    continue
                if (child / "reseña.md").exists() and child.name not in registered:
                    findings.append(ReconcileFinding(
                        kind="orphan",
                        backlog="research",
                        slug=child.name,
                        reason=f"reseña.md at {child} but slug not in research.json",
                    ))
        return findings


# ----- Download cache check -------------------------------------------- #

class DownloadCacheCheck:
    """If the raw file pointed to by ``downloads[slug].raw_path`` exists on
    disk and the backlog entry is pending, propose status='descargado'
    + sha256 of the file."""

    name = "download-cache"

    def run(self, env: Environment) -> list[ReconcileFinding]:
        findings: list[ReconcileFinding] = []
        for entry in env.registry.downloads.entries():
            slug = entry["slug"]
            raw_path_str = entry.get("raw_path", "")
            if not raw_path_str:
                continue
            raw_path = Path(raw_path_str)
            if not raw_path.is_absolute():
                raw_path = env.downloads_root.parent / raw_path_str
            if raw_path.exists() and entry.get("status") != "descargado":
                sha = _sha256_of_file(raw_path)
                findings.append(ReconcileFinding(
                    kind="update",
                    backlog="downloads",
                    slug=slug,
                    patch={"status": "descargado", "sha256": sha, "error": ""},
                    reason=f"raw file present at {raw_path}",
                ))
            elif not raw_path.exists() and entry.get("status") == "descargado":
                findings.append(ReconcileFinding(
                    kind="info",
                    backlog="downloads",
                    slug=slug,
                    reason=f"status='descargado' but raw file missing at {raw_path}",
                ))
        return findings


# ----- Corpus file check (SHA drift → stale) --------------------------- #

class CorpusFileCheck:
    """For each slug in indexing with declared ``paths``: compute aggregate
    SHA of current files; if it differs from ``last_sha``, propose
    status='stale'."""

    name = "corpus-file"

    def run(self, env: Environment) -> list[ReconcileFinding]:
        findings: list[ReconcileFinding] = []
        for entry in env.registry.indexing.entries():
            slug = entry["slug"]
            paths = entry.get("paths") or []
            if not paths:
                continue
            resolved = [env.corpus_root / p for p in paths]
            current_sha = _sha256_of_paths(resolved)
            last_sha = entry.get("last_sha") or ""
            if current_sha != last_sha and entry.get("status") == "indexado":
                findings.append(ReconcileFinding(
                    kind="update",
                    backlog="indexing",
                    slug=slug,
                    patch={"status": "stale"},
                    reason=(
                        f"aggregate SHA changed since last index "
                        f"({last_sha[:8] or 'empty'}… → {current_sha[:8]}…)"
                    ),
                ))
        return findings


# ----- Postgres state check (optional; needs tunnel) ------------------- #

class PostgresStateCheck:
    """Confirm ``status='indexado'`` against actual Postgres presence.

    Skipped silently if no Postgres handle was injected (tests / offline).
    """

    name = "postgres-state"

    def run(self, env: Environment) -> list[ReconcileFinding]:
        if env.postgres_document_registry is None:
            return []
        try:
            pg_paths = {r.file_path for r in env.postgres_document_registry.all_records()}
        except Exception as exc:
            return [ReconcileFinding(
                kind="info", backlog=None, slug=None,
                reason=f"postgres check skipped: {exc}",
            )]

        findings: list[ReconcileFinding] = []
        for entry in env.registry.indexing.entries():
            slug = entry["slug"]
            paths = entry.get("paths") or []
            if not paths:
                continue
            missing = [p for p in paths if p not in pg_paths]
            if missing and entry.get("status") == "indexado":
                findings.append(ReconcileFinding(
                    kind="update",
                    backlog="indexing",
                    slug=slug,
                    patch={"status": "stale"},
                    reason=f"{len(missing)} path(s) not present in Postgres document_registry",
                ))
        return findings


# ----- Orphan indexed file check --------------------------------------- #

class OrphanCorpusCheck:
    """Files present in ``corpus/`` not covered by any slug in indexing.

    Reported as ``kind="orphan"`` (informational — human decides whether
    to create a discovery+indexing entry or delete the file)."""

    name = "orphan-corpus"

    def __init__(self, max_report: int = 50) -> None:
        self._max = max_report

    def run(self, env: Environment) -> list[ReconcileFinding]:
        if not env.corpus_root.is_dir():
            return []
        tracked: set[str] = set()
        for entry in env.registry.indexing.entries():
            for p in entry.get("paths") or []:
                tracked.add(p)
                # A declared directory covers everything under it
                tracked.add(p.rstrip("/") + "/")

        def _is_tracked(rel: str) -> bool:
            if rel in tracked:
                return True
            for t in tracked:
                if t.endswith("/") and rel.startswith(t):
                    return True
            return False

        findings: list[ReconcileFinding] = []
        count = 0
        for path in env.corpus_root.rglob("*.txt"):
            rel = str(path.relative_to(env.corpus_root)).replace("\\", "/")
            if not _is_tracked(rel):
                findings.append(ReconcileFinding(
                    kind="orphan",
                    backlog="indexing",
                    slug=None,
                    reason=f"corpus file {rel} not in any indexing entry",
                ))
                count += 1
                if count >= self._max:
                    findings.append(ReconcileFinding(
                        kind="info", backlog="indexing", slug=None,
                        reason=f"orphan-corpus stopped at {self._max} findings "
                               f"(increase --max-orphans to see more)",
                    ))
                    break
        return findings


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

#: Default check roster used by the CLI. Order matters only for reporting;
#: findings are pure data.
DEFAULT_CHECKS: tuple[Check, ...] = (
    ReviewFileCheck(),
    DownloadCacheCheck(),
    CorpusFileCheck(),
    PostgresStateCheck(),
    OrphanCorpusCheck(),
)


class Reconciler:
    """Run a set of checks and (optionally) apply their findings."""

    def __init__(self, checks: Iterable[Check] = DEFAULT_CHECKS) -> None:
        self._checks = tuple(checks)

    # ----- Scan (read-only) ---------------------------------------- #

    def scan(self, env: Environment) -> list[ReconcileFinding]:
        findings: list[ReconcileFinding] = []
        for check in self._checks:
            findings.extend(check.run(env))
        return findings

    # ----- Apply (mutating) ---------------------------------------- #

    def apply(
        self,
        env: Environment,
        findings: Iterable[ReconcileFinding],
    ) -> list[ReconcileFinding]:
        """Apply every ``kind="update"`` finding to the appropriate
        backlog. Orphans and info findings are skipped (caller's call).

        Returns the list of findings that were actually applied. The
        caller is responsible for calling ``env.registry.save_all()``
        after this method if they want the changes persisted.
        """
        applied: list[ReconcileFinding] = []
        for f in findings:
            if f.kind != "update" or not f.backlog or not f.slug:
                continue
            bl = env.registry[f.backlog]
            entry = bl.get(f.slug)
            if entry is None:
                # Medium aggression: we do NOT create entries. Flag only.
                continue
            entry.update(f.patch)
            bl.upsert(entry)
            applied.append(f)
        return applied
