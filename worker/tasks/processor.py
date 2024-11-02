import asyncio
import logging
from typing import Any

from server.common.queue import ProcessJobData
from server.common.task import handle_task_failure

logger = logging.getLogger(__name__)


async def process_article_job(ctx: dict, *args: Any, **kwargs: Any):
    try:
        data = ProcessJobData.model_validate(kwargs)
        print(f"processing article {data.article_id}")
        await asyncio.sleep(5)
        print(f"done processing article {data.article_id}")
    except:
        handle_task_failure(logger, ctx, 60)
