"""Bootstrap a local development client."""

from __future__ import annotations

from app.extensions import db
from app.models import Client

DEV_CLIENT_NAME = "dev"


def seed_dev_client() -> Client:
    existing = Client.query.filter_by(name=DEV_CLIENT_NAME).first()
    if existing is not None:
        return existing

    client = Client(name=DEV_CLIENT_NAME)
    db.session.add(client)
    db.session.commit()
    return client
