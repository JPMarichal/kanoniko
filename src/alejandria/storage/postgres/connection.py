"""Postgres connection management using psycopg 3.

Thin wrapper that builds connection params from ``alejandria.config.settings``
and applies a per-connection ``statement_timeout``. Async pools are out of
scope for the migration phase — ingestion is sync by design and the API layer
uses psycopg's own pool when needed.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import psycopg

from alejandria.config import settings

logger = logging.getLogger(__name__)


def _conninfo() -> str:
    """Build a libpq-style connection string from settings.

    psycopg3 accepts URIs but libpq kwargs avoid quoting headaches with
    passwords containing ``@`` or ``/``.
    """
    parts = [
        f"host={settings.postgres_host}",
        f"port={settings.postgres_port}",
        f"dbname={settings.postgres_db}",
        f"user={settings.postgres_user}",
        f"sslmode={settings.postgres_sslmode}",
        f"application_name={settings.postgres_application_name}",
    ]
    if settings.postgres_password:
        parts.append(f"password={settings.postgres_password}")
    return " ".join(parts)


def _statement_timeout_option() -> str | None:
    ms = settings.postgres_statement_timeout_ms
    if ms <= 0:
        return None
    return f"-c statement_timeout={ms}"


@contextmanager
def get_connection(autocommit: bool = False) -> Iterator[psycopg.Connection]:
    """Yield a psycopg connection configured from settings.

    Usage::

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    """
    options = _statement_timeout_option()
    kwargs: dict = {"autocommit": autocommit}
    if options:
        kwargs["options"] = options
    conn = psycopg.connect(_conninfo(), **kwargs)
    try:
        yield conn
    finally:
        conn.close()
