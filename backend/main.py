from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import logging
import traceback
from starlette.requests import Request

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.db.database import dispose_engine
from app.middleware.error_handler import app_exception_handler, validation_exception_handler
from app.middleware.logging import logging_middleware
from app.middleware.request_id import request_id_middleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await dispose_engine()


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logging.exception("Unhandled exception during request: %s %s", request.method, request.url)
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    settings = get_settings()
    if settings.is_production:
        content = {"detail": "An unexpected server error occurred"}
    else:
        content = {"detail": str(exc), "traceback": tb}
    return ORJSONResponse(status_code=500, content=content)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    @app.middleware("http")
    async def ensure_cors_headers(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as exc:
            # Delegate to the unified unhandled exception handler so development
            # tracebacks are included in the response content.
            response = await unhandled_exception_handler(request, exc)
        origin = request.headers.get("origin")
        if origin:
            response.headers.setdefault("Access-Control-Allow-Origin", origin)
            response.headers.setdefault("Access-Control-Allow-Credentials", "true")
            response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
            response.headers.setdefault("Access-Control-Allow-Headers", "Authorization,Content-Type,Accept")
        else:
            response.headers.setdefault("Access-Control-Allow-Origin", "*")
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_id_middleware)
    app.middleware("http")(logging_middleware)

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(api_router, prefix=settings.api_v1_prefix)



    return app


app = create_app()
