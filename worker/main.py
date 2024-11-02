import asyncio
import logging
import logging.config
from json import JSONEncoder

import coloredlogs
from arq.cli import watch_reload
from arq.connections import RedisSettings
from arq.typing import WorkerSettingsBase

from server.common.database import session_manager
from server.common.json import TypeAwareEncoder
from server.common.logging import LOCAL_LOGGING_FORMAT, LOGGING_CONFIG
from server.common.redis import close_redis
from server.config import settings
from worker.tasks.processor import process_article_job

logging.config.dictConfig(LOGGING_CONFIG)
if settings.is_local():
    coloredlogs.install(fmt=LOCAL_LOGGING_FORMAT)

JSONEncoder._old_default = JSONEncoder.default  # type: ignore
JSONEncoder.default = TypeAwareEncoder.default  # type: ignore


async def startup(ctx):
    pass


async def shutdown(ctx):
    await close_redis()


_redis_settings = RedisSettings.from_dsn(settings.datastores.redis_url)
_redis_settings.conn_timeout = 3
_redis_settings.conn_retry_delay = 2
session_manager.init(settings.datastores.sqlalchemy_database_url)


class WorkerSettings(WorkerSettingsBase):
    functions = [
        process_article_job,
    ]
    cron_jobs = []
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = _redis_settings
    retry_jobs = True
    max_tries = settings.task.job_max_tries
    timeout_seconds = 300


def main():
    asyncio.new_event_loop().run_until_complete(watch_reload("worker", WorkerSettings))


if __name__ == "__main__":
    main()
