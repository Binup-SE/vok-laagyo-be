"""Application exceptions — keyed for FE handling (shared-api style, Vok-sized)."""


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


class MissingTokenError(UnauthorizedError):
    key = "MISSING_TOKEN"

    def __init__(self, message: str = "Missing token"):
        super().__init__(message)


class InvalidTokenError(UnauthorizedError):
    key = "INVALID_TOKEN"

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class ForbiddenError(AppError):
    status_code = 403
    key = "FORBIDDEN"


class TenantMismatchError(ForbiddenError):
    key = "TENANT_MISMATCH"

    def __init__(self, message: str = "Token tenant does not match host"):
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    key = "NOT_FOUND"


class UnknownTenantError(NotFoundError):
    key = "UNKNOWN_TENANT"

    def __init__(self, message: str = "Unknown host"):
        super().__init__(message)


class TenantUnavailableError(ForbiddenError):
    key = "TENANT_UNAVAILABLE"

    def __init__(self, message: str = "Tenant unavailable"):
        super().__init__(message)


class ConflictError(AppError):
    status_code = 409
    key = "CONFLICT"
