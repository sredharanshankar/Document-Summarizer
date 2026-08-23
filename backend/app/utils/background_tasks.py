"""Fire-and-forget background task scheduling.

`asyncio.create_task()` on its own is a trap: the event loop only holds a
*weak* reference to the task, so if nothing else references it, it can be
garbage-collected mid-execution (this is documented, surprising asyncio
behavior). `schedule_background_task` keeps a strong reference until the
task finishes, which is exactly what job processing here needs - the
request that started it has already returned a 202 and moved on.
"""

import asyncio
from collections.abc import Coroutine
from typing import Any

_running_tasks: set[asyncio.Task] = set()


def schedule_background_task(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _running_tasks.add(task)
    task.add_done_callback(_running_tasks.discard)
    return task
