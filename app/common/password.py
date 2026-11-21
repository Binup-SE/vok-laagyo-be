"""Password hashing helpers — bcrypt, same role as flask-bcrypt in user-api."""

from __future__ import annotations

import bcrypt


def _coerce_hash(value) -> str:
    """Coerce DB password hashes (bytes/memoryview) so bcrypt can verify them."""
    if value is None:
        return ""
    if isinstance(value, memoryview):
        value = value.tobytes()
    if isinstance(value, bytes):
        value = value.decode("utf-8", "ignore")
    return str(value)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(plain: str | None, hashed) -> bool:
    if plain is None or hashed is None:
        return False
    stored = _coerce_hash(hashed)
    if not stored:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
    except (ValueError, TypeError):
        return False
