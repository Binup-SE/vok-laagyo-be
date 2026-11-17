"""JSON response envelope — adapted from shared-api Response helpers."""

from __future__ import annotations

from flask import jsonify, make_response

from app.common.exceptions import AppError


class Response:
    @staticmethod
    def success(data=None, status_code: int = 200):
        return make_response(
            jsonify(success=True, data=data),
            status_code,
        )

    @staticmethod
    def error(
        message: str,
        *,
        key: str = "BAD_REQUEST",
        status_code: int = 400,
        errors=None,
    ):
        payload = {
            "success": False,
            "message": str(message),
            "key": key,
        }
        if errors is not None:
            payload["errors"] = errors
        return make_response(jsonify(payload), status_code)

    @staticmethod
    def from_error(exc: AppError):
        return Response.error(
            exc.message,
            key=exc.key,
            status_code=exc.status_code,
        )

    @staticmethod
    def bad_request(message, key: str = "BAD_REQUEST"):
        return Response.error(message, key=key, status_code=400)

    @staticmethod
    def unauthorized(message, key: str = "UNAUTHORIZED"):
        return Response.error(message, key=key, status_code=401)

    @staticmethod
    def forbidden(message, key: str = "FORBIDDEN"):
        return Response.error(message, key=key, status_code=403)

    @staticmethod
    def not_found(message, key: str = "NOT_FOUND"):
        return Response.error(message, key=key, status_code=404)

    @staticmethod
    def conflict(message, key: str = "CONFLICT"):
        return Response.error(message, key=key, status_code=409)

    @staticmethod
    def server_error(
        message: str = "Failed to process request.",
        key: str = "SERVER_ERROR",
    ):
        return Response.error(message, key=key, status_code=500)
