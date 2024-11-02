import logging
from os import environ
from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRoute

LOCAL_LOGGING_FORMAT = "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            path = str(request.url).replace(str(request.base_url), "/")
            try:
                response = await original_route_handler(request)
                logger.info(f"[{response.status_code} {request.method}] {path}")
                return response
            except HTTPException as exc:
                try:
                    body = await request.body()
                    body = body.decode("utf-8")
                    body = body.replace("\n", "").replace(" ", "")
                    logger.info(f"[{exc.status_code} {request.method}] [req: {body}] [res: {exc.detail}] {path}")
                except:
                    logger.exception("unable to log route")
                raise exc

        return custom_route_handler


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)d]%(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": environ.get("LOGLEVEL", "INFO"),
            "formatter": "json" if environ.get("ENVIRONMENT", "local") == "production" else "standard",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": environ.get("LOGLEVEL", "INFO"),
            "propagate": True,
        },
        "app": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "scrapy": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
