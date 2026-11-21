"""User serializers — Vok-sized stand-in for user-api marshmallow schemas."""

from __future__ import annotations

from app.models import User


def serialize_login_user(user: User) -> dict:
    first = user.first_name or ""
    last = user.last_name or ""
    name = f"{first} {last}".strip() or None
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": name,
        "is_admin": user.is_admin,
        "is_guest": user.is_guest,
        "picture": user.picture,
        "color": user.color,
        "job_title": user.job_title,
        "user_type": user.user_type,
        "client_id": str(user.client_id) if user.client_id else None,
        "validated": user.validated,
    }
