from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status

from app.domain.exceptions import (
    DomainError,
    UserAlreadyExists,
    InvalidCredentials,
    InvalidActivationCode,
    ActivationCodeExpired,
    UserAlreadyActive
)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(
        InvalidActivationCode, invalid_activation_code_handler
    )
    app.add_exception_handler(
        ActivationCodeExpired, activation_code_expired_handler
    )
    app.add_exception_handler(UserAlreadyActive, user_already_active_handler)


def domain_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Domain error"},
    )


def user_already_exists_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User already exists"},
    )


def invalid_credentials_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid credentials"},
        headers={"WWW-Authenticate": "Basic"},
    )


def invalid_activation_code_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid activation code"},
    )


def activation_code_expired_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={"detail": "Activation code expired"},
    )


def user_already_active_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User is already active"},
    )
