from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api import health  # noqa: E402, F401
from app.api.users import users_bp  # noqa: E402, F401

api_bp.register_blueprint(users_bp, url_prefix="/users")
