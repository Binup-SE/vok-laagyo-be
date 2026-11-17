"""Single shared-Postgres helpers.

Adapted from shared-api pool/keepalive patterns — NOT multi-customer binds.
One engine, row-level tenant_id later via RLS + SET LOCAL.
"""

from __future__ import annotations

from flask import g, has_app_context, has_request_context
from sqlalchemy import text

from app.extensions import db

# Proxies / idle firewalls drop TCP under ~1h; recycle + keepalives (from shared-api).
POSTGRES_POOL_RECYCLE = 300
POSTGRES_POOL_SIZE = 5
POSTGRES_MAX_OVERFLOW = 10
POSTGRES_KEEPALIVE_ARGS = {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
}


def is_postgres_uri(uri: str | None) -> bool:
    return str(uri or "").startswith("postgresql")


def postgres_connect_args(base_connect_args: dict | None = None) -> dict:
    """libpq connect_args: timeout, keepalives, UTC. Shared schema stays on public."""
    connect_args = dict(base_connect_args or {})
    connect_args.setdefault("connect_timeout", 10)
    for key, value in POSTGRES_KEEPALIVE_ARGS.items():
        connect_args.setdefault(key, value)
    # Prefer UTC; do not invent per-tenant schemas.
    connect_args["options"] = connect_args.get("options") or "-c timezone=utc"
    return connect_args


def sqlalchemy_engine_options(database_uri: str | None) -> dict:
    """Flask-SQLAlchemy SQLALCHEMY_ENGINE_OPTIONS for our single Postgres."""
    if not is_postgres_uri(database_uri):
        return {"pool_pre_ping": True}

    return {
        "pool_pre_ping": True,
        "pool_recycle": POSTGRES_POOL_RECYCLE,
        "pool_size": POSTGRES_POOL_SIZE,
        "max_overflow": POSTGRES_MAX_OVERFLOW,
        "connect_args": postgres_connect_args(),
    }


def get_session():
    """Request-scoped SQLAlchemy session (Flask-SQLAlchemy)."""
    return db.session


def require_tenant_id():
    """Return g.tenant.id or raise — never trust client-supplied tenant_id."""
    from app.common.exceptions import UnknownTenantError

    tenant = getattr(g, "tenant", None) if has_request_context() else None
    if tenant is None:
        raise UnknownTenantError("No tenant on request")
    return tenant.id


def set_local_tenant_id(tenant_id) -> None:
    """Defense-in-depth for future RLS: SET LOCAL app.tenant_id on this connection.

    Safe to call before RLS policies exist; no-op-ish until policies read the GUC.
    Always pair with reset_local_tenant_id on teardown when using a pooled connection.
    """
    if tenant_id is None:
        return
    db.session.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )


def reset_local_tenant_id() -> None:
    """Clear request-local tenant GUC so pooled connections do not leak tenants."""
    if not has_app_context():
        return
    try:
        db.session.execute(text("SELECT set_config('app.tenant_id', '', true)"))
    except Exception:
        # Connection may already be closed / rolled back on teardown.
        pass


def ping_db() -> bool:
    """Lightweight connectivity check for health endpoints."""
    db.session.execute(text("SELECT 1"))
    return True
