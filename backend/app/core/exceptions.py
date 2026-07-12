from typing import Any


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status_code=403)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message, status_code=422, errors=errors)
