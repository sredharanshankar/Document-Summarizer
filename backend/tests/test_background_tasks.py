import asyncio
import gc

import pytest

from app.utils.background_tasks import schedule_background_task


@pytest.mark.asyncio
async def test_scheduled_task_runs_to_completion_even_without_a_kept_reference() -> None:
    result: dict[str, bool] = {"finished": False}

    async def work() -> None:
        await asyncio.sleep(0.05)
        result["finished"] = True

    schedule_background_task(work())  # deliberately not storing the returned Task
    gc.collect()  # force a collection pass that would reap an unreferenced task

    await asyncio.sleep(0.15)

    assert result["finished"] is True
