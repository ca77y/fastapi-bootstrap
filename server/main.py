import logging.config
from json import JSONEncoder

import coloredlogs
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_pagination import set_page

from server.articles.routes import router as articles_router
from server.common.database import session_manager
from server.common.http import PageDataResponse
from server.common.json import TypeAwareEncoder
from server.common.logging import LOCAL_LOGGING_FORMAT, LOGGING_CONFIG, LoggingRoute
from server.config import settings
from server.profiles.routes import router as profiles_router

logging.config.dictConfig(LOGGING_CONFIG)
if settings.is_local():
    coloredlogs.install(fmt=LOCAL_LOGGING_FORMAT)

JSONEncoder._old_default = JSONEncoder.default  # type: ignore
JSONEncoder.default = TypeAwareEncoder.default  # type: ignore

app = FastAPI(default_response_class=ORJSONResponse)

root = APIRouter(prefix="/api/v1", route_class=LoggingRoute)
session_manager.init(settings.datastores.sqlalchemy_database_url)


@root.get("/healthcheck")
def health_check():
    return {"status": "ok"}


root.include_router(articles_router, prefix="/articles", tags=["articles"])
root.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(root)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_page(PageDataResponse)


def main():
    uvicorn.run("server.main:app", host="0.0.0.0", port=3000, reload=True, log_config=None)


if __name__ == "__main__":
    main()
