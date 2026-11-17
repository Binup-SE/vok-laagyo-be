from flask import g, request

from app.api import api_bp
from app.common.auth import (
    authenticate_request,
    check_password,
    create_access_token,
)
from app.common.exceptions import BadRequestError, UnauthorizedError
from app.common.response import Response
from app.models import Membership, User


@api_bp.post("/auth/login")
def login():
    """Password login bound to Host-resolved tenant (JWT includes tenant_id)."""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        raise BadRequestError("email and password are required")

    tenant = g.tenant
    user = User.query.filter_by(email=email).first()
    if user is None or not check_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password", key="INVALID_CREDENTIALS")

    membership = Membership.query.filter_by(
        user_id=user.id,
        tenant_id=tenant.id,
    ).first()
    if membership is None:
        raise UnauthorizedError(
            "No membership for this restaurant",
            key="NO_MEMBERSHIP",
        )

    token = create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        role=membership.role,
        email=user.email,
    )
    return Response.success(
        {
            "access_token": token,
            "token_type": "Bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            },
            "tenant": {
                "id": str(tenant.id),
                "slug": tenant.slug,
                "name": tenant.name,
            },
            "role": membership.role,
        }
    )


@api_bp.get("/auth/me")
@authenticate_request
def me():
    user = g.user
    tenant = g.tenant
    return Response.success(
        {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            },
            "tenant": {
                "id": str(tenant.id),
                "slug": tenant.slug,
                "name": tenant.name,
            },
            "role": g.role,
        }
    )
