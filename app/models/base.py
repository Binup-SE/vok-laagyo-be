"""Shared model bases — adapted from reg1-database-manager Base patterns.

Differences for Vok:
- UUID primary keys (not autoincrement ints)
- timestamptz created_at (not MySQL ON UPDATE)
- TenantScopedMixin for row-level tenant_id (shared schema)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        default=lambda: datetime.now(timezone.utc),
    )


class TenantScopedMixin:
    """Every tenant-owned business table should include this."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class BaseModel(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    """UUID + created_at. Use for platform tables (tenants, users, …)."""

    __abstract__ = True


class TenantBaseModel(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, db.Model):
    """UUID + created_at + tenant_id. Use for menus, items, settings, …"""

    __abstract__ = True
