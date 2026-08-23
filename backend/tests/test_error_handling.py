"""Tests for main.py's exception handlers - the cross-cutting guarantee that
every error response has the app's {"error", "message"} shape, regardless
of which layer raised it.
"""

from fastapi.testclient import TestClient


def test_malformed_request_body_returns_the_app_error_shape(client: TestClient) -> None:
    # Regression test: FastAPI's own default response for a request that
    # fails Pydantic validation is {"detail": [...]}, with no "message"
    # field. The frontend only knows how to read {"error", "message"} (see
    # api.ts's parseErrorResponse) - without a custom handler for this,
    # a malformed request silently degrades to a generic, unhelpful
    # "Something went wrong" message instead of a clear one.
    response = client.post(
        "/api/documents/compare",
        json={"job_ids": [None, "abc"]},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert isinstance(body["message"], str) and body["message"]
    assert "detail" not in body


def test_request_missing_a_required_field_returns_the_app_error_shape(
    client: TestClient,
) -> None:
    response = client.post("/api/documents/compare", json={"wrong_field": "oops"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert isinstance(body["message"], str) and body["message"]
