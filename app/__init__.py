from flask import Flask

from app.api import api_bp
from app.common.db import reset_local_tenant_id, set_local_tenant_id
from app.common.exceptions import AppError
from app.common.response import Response
from app.config import Config
from app.extensions import db, migrate
from app.middleware import register_tenant_middleware


def create_app(config_object: type[Config] | Config | None = None) -> Flask:
    app = Flask(__name__)
    cfg = config_object() if isinstance(config_object, type) else (config_object or Config())
    app.config.from_mapping(
        ENV=cfg.ENV,
        SECRET_KEY=cfg.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=cfg.SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=cfg.SQLALCHEMY_TRACK_MODIFICATIONS,
        SQLALCHEMY_ENGINE_OPTIONS=cfg.SQLALCHEMY_ENGINE_OPTIONS,
        BASE_DOMAIN=cfg.BASE_DOMAIN,
        ALLOW_PATH_TENANT=cfg.ALLOW_PATH_TENANT,
        JWT_EXPIRE_MINUTES=cfg.JWT_EXPIRE_MINUTES,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate / Alembic see metadata
    from app import models  # noqa: F401

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    register_tenant_middleware(app)
    _register_error_handlers(app)
    _register_db_hooks(app)

    from seeds.cli import register_seed_commands

    register_seed_commands(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def _handle_app_error(exc: AppError):
        return Response.from_error(exc)

    @app.errorhandler(404)
    def _handle_not_found(_exc):
        return Response.not_found("Not found")

    @app.errorhandler(500)
    def _handle_server_error(_exc):
        return Response.server_error()


def _register_db_hooks(app: Flask) -> None:
    @app.before_request
    def _apply_tenant_guc():
        from flask import g, request

        if not request.path.startswith("/api/"):
            return
        tenant = getattr(g, "tenant", None)
        if tenant is not None:
            set_local_tenant_id(tenant.id)

    @app.teardown_request
    def _cleanup_db(exc=None):
        reset_local_tenant_id()
        db.session.remove()
