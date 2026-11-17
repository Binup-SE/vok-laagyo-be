import os

from dotenv import load_dotenv

from app.common.db import sqlalchemy_engine_options

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ENV = os.getenv("ENV", os.getenv("FLASK_ENV", "production"))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://vok:vok@localhost:5432/vok_laagyo",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = sqlalchemy_engine_options(SQLALCHEMY_DATABASE_URI)
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "voklaagyo.com")
    # Path /m/:slug is only for local/dev fallback — never production primary.
    ALLOW_PATH_TENANT = _env_bool(
        "ALLOW_PATH_TENANT",
        default=ENV.strip().lower() in {"development", "dev", "local"},
    )
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24)))


    @property
    def is_development(self) -> bool:
        return self.ENV.strip().lower() in {"development", "dev", "local"}
