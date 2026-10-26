"""Error responses that are helpful to users and reveal nothing internal.

Validation errors list each problem field in plain words. Unexpected errors are
logged for the operator (without the request body, which contains health answers)
and the user gets a generic message with no stack trace or file paths.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("vytal.errors")


def _field_name(location: tuple) -> str:
    parts = [str(part) for part in location if part != "body"]
    return ".".join(parts) or "body"


def _friendly_message(error: dict) -> str:
    kind = error.get("type", "")
    context = error.get("ctx") or {}
    if kind == "missing":
        return "This answer is required."
    if kind == "extra_forbidden":
        return "This field is not accepted."
    if kind == "literal_error":
        return f"Choose one of: {context.get('expected', 'the listed options')}."
    if kind in {"greater_than_equal", "greater_than"}:
        return f"Must be at least {context.get('ge', context.get('gt'))}."
    if kind in {"less_than_equal", "less_than"}:
        return f"Must be at most {context.get('le', context.get('lt'))}."
    if kind.startswith(("int_", "float_")):
        return "Must be a number."
    if kind == "json_invalid":
        return "The request is not valid JSON."
    return "This value is not valid."


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        errors = [{"field": _field_name(tuple(e.get("loc", ()))), "message": _friendly_message(e)} for e in exc.errors()]
        return JSONResponse({"detail": "Some answers need attention.", "errors": errors}, status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse({"detail": detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, type(exc).__name__, exc_info=exc)
        return JSONResponse({"detail": "Something went wrong on our side. Please try again."}, status_code=500)
