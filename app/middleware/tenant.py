from __future__ import annotations

from flask import Flask, current_app, g, request
from sqlalchemy.exc import SQLAlchemyError

from app.common.exceptions import AppError, TenantUnavailableError, UnknownTenantError
from app.models import Tenant, TenantDomain


class DatabaseUnavailableError(AppError):
    status_code = 503
    key = "DB_UNAVAILABLE"

    def __init__(self, message: str = "Database unavailable"):
        super().__init__(message)



def _normalize_host(raw: str | None) -> str | None:
    if not raw:
        return None
    host = raw.split(",")[0].strip().lower()
    if not host:
        return None
    # Strip port (localhost:5000, cafe-roma.voklaagyo.localhost:3000)
    if host.startswith("[") and "]" in host:
        end = host.find("]")
        host = host[: end + 1]
    elif ":" in host:
        host = host.rsplit(":", 1)[0]
    return host or None


def _slug_from_subdomain(host: str, base_domain: str) -> str | None:
    base = base_domain.lower().lstrip(".")
    if host == base or host == f"www.{base}":
        return None
    suffix = f".{base}"
    if not host.endswith(suffix):
        return None
    label = host[: -len(suffix)]
    if not label or "." in label:
        # Only first-level subdomain for now (no nested a.b.base)
        return None
    return label


def _slug_from_path() -> str | None:
    # /m/:slug or /m/:slug/api/... (dev path fallback only)
    parts = [p for p in request.path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "m":
        return parts[1]
    return None


def resolve_tenant() -> Tenant | None:
    """Resolve tenant from Host (custom domain → subdomain). Never from client tenant_id."""
    host = _normalize_host(request.host)
    if not host:
        return None

    domain = TenantDomain.query.filter_by(hostname=host).first()
    if domain is not None:
        return domain.tenant

    base_domain = current_app.config["BASE_DOMAIN"]
    slug = _slug_from_subdomain(host, base_domain)
    if slug:
        tenant = Tenant.query.filter_by(slug=slug).first()
        if tenant is not None:
            return tenant

    if current_app.config.get("ALLOW_PATH_TENANT"):
        path_slug = _slug_from_path()
        if path_slug:
            return Tenant.query.filter_by(slug=path_slug).first()

    return None


def register_tenant_middleware(app: Flask) -> None:
    skip_endpoints = {"api.health"}

    @app.before_request
    def _attach_tenant() -> None:
        if not request.path.startswith("/api/"):
            return
        if request.endpoint in skip_endpoints:
            g.tenant = None
            return

        try:
            tenant = resolve_tenant()
        except SQLAlchemyError as exc:
            raise DatabaseUnavailableError() from exc

        if tenant is None:
            raise UnknownTenantError()
        if tenant.status == "suspended":
            raise TenantUnavailableError()

        g.tenant = tenant
