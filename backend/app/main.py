import json
import logging
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.routes import router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.http import error_response


logger = logging.getLogger("linkdb")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.info("%s %s %s", request.method, request.url.path, response.status_code)
        return response


class OriginGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        origin = request.headers.get("origin")
        if origin and origin not in settings.allowed_cors_origins:
            return error_response(
                "INTERNAL_SERVER_ERROR",
                "Origin not allowed by CORS.",
                500,
            )
        return await call_next(request)


def build_validation_details(exc: RequestValidationError) -> dict[str, object]:
    field_errors: dict[str, list[str]] = defaultdict(list)
    form_errors: list[str] = []

    for error in exc.errors():
        location = [
            str(part) for part in error["loc"] if part not in {"body", "query", "path"}
        ]
        if location:
            field_errors[".".join(location)].append(error["msg"])
        else:
            form_errors.append(error["msg"])

    return {
        "formErrors": form_errors,
        "fieldErrors": dict(field_errors),
    }


def create_app() -> FastAPI:
    settings = get_settings()
    settings.assert_production_secrets()

    app = FastAPI()
    app.add_middleware(OriginGuardMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggerMiddleware)
    app.include_router(router)

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> Response:
        return error_response(exc.code, exc.message, exc.status_code, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> Response:
        if any(error["type"] == "json_invalid" for error in exc.errors()):
            return error_response(
                "INVALID_JSON",
                "Request body contains invalid JSON.",
                400,
            )
        return error_response(
            "VALIDATION_ERROR",
            "Request validation failed.",
            400,
            build_validation_details(exc),
        )

    @app.exception_handler(json.JSONDecodeError)
    async def json_error_handler(_request: Request, _exc: json.JSONDecodeError) -> Response:
        return error_response("INVALID_JSON", "Request body contains invalid JSON.", 400)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> Response:
        if exc.status_code == 404:
            return error_response(
                "NOT_FOUND",
                f"Route {request.method} {request.url.path} not found.",
                404,
            )
        return error_response("HTTP_ERROR", str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def unexpected_error_handler(_request: Request, exc: Exception) -> Response:
        logger.exception("Unhandled error", exc_info=exc)
        message = (
            "Internal server error."
            if settings.is_production
            else "An unexpected error occurred."
        )
        return error_response("INTERNAL_SERVER_ERROR", message, 500)

    return app


app = create_app()
