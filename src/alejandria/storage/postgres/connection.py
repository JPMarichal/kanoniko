"""Postgres connection management using psycopg 3.

Thin wrapper that builds connection params from ``alejandria.config.settings``
and applies a per-connection ``statement_timeout``. Async pools are out of
scope for the migration phase — ingestion is sync by design and the API layer
uses psycopg's own pool when needed.

SSH tunnel notes
----------------
Two transports are supported for reaching the IONOS Postgres:

1. **Sidecar (recommended, default in Docker/Podman):** a dedicated ``autossh``
   container keeps a self-healing tunnel and exposes Postgres at ``tunnel:5432``.
   In that mode ``ALEJANDRIA_SSH_TUNNEL_ENABLED=false`` and this module just
   connects to ``postgres_host``/``postgres_port`` directly.

2. **In-process (fallback for host/WSL scripts, tests, one-off runs):** set
   ``ALEJANDRIA_SSH_TUNNEL_ENABLED=true`` and this module manages an SSH tunnel
   via ``sshtunnel``. The implementation is **self-healing**: it never trusts the
   stale ``is_active`` flag, sends SSH keepalives, and rebuilds the tunnel
   whenever it is found dead or a connection attempt fails.
"""

from __future__ import annotations

import atexit
import logging
import threading
from contextlib import contextmanager
from typing import Iterator

import psycopg

from alejandria.config import settings

logger = logging.getLogger(__name__)

# Guards the module-level tunnel singleton against concurrent (re)builds.
_tunnel = None
_tunnel_lock = threading.RLock()

# Keepalive interval (seconds) so idle SSH sessions are not dropped by the VPS
# or intermediate firewalls. Also lets the client detect a dead peer quickly.
_TUNNEL_KEEPALIVE_SECONDS = 30.0


def _tunnel_is_up(tunnel) -> bool:
    """Return True only if the tunnel is *actually* forwarding.

    ``sshtunnel`` leaves ``is_active`` set to True even after the underlying
    transport has died, so we additionally probe ``local_bind_port`` (which
    raises ``HandlerSSHTunnelForwarderError`` when not started) and refresh the
    per-forward liveness map. Any exception means "rebuild it".
    """
    if tunnel is None:
        return False
    try:
        if not getattr(tunnel, "is_active", False):
            return False
        # Refresh the liveness map; raises/returns False when the session died.
        try:
            tunnel.check_tunnels()
            statuses = getattr(tunnel, "tunnel_is_up", {}) or {}
            if statuses and not all(statuses.values()):
                return False
        except Exception:
            return False
        # Accessing local_bind_port raises if the forwarder is not started.
        _ = tunnel.local_bind_port
        return True
    except Exception:
        return False


def _stop_tunnel_locked() -> None:
    """Tear down the current tunnel. Caller must hold ``_tunnel_lock``."""
    global _tunnel
    if _tunnel is not None:
        try:
            _tunnel.stop(force=True)
            logger.info("SSH tunnel closed")
        except TypeError:
            # Older sshtunnel without force kwarg.
            try:
                _tunnel.stop()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error closing SSH tunnel: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Error closing SSH tunnel: %s", exc)
    _tunnel = None


def _start_tunnel_locked() -> None:
    """Build and start a fresh tunnel. Caller must hold ``_tunnel_lock``."""
    global _tunnel
    import sshtunnel

    pkey = settings.ssh_tunnel_private_key_path or None

    _tunnel = sshtunnel.open_tunnel(
        (settings.ssh_tunnel_host, settings.ssh_tunnel_port),
        ssh_username=settings.ssh_tunnel_user,
        ssh_pkey=pkey,
        ssh_private_key_password=settings.ssh_tunnel_private_key_password or None,
        remote_bind_address=("127.0.0.1", settings.ssh_tunnel_remote_port),
        local_bind_address=("127.0.0.1", settings.ssh_tunnel_local_port),
        compression=True,
        # Send SSH keepalives so idle sessions stay up and dead peers are
        # detected promptly instead of hanging.
        set_keepalive=_TUNNEL_KEEPALIVE_SECONDS,
    )
    _tunnel.start()
    logger.info(
        "SSH tunnel active: local 127.0.0.1:%s -> %s:%s -> remote localhost:%s",
        _tunnel.local_bind_port,
        settings.ssh_tunnel_host,
        settings.ssh_tunnel_port,
        settings.ssh_tunnel_remote_port,
    )


def _ensure_tunnel() -> None:
    """Ensure a live in-process tunnel exists (no-op when disabled).

    Self-healing: if the existing tunnel is dead/stale it is torn down and
    rebuilt. Trusting ``is_active`` alone was the root cause of the intermittent
    "Tunnels are not started" failures.
    """
    if not settings.ssh_tunnel_enabled:
        return
    with _tunnel_lock:
        if _tunnel_is_up(_tunnel):
            return
        if _tunnel is not None:
            logger.warning("SSH tunnel found dead/stale — rebuilding")
            _stop_tunnel_locked()
        _start_tunnel_locked()


def _reset_tunnel() -> None:
    """Force the next connection to rebuild the tunnel from scratch."""
    if not settings.ssh_tunnel_enabled:
        return
    with _tunnel_lock:
        _stop_tunnel_locked()


def _close_tunnel() -> None:
    with _tunnel_lock:
        _stop_tunnel_locked()


atexit.register(_close_tunnel)


def _tunnel_host() -> str:
    if settings.ssh_tunnel_enabled and _tunnel_is_up(_tunnel):
        return "127.0.0.1"
    return settings.postgres_host


def _tunnel_port() -> int:
    if settings.ssh_tunnel_enabled and _tunnel_is_up(_tunnel):
        try:
            return _tunnel.local_bind_port
        except Exception:
            return settings.ssh_tunnel_local_port
    return settings.postgres_port


def _conninfo() -> str:
    """Build a libpq-style connection string from settings.

    psycopg3 accepts URIs but libpq kwargs avoid quoting headaches with
    passwords containing ``@`` or ``/``.
    """
    parts = [
        f"host={_tunnel_host()}",
        f"port={_tunnel_port()}",
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


def _connect() -> psycopg.Connection:
    """Open a psycopg connection, (re)building the tunnel and retrying once.

    When the in-process tunnel is enabled and the first attempt fails with an
    ``OperationalError`` (typically because the tunnel died mid-flight), the
    tunnel is reset and a single retry is performed. This makes the write/read
    path resilient to transient SSH drops without a container restart.
    """
    options = _statement_timeout_option()
    kwargs: dict = {"autocommit": False}
    if options:
        kwargs["options"] = options

    attempts = 2 if settings.ssh_tunnel_enabled else 1
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        _ensure_tunnel()
        try:
            return psycopg.connect(_conninfo(), **kwargs)
        except psycopg.OperationalError as exc:
            last_exc = exc
            logger.warning(
                "Postgres connect failed (attempt %d/%d): %s",
                attempt,
                attempts,
                exc,
            )
            if settings.ssh_tunnel_enabled and attempt < attempts:
                _reset_tunnel()
                continue
            raise
    # Unreachable, but keeps type checkers happy.
    assert last_exc is not None
    raise last_exc


@contextmanager
def get_connection(autocommit: bool = False) -> Iterator[psycopg.Connection]:
    """Yield a psycopg connection configured from settings.

    Usage::

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    """
    conn = _connect()
    if autocommit:
        conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()
