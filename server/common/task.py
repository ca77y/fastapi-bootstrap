from arq import Retry

from server.config import settings


def handle_task_failure(logger, ctx, defer_base_seconds):
    attempts_count = ctx.get("job_try", settings.task.job_max_tries)
    if attempts_count is not None and attempts_count >= settings.task.job_max_tries:
        logger.exception("Task failed to finish and there will be no more retries!")
    elif not settings.is_local():
        logger.exception("Task failed to finish and will be retried")
        raise Retry(defer=attempts_count * defer_base_seconds)
    else:
        logger.exception("Task failed to finish and will NOT be retried")
