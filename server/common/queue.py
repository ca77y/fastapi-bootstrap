from enum import StrEnum
from typing import Union
from uuid import UUID

from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job
from pydantic import BaseModel

from server.config import settings


class JobName(StrEnum):
    process_article_job = "process_article_job"


class ProcessJobData(BaseModel):
    article_id: UUID


class EmptyJobData(BaseModel):
    pass


JobData = Union[EmptyJobData, ProcessJobData]


async def enqueue(job_name: JobName, job_data: JobData) -> Job | None:
    pool = await create_pool(RedisSettings.from_dsn(settings.datastores.redis_url))
    res = await pool.enqueue_job(job_name, **job_data.model_dump(exclude_none=True))
    return res
