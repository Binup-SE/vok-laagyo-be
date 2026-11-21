"""Single shared-Postgres helpers.

Adapted from shared-api pool/keepalive patterns — NOT multi-customer binds.
"""

from __future__ import annotations  # noqa: I001 — required on Python 3.9

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
    """libpq connect_args: timeout, keepalives, UTC."""
    connect_args = dict(base_connect_args or {})
    connect_args.setdefault("connect_timeout", 10)
    for key, value in POSTGRES_KEEPALIVE_ARGS.items():
        connect_args.setdefault(key, value)
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


def ping_db() -> bool:
    """Lightweight connectivity check for health endpoints."""
    db.session.execute(text("SELECT 1"))
    return True
