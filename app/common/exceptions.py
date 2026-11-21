"""Application exceptions — keyed for FE handling (shared-api style, Vok-sized)."""

from __future__ import annotations


class AppError(Exception):
    """Base API error with stable machine key + HTTP status."""

    status_code = 400
    key = "BAD_REQUEST"

    def __init__(self, message: str = "Bad request", *, key: str | None = None):
        super().__init__(message)
        self.message = message
        if key is not None:
            self.key = key


class BadRequestError(AppError):
    status_code = 400
    key = "BAD_REQUEST"


class UnauthorizedError(AppError):
    status_code = 401
    key = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = 403
    key = "FORBIDDEN"


class NotFoundError(AppError):
    status_code = 404
    key = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    key = "CONFLICT"
