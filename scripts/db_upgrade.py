"""Apply pending Alembic migrations (reg1 db_upgrade.py idea, without deleting versions)."""

from __future__ import annotations

import logging

from flask_migrate import upgrade

from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vok.db_upgrade")


def main() -> None:
    app = create_app()
    with app.app_context():
        logger.info("Applying migrations (upgrade head)...")
        upgrade()
        logger.info("DB upgrade completed.")


if __name__ == "__main__":
    main()
