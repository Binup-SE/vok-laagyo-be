"""User model — Reg-1 user shape with client_id instead of firm_id."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    password: Mapped[Optional[str]] = mapped_column(String(255))
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    job_title: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(255))

    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    color: Mapped[Optional[str]] = mapped_column(String(255))
    picture: Mapped[Optional[str]] = mapped_column(String(255))
    is_guest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    work_schedule: Mapped[Optional[str]] = mapped_column(String(255))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    start_date: Mapped[Optional[str]] = mapped_column(String(255))
    end_date: Mapped[Optional[str]] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_type: Mapped[Optional[str]] = mapped_column(String(255))
    line_manager: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    password_history: Mapped[Optional[Any]] = mapped_column(JSONB)
    is_disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    client = relationship("Client", foreign_keys=[client_id])
