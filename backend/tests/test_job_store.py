from app.services.job_store import MAX_QA_HISTORY, JobStore


def test_append_qa_exchange_accumulates_in_order() -> None:
    store = JobStore()
    job = store.create(filename="report.pdf")

    store.append_qa_exchange(job.id, "First question?", "First answer.")
    store.append_qa_exchange(job.id, "Second question?", "Second answer.")

    updated = store.get(job.id)
    assert updated is not None
    assert updated.qa_history == [
        ("First question?", "First answer."),
        ("Second question?", "Second answer."),
    ]


def test_qa_history_starts_empty() -> None:
    store = JobStore()
    job = store.create(filename="report.pdf")
    assert job.qa_history == []


def test_qa_history_is_capped_to_most_recent_exchanges() -> None:
    store = JobStore()
    job = store.create(filename="report.pdf")

    for i in range(MAX_QA_HISTORY + 3):
        store.append_qa_exchange(job.id, f"Question {i}?", f"Answer {i}.")

    updated = store.get(job.id)
    assert updated is not None
    assert len(updated.qa_history) == MAX_QA_HISTORY
    # Oldest exchanges are dropped first - the tail is what's kept.
    assert updated.qa_history[-1] == (
        f"Question {MAX_QA_HISTORY + 2}?",
        f"Answer {MAX_QA_HISTORY + 2}.",
    )
    assert updated.qa_history[0] == ("Question 3?", "Answer 3.")


def test_append_qa_exchange_on_unknown_job_does_not_raise() -> None:
    store = JobStore()
    store.append_qa_exchange("does-not-exist", "Q?", "A.")  # should be a no-op
