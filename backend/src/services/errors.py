"""Domain-level HTTP-mappable errors (shared by services and repositories)."""

from __future__ import annotations


class ErrorCode:
    VALIDATION = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN_ERROR"


class DomainError(Exception):
    status_code: int = 500
    error_code: str = ErrorCode.UNKNOWN

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    status_code = 400
    error_code = ErrorCode.VALIDATION


class NotFoundError(DomainError):
    status_code = 404
    error_code = ErrorCode.NOT_FOUND


class ConflictError(DomainError):
    status_code = 409
    error_code = ErrorCode.CONFLICT
