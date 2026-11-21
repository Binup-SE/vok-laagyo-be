"""User routes — login surface aligned with user-api (/finduser, /login, /logout)."""

from __future__ import annotations

from flask import g, request

from app.api.users import users_bp
from app.api.users.serializer import serialize_login_user
from app.common.auth import authenticate_request, create_access_token
from app.common.password import check_password
from app.common.response import Response
from app.models import User


def _email_password_login():
    """Shared email/password login used by /finduser and /login."""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip()
    password = body.get("password")

    if not email or password is None:
        return Response.bad_request(
            "Email and password are required.",
            key="MISSING_CREDENTIALS",
        )

    user = User.query.filter_by(email=email).first()
    if user is None or user.is_deleted or user.is_disabled:
        return Response.not_found(
            "Invalid Username or Password.",
            key="USER_NOT_FOUND",
        )

    if not check_password(password, user.password):
        return Response.forbidden(
            "Invalid Username or Password.",
            key="INVALID_CREDENTIALS",
        )

    token = create_access_token(
        email=user.email,
        user_id=user.id,
        client_id=user.client_id,
    )
    return Response.success(
        {
            "token": token,
            "user": serialize_login_user(user),
        }
    )


@users_bp.post("/finduser")
def finduser():
    """User login — same route name as user-api POST /finduser."""
    return _email_password_login()


@users_bp.post("/login")
def login():
    """Email/password login alias."""
    return _email_password_login()


@users_bp.post("/logout")
@authenticate_request
def logout():
    """Client should drop the JWT; no server session store yet."""
    return Response.success({"message": "Logged out successfully"})


@users_bp.get("/me")
@authenticate_request
def me():
    """Return the authenticated user (smoke-test for X-Access-Token)."""
    return Response.success(serialize_login_user(g.user))
