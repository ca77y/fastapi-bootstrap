import logging
from http.client import (
    BAD_REQUEST,
    INTERNAL_SERVER_ERROR,
    NOT_FOUND,
    PAYMENT_REQUIRED,
    SERVICE_UNAVAILABLE,
    TOO_MANY_REQUESTS,
    UNAUTHORIZED,
)

import sqlalchemy.exc
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=BAD_REQUEST, detail=message)


def unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=UNAUTHORIZED, detail=message)


def payment_required(message: str) -> HTTPException:
    return HTTPException(status_code=PAYMENT_REQUIRED, detail=message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=NOT_FOUND, detail=message)


def too_many_requests(message: str) -> HTTPException:
    return HTTPException(status_code=TOO_MANY_REQUESTS, detail=message)


def server_error(message: str) -> HTTPException:
    return HTTPException(status_code=INTERNAL_SERVER_ERROR, detail=message)


def server_not_available(message: str) -> HTTPException:
    return HTTPException(status_code=SERVICE_UNAVAILABLE, detail=message)


class InvalidLoginCodeError(Exception):
    def __init__(self, *args: object, session: str) -> None:
        super().__init__(*args)
        self.session = session


class RefreshTokenError(Exception):
    pass


async def register_handlers(app: FastAPI):
    @app.exception_handler(sqlalchemy.exc.IntegrityError)
    async def integrity_error_handler(_: Request, exc: sqlalchemy.exc.IntegrityError):
        logger.error("duplicate key found", exc)
        return JSONResponse(
            status_code=400,
            content={"detail": "duplicate value already in the database"},
        )

    @app.exception_handler(InvalidLoginCodeError)
    async def invalid_login_code_handler(_: Request, exc: InvalidLoginCodeError):
        return JSONResponse(
            status_code=401, content={"detail": "Login code was invalid"}, headers={"X-Session": exc.session}
        )
