from sqlalchemy.exc import SQLAlchemyError

from app.api import api_bp
from app.common.db import ping_db
from app.common.response import Response


@api_bp.get("/health")
def health():
    try:
        ping_db()
    except SQLAlchemyError:
        return Response.error(
            "Database unavailable",
            key="DB_UNAVAILABLE",
            status_code=503,
        )

    return Response.success({"ok": True, "db": True})
