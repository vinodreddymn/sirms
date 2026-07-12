from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from app.core.exceptions import AppException
from app.core.response import ApiResponse, ErrorDetail


async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
    response = ApiResponse[None](
        success=False,
        message=exc.message,
        errors=[ErrorDetail(**error) for error in exc.errors] if exc.errors else None,
        request_id=getattr(request.state, "request_id", None),
    )
    return ORJSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> ORJSONResponse:
    response = ApiResponse[None](
        success=False,
        message="Validation error",
        errors=[
            ErrorDetail(field=".".join(str(part) for part in error["loc"]), message=error["msg"])
            for error in exc.errors()
        ],
        request_id=getattr(request.state, "request_id", None),
    )
    return ORJSONResponse(status_code=422, content=response.model_dump(mode="json"))
