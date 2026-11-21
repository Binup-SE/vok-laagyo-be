"""JWT auth helpers — adapted from user-api/api/common/auth.py."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any
from uuid import UUID

import jwt
from flask import current_app, g, request

from app.common.exceptions import UnauthorizedError
from app.common.response import Response
from app.models import User


def create_access_token(*, email: str, user_id: UUID, client_id: UUID | None = None) -> str:
    expire_minutes = int(current_app.config.get("JWT_EXPIRE_MINUTES", 60 * 24))
    payload: dict[str, Any] = {
        "user": email,
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expire_minutes),
    }
    if client_id is not None:
        payload["client_id"] = str(client_id)
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _load_user_from_token(token: str) -> User:
    try:
        data = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Expired Token.", key="EXPIRED_TOKEN") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid Token.", key="INVALID_TOKEN") from exc

    email = data.get("user")
    user_id = data.get("user_id")
    query = User.query.filter_by(is_deleted=False, is_disabled=False)
    if user_id:
        user = query.filter_by(id=user_id).first()
    elif email:
        user = query.filter_by(email=email).first()
    else:
        user = None

    if user is None:
        raise UnauthorizedError("User not found.", key="USER_NOT_FOUND")
    return user


def authenticate_request(func):
    """Require JWT in X-Access-Token (user-api header convention)."""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Access-Token")
        if not token:
            return Response.unauthorized("Missing Token.", key="MISSING_TOKEN")
        try:
            g.user = _load_user_from_token(token)
        except UnauthorizedError as exc:
            return Response.from_error(exc)
        return func(*args, **kwargs)

    return decorated
