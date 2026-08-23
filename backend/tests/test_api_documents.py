import time

from fastapi.testclient import TestClient


def _poll_until_terminal(client: TestClient, job_id: str, timeout_seconds: float = 15.0) -> dict:
    # Generous timeout: actual processing (fallback provider, tiny test
    # files) is near-instant. The real variable is how long a job waits
    # for a free slot in the shared background thread pool, which grows
    # with how many other tests are creating jobs around the same time -
    # a 5s timeout was tight enough to occasionally flake as the suite grew.
    deadline = time.monotonic() + timeout_seconds
    body = {}
    while time.monotonic() < deadline:
        response = client.get(f"/api/documents/status/{job_id}")
        body = response.json()
        if body["status"] in ("completed", "failed"):
            return body
        time.sleep(0.02)
    raise AssertionError(f"Job {job_id} did not reach a terminal state in time: {body}")


def test_analyze_accepts_valid_pdf_and_returns_job(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
        data={"summary_length": "medium"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "processing"
    assert body["job_id"]


def test_analyze_rejects_unsupported_type(client: TestClient) -> None:
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("notes.exe", b"hello", "application/octet-stream")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "unsupported_file_type"
    assert "message" in body
    assert "Traceback" not in response.text


def test_analyze_rejects_empty_file(client: TestClient) -> None:
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "empty_file"


def test_analyze_rejects_content_mismatched_with_extension(client: TestClient) -> None:
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("fake.pdf", b"not a pdf at all", "application/pdf")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "corrupted_file"


def test_status_returns_job_owned_by_the_correct_filename(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/documents/status/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["job_id"] == job_id
    assert body["status"] in ("processing", "completed")
    assert body["filename"] == "report.pdf"


def test_status_returns_404_for_unknown_job(client: TestClient) -> None:
    response = client.get("/api/documents/status/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_full_pipeline_completes_with_fallback_provider_when_no_api_key(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    # No AI_API_KEY is set in the test environment, so this exercises the
    # real end-to-end path through the no-API-key fallback summarizer.
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
        data={"summary_length": "short"},
    )
    job_id = create_response.json()["job_id"]

    body = _poll_until_terminal(client, job_id)

    assert body["status"] == "completed"
    result = body["result"]
    assert result["summary"]
    assert result["ai_provider"] == "fallback"
    assert result["metadata"]["filename"] == "report.pdf"
    assert result["metadata"]["word_count"] > 0
    assert result["metadata"]["used_ocr"] is False


def test_full_pipeline_completes_for_docx_upload(
    client: TestClient, sample_docx_bytes: bytes
) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "report.docx",
                sample_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    job_id = create_response.json()["job_id"]

    body = _poll_until_terminal(client, job_id)

    assert body["status"] == "completed"
    assert body["result"]["metadata"]["file_type"] == "docx"
    assert body["result"]["metadata"]["used_ocr"] is False
    assert body["result"]["summary"]


def test_full_pipeline_completes_for_txt_upload(
    client: TestClient, sample_txt_bytes: bytes
) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("notes.txt", sample_txt_bytes, "text/plain")},
    )
    job_id = create_response.json()["job_id"]

    body = _poll_until_terminal(client, job_id)

    assert body["status"] == "completed"
    assert body["result"]["metadata"]["file_type"] == "txt"
    assert body["result"]["metadata"]["used_ocr"] is False
    assert body["result"]["summary"]


def test_summarize_regenerates_summary_for_completed_job(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
        data={"summary_length": "short"},
    )
    job_id = create_response.json()["job_id"]
    _poll_until_terminal(client, job_id)

    response = client.post(
        "/api/documents/summarize",
        json={"job_id": job_id, "summary_length": "long"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary_length"] == "long"
    assert body["summary"]


def test_summarize_returns_404_for_unknown_job(client: TestClient) -> None:
    response = client.post(
        "/api/documents/summarize",
        json={"job_id": "does-not-exist", "summary_length": "short"},
    )
    assert response.status_code == 404


def test_ask_answers_a_question_about_a_completed_job(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
    )
    job_id = create_response.json()["job_id"]
    _poll_until_terminal(client, job_id)

    response = client.post(
        "/api/documents/ask",
        json={"job_id": job_id, "question": "What is this document used for?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["ai_provider"] == "fallback"


def test_ask_supports_a_sparse_followup_using_conversation_history(
    client: TestClient,
) -> None:
    import fitz

    doc = fitz.open()
    doc.new_page().insert_text(
        (72, 72),
        "Financing structures have evolved considerably this year, unlocking "
        "institutional capital that was previously unavailable to the sector.",
    )
    pdf_bytes = doc.tobytes()
    doc.close()

    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("financing.pdf", pdf_bytes, "application/pdf")},
    )
    job_id = create_response.json()["job_id"]
    _poll_until_terminal(client, job_id)

    first = client.post(
        "/api/documents/ask",
        json={"job_id": job_id, "question": "What is happening with financing?"},
    )
    assert first.status_code == 200
    first_answer = first.json()["answer"].lower()
    assert "financ" in first_answer or "capital" in first_answer

    # "What about that?" has no keywords of its own - only answerable by
    # using the previous question from job.qa_history for context.
    followup = client.post(
        "/api/documents/ask",
        json={"job_id": job_id, "question": "What about that?"},
    )
    assert followup.status_code == 200
    assert "doesn't seem to mention" not in followup.json()["answer"].lower()


def test_ask_rejects_a_blank_question(client: TestClient, sample_pdf_bytes: bytes) -> None:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
    )
    job_id = create_response.json()["job_id"]
    _poll_until_terminal(client, job_id)

    response = client.post(
        "/api/documents/ask",
        json={"job_id": job_id, "question": "   "},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"


def test_ask_returns_404_for_unknown_job(client: TestClient) -> None:
    response = client.post(
        "/api/documents/ask",
        json={"job_id": "does-not-exist", "question": "Anything?"},
    )
    assert response.status_code == 404


def test_ask_returns_422_when_job_has_not_finished_processing(client: TestClient) -> None:
    from app.services.job_store import job_store

    job = job_store.create(filename="in-progress.pdf")  # never completed

    response = client.post(
        "/api/documents/ask",
        json={"job_id": job.id, "question": "Anything?"},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "processing_error"


def _analyze_and_wait(client: TestClient, filename: str, pdf_bytes: bytes) -> str:
    create_response = client.post(
        "/api/documents/analyze",
        files={"file": (filename, pdf_bytes, "application/pdf")},
    )
    job_id = create_response.json()["job_id"]
    _poll_until_terminal(client, job_id)
    return job_id


def test_compare_returns_similarities_and_differences_for_two_completed_jobs(
    client: TestClient,
) -> None:
    import fitz

    doc_a = fitz.open()
    doc_a.new_page().insert_text(
        (72, 72),
        "Investment planning requires careful investment analysis. Renewable "
        "energy projects continue to expand across the investment portfolio.",
    )
    pdf_a = doc_a.tobytes()
    doc_a.close()

    doc_b = fitz.open()
    doc_b.new_page().insert_text(
        (72, 72),
        "Investment committee approved the office relocation budget. The "
        "relocation project team expects the move to complete by spring.",
    )
    pdf_b = doc_b.tobytes()
    doc_b.close()

    job_a = _analyze_and_wait(client, "finance.pdf", pdf_a)
    job_b = _analyze_and_wait(client, "relocation.pdf", pdf_b)

    response = client.post("/api/documents/compare", json={"job_ids": [job_a, job_b]})

    assert response.status_code == 200
    body = response.json()
    assert body["documents"] == ["finance.pdf", "relocation.pdf"]
    assert body["ai_provider"] == "fallback"
    assert body["comparison_summary"]
    assert len(body["similarities"]) > 0
    assert len(body["differences"]) > 0


def test_compare_rejects_fewer_than_two_documents(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    job_id = _analyze_and_wait(client, "report.pdf", sample_pdf_bytes)

    response = client.post("/api/documents/compare", json={"job_ids": [job_id]})

    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"


def test_compare_rejects_more_than_the_maximum_documents(client: TestClient) -> None:
    response = client.post(
        "/api/documents/compare",
        json={"job_ids": [f"job-{i}" for i in range(6)]},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"


def test_compare_returns_404_for_an_unknown_job(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    job_id = _analyze_and_wait(client, "report.pdf", sample_pdf_bytes)

    response = client.post(
        "/api/documents/compare",
        json={"job_ids": [job_id, "does-not-exist"]},
    )

    assert response.status_code == 404


def test_compare_returns_422_when_a_job_has_not_finished_processing(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    from app.services.job_store import job_store

    job_id = _analyze_and_wait(client, "report.pdf", sample_pdf_bytes)
    unfinished_job = job_store.create(filename="in-progress.pdf")

    response = client.post(
        "/api/documents/compare",
        json={"job_ids": [job_id, unfinished_job.id]},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "processing_error"


def test_compare_ask_answers_question_across_documents(
    client: TestClient, sample_pdf_bytes: bytes
) -> None:
    job_a = _analyze_and_wait(client, "doc_a.pdf", sample_pdf_bytes)
    job_b = _analyze_and_wait(client, "doc_b.pdf", sample_pdf_bytes)

    response = client.post(
        "/api/documents/compare/ask",
        json={"job_ids": [job_a, job_b], "question": "What is the main topic?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert body["ai_provider"] == "fallback"

