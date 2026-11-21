"""Bootstrap a local development user on the dev client."""

from __future__ import annotations

from app.common.password import hash_password
from app.extensions import db
from app.models import User
from seeds.client_seed import seed_dev_client

DEV_USER_EMAIL = "dev@voklaagyo.com"
DEV_USER_PASSWORD = "devpassword"


def seed_dev_user() -> User:
    client = seed_dev_client()
    existing = User.query.filter_by(email=DEV_USER_EMAIL).first()
    if existing is not None:
        if existing.client_id != client.id:
            existing.client_id = client.id
            db.session.commit()
        return existing

    user = User(
        email=DEV_USER_EMAIL,
        first_name="Dev",
        last_name="User",
        password=hash_password(DEV_USER_PASSWORD),
        validated=True,
        is_admin=True,
        client_id=client.id,
        user_type="owner",
    )
    db.session.add(user)
    db.session.commit()
    return user
