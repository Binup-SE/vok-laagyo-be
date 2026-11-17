"""Auth helpers adapted from user-api — JWT includes tenant_id and must match Host."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

import bcrypt
import jwt
from flask import current_app, g, request

from app.common.exceptions import (
    ForbiddenError,
    InvalidTokenError,
    MissingTokenError,
    TenantMismatchError,
    UnauthorizedError,
)
from app.models import Membership, User

ROLES = ("owner", "manager", "staff")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    *,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    role: str,
    email: str,
) -> str:
    minutes = int(current_app.config.get("JWT_EXPIRE_MINUTES", 60 * 24))
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _extract_token() -> str | None:
    # Prefer user-api style header; also accept Bearer for modern clients.
    if "X-Access-Token" in request.headers:
        return request.headers.get("X-Access-Token")
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError() from exc


def authenticate_request(func: Callable):
    """Require JWT; claim tenant_id must equal Host-resolved g.tenant.id."""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            raise MissingTokenError()

        tenant = getattr(g, "tenant", None)
        if tenant is None:
            raise UnauthorizedError("No tenant on request", key="UNKNOWN_TENANT")

        claims = decode_access_token(token)
        claim_tenant = claims.get("tenant_id")
        claim_user = claims.get("user_id")
        if not claim_tenant or not claim_user:
            raise InvalidTokenError("Token missing tenant_id or user_id")

        if str(claim_tenant) != str(tenant.id):
            raise TenantMismatchError()

        user = User.query.filter_by(id=claim_user).first()
        if user is None:
            raise UnauthorizedError("User not found", key="USER_NOT_FOUND")

        membership = Membership.query.filter_by(
            user_id=user.id,
            tenant_id=tenant.id,
        ).first()
        if membership is None:
            raise ForbiddenError("No membership for this tenant", key="NO_MEMBERSHIP")

        g.user = user
        g.membership = membership
        g.role = membership.role
        return func(*args, **kwargs)

    return decorated


def require_roles(*roles: str):
    """Restrict route to membership roles (owner | manager | staff)."""

    allowed = set(roles)

    def decorator(func: Callable):
        @wraps(func)
        @authenticate_request
        def decorated(*args, **kwargs):
            if g.role not in allowed:
                raise ForbiddenError("Insufficient role", key="FORBIDDEN_ROLE")
            return func(*args, **kwargs)

        return decorated

    return decorator
