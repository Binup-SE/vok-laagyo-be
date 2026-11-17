"""Seed Tenant A / Tenant B for Host isolation checks."""

from __future__ import annotations

import uuid

from app.extensions import db
from app.models import Tenant

CAFE_ROMA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
SPICE_HOUSE_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")

DEV_TENANTS = (
    {
        "id": CAFE_ROMA_ID,
        "slug": "cafe-roma",
        "name": "Cafe Roma",
        "status": "active",
    },
    {
        "id": SPICE_HOUSE_ID,
        "slug": "spice-house",
        "name": "Spice House",
        "status": "active",
    },
)


def run() -> list[str]:
    """Insert missing dev tenants. Idempotent on slug."""
    created: list[str] = []
    for row in DEV_TENANTS:
        existing = Tenant.query.filter_by(slug=row["slug"]).first()
        if existing is not None:
            continue
        db.session.add(Tenant(**row))
        created.append(row["slug"])
    if created:
        db.session.commit()
    return created
