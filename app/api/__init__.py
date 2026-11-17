from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api import auth_routes, health, tenant_info  # noqa: E402, F401
