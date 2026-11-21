"""users

Revision ID: 002_users
Revises: 001_clients
Create Date: 2026-11-18

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_users"
down_revision: Union[str, None] = "001_clients"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=True),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("job_title", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("color", sa.String(length=255), nullable=True),
        sa.Column("picture", sa.String(length=255), nullable=True),
        sa.Column("is_guest", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("work_schedule", sa.String(length=255), nullable=True),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_date", sa.String(length=255), nullable=True),
        sa.Column("end_date", sa.String(length=255), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("user_type", sa.String(length=255), nullable=True),
        sa.Column("line_manager", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("password_history", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_disabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "date_added",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "date_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["line_manager"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_client_id", "users", ["client_id"], unique=False)
    op.create_index("ix_users_added_by", "users", ["added_by"], unique=False)
    op.create_index("ix_users_updated_by", "users", ["updated_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_updated_by", table_name="users")
    op.drop_index("ix_users_added_by", table_name="users")
    op.drop_index("ix_users_client_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
