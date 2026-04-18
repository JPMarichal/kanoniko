"""Capture the golden-query oracle from the Neo4j live stack.

Purpose: ejecutar cada query de ``golden_queries.yaml`` contra el stack
Neo4j+SQLite actual y persistir los resultados como ``oracle.json``. Ese JSON
se usa después como "verdad de referencia" cuando se ejecuten las mismas
queries contra ``postgres_graph_client`` (Fase 3 port, paridad test).

Uso::

    # Con túnel SSH arriba + Neo4j alcanzable vía docker_default
    python -m tests.parity.capture_oracle \
        --yaml tests/parity/golden_queries.yaml \
        --out  tests/parity/oracle.json

Diseño:
    * Lee el YAML, agrupa por método.
    * Para cada query, instancia Neo4jClient y llama al método con los args.
    * Serializa el resultado (dicts/lists de dicts) a JSON.
    * Incluye el hash SHA-256 del gazetteer para invalidar oracle si cambia.
    * No valida expectations — eso es otro script. Aquí solo captura.

El resultado se commitea al repo como ``oracle.json`` para que el test
de paridad sea reproducible sin volver a tocar Neo4j live.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        logger.error("pyyaml not installed. pip install pyyaml")
        raise
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _gazetteer_hash() -> str:
    """Hash del gazetteer para detectar invalidación del oracle."""
    gp = (
        Path(__file__).resolve().parent.parent.parent
        / "src" / "alejandria" / "knowledge" / "gazetteers" / "entities.json"
    )
    if not gp.exists():
        return ""
    return hashlib.sha256(gp.read_bytes()).hexdigest()[:16]


def _serialize(obj: Any) -> Any:
    """Recursive JSON-friendly serialization para dataclasses y dicts anidados."""
    from dataclasses import asdict, is_dataclass

    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if is_dataclass(obj):
        return _serialize(asdict(obj))
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    return str(obj)


def _dispatch(client, method: str, args: dict) -> Any:
    """Llama ``method`` de ``client`` con ``args`` como kwargs.

    Maneja conversión de listas/strings. No tolera fallos — si un método
    no existe o rechaza args, se levanta y el caller decide.
    """
    fn = getattr(client, method, None)
    if fn is None:
        raise AttributeError(f"Neo4jClient has no method {method!r}")
    return fn(**args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture golden-query oracle from Neo4j.")
    parser.add_argument("--yaml", type=Path, default=Path("tests/parity/golden_queries.yaml"))
    parser.add_argument("--out", type=Path, default=Path("tests/parity/oracle.json"))
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    spec = _load_yaml(args.yaml)
    queries = spec.get("queries", [])
    logger.info("loaded %d queries from %s", len(queries), args.yaml)

    from alejandria.knowledge.neo4j_client import Neo4jClient
    client = Neo4jClient()

    oracle: dict[str, Any] = {
        "version": spec.get("version"),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "captured_against": spec.get("captured_against", "unknown"),
        "gazetteer_hash_prefix": _gazetteer_hash(),
        "results": {},
    }

    ok = 0
    failed = 0
    for q in queries:
        qid = q.get("id")
        method = q.get("method")
        qargs = q.get("args") or {}
        try:
            t0 = time.perf_counter()
            result = _dispatch(client, method, qargs)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            oracle["results"][qid] = {
                "method": method,
                "args": qargs,
                "elapsed_ms": round(elapsed_ms, 2),
                "result": _serialize(result),
            }
            ok += 1
            logger.info("  %-5s %s  %.1fms", qid, method, elapsed_ms)
        except Exception as e:
            failed += 1
            oracle["results"][qid] = {
                "method": method,
                "args": qargs,
                "error": f"{type(e).__name__}: {e}",
            }
            logger.error("  %-5s %s  FAILED: %s", qid, method, e)

    client.close()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(oracle, f, ensure_ascii=False, indent=2)

    logger.info("ok=%d failed=%d → %s", ok, failed, args.out)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
