"""Dev owners for cafe-roma / spice-house. Password for both: password"""

from __future__ import annotations

import uuid

from app.common.auth import hash_password
from app.extensions import db
from app.models import Membership, Tenant, User
from seeds.tenants import CAFE_ROMA_ID, SPICE_HOUSE_ID

# Fixed IDs so seeds stay stable across re-runs.
OWNER_CAFE_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_SPICE_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

DEV_OWNERS = (
    {
        "id": OWNER_CAFE_ID,
        "email": "owner@cafe-roma.test",
        "name": "Cafe Roma Owner",
        "tenant_id": CAFE_ROMA_ID,
        "role": "owner",
    },
    {
        "id": OWNER_SPICE_ID,
        "email": "owner@spice-house.test",
        "name": "Spice House Owner",
        "tenant_id": SPICE_HOUSE_ID,
        "role": "owner",
    },
)

DEV_PASSWORD = "password"


def run() -> list[str]:
    created: list[str] = []
    password_hash = hash_password(DEV_PASSWORD)

    for row in DEV_OWNERS:
        tenant = Tenant.query.filter_by(id=row["tenant_id"]).first()
        if tenant is None:
            continue

        user = User.query.filter_by(email=row["email"]).first()
        if user is None:
            user = User(
                id=row["id"],
                email=row["email"],
                name=row["name"],
                password_hash=password_hash,
            )
            db.session.add(user)
            db.session.flush()
            created.append(row["email"])

        membership = Membership.query.filter_by(
            user_id=user.id,
            tenant_id=tenant.id,
        ).first()
        if membership is None:
            db.session.add(
                Membership(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    role=row["role"],
                )
            )
            if row["email"] not in created:
                created.append(f"membership:{row['email']}")

    if created:
        db.session.commit()
    return created
