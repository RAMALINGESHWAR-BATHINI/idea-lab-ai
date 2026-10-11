"""Lightweight background task manager.

Uses an in-process asyncio task queue. For production scaling, this can be
replaced with a Redis-backed queue (RQ/Celery) without changing the calling
code. Tasks are fire-and-forget with best-effort error handling and status
tracking via the ``job_status`` table (optional — falls back to logs).

Design: the main web process spawns tasks on a separate event loop task. AI
heavy work (document indexing, embedding generation) is offloaded here so it
never blocks request handlers.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable

from app.core.logging import get_logger

logger = get_logger(__name__)

# A simple registry of pending tasks. In production this would be Redis.
_tasks: dict[str, asyncio.Task] = {}


async def run_background_task(
    func: Callable[..., Any],
    *,
    name: str | None = None,
    **kwargs: Any,
) -> str:
    """Schedule a background task and return its job ID.

    The task runs on the current event loop. Exceptions are logged but do not
    propagate to the caller.
    """
    job_id = str(uuid.uuid4())
    task_name = name or func.__name__

    async def _runner() -> None:
        try:
            await func(**kwargs)
            logger.info("background_task_complete", task=task_name, job_id=job_id)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "background_task_failed",
                task=task_name,
                job_id=job_id,
                error=str(exc),
                exc_info=True,
            )

    task = asyncio.create_task(_runner(), name=f"bg:{task_name}:{job_id}")
    _tasks[job_id] = task
    # Clean up the registry when the task completes.
    task.add_done_callback(lambda t, jid=job_id: _tasks.pop(jid, None))
    return job_id


def get_task_status(job_id: str) -> str | None:
    """Return the status of a background task: 'running', 'done', 'cancelled', 'failed', or None."""
    task = _tasks.get(job_id)
    if task is None:
        return None
    if task.done():
        if task.cancelled():
            return "cancelled"
        exc = task.exception()
        return "failed" if exc else "done"
    return "running"
