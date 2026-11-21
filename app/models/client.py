from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Client(BaseModel):
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(Text, nullable=False)
