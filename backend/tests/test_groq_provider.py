import httpx
import pytest
from groq import APIError, APITimeoutError, AuthenticationError, RateLimitError

from app.models.schemas import SummaryLength
from app.services.ai.groq_provider import GroqProvider
from app.utils.errors import AIProviderError, AIRateLimitError, AITimeoutError


def _request() -> httpx.Request:
    return httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


class FakeCompletions:
    def __init__(self, responder) -> None:
        self._responder = responder
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responder(kwargs)


def _install_fake_completions(provider: GroqProvider, responder) -> FakeCompletions:
    fake = FakeCompletions(responder)
    provider._client.chat.completions = fake
    return fake


def _make_provider() -> GroqProvider:
    return GroqProvider(api_key="test-key", model="test-model", timeout_seconds=5)


def _content_response(content: str):
    class Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class Choice:
        def __init__(self, content: str) -> None:
            self.message = Message(content)

    class Completion:
        def __init__(self, content: str) -> None:
            self.choices = [Choice(content)]

    return Completion(content)


def test_generate_analysis_parses_valid_json() -> None:
    provider = _make_provider()
    valid_json = (
        '{"summary": "A summary.", "key_points": ["a", "b"], '
        '"main_ideas": ["idea"], "improvement_suggestions": []}'
    )
    fake = _install_fake_completions(provider, lambda kwargs: _content_response(valid_json))

    result = provider.generate_analysis("some document text", SummaryLength.MEDIUM)

    assert result.summary == "A summary."
    assert result.key_points == ["a", "b"]
    assert result.main_ideas == ["idea"]
    assert result.improvement_suggestions == []
    assert fake.calls[0]["response_format"] == {"type": "json_object"}


def test_generate_analysis_raises_on_malformed_json() -> None:
    provider = _make_provider()
    _install_fake_completions(provider, lambda kwargs: _content_response("not json at all"))

    with pytest.raises(AIProviderError):
        provider.generate_analysis("some text", SummaryLength.SHORT)


def test_generate_analysis_raises_on_schema_mismatch() -> None:
    provider = _make_provider()
    # Valid JSON, but missing the required "summary" field.
    _install_fake_completions(
        provider, lambda kwargs: _content_response('{"key_points": ["a"]}')
    )

    with pytest.raises(AIProviderError):
        provider.generate_analysis("some text", SummaryLength.SHORT)


def test_rate_limit_error_maps_to_ai_rate_limit_error() -> None:
    provider = _make_provider()
    request = _request()
    response = httpx.Response(429, request=request)

    def raise_rate_limit(kwargs):
        raise RateLimitError("rate limited", response=response, body=None)

    _install_fake_completions(provider, raise_rate_limit)

    with pytest.raises(AIRateLimitError):
        provider.generate_analysis("text", SummaryLength.SHORT)


def test_authentication_error_maps_to_ai_provider_error() -> None:
    provider = _make_provider()
    request = _request()
    response = httpx.Response(401, request=request)

    def raise_auth_error(kwargs):
        raise AuthenticationError("bad key", response=response, body=None)

    _install_fake_completions(provider, raise_auth_error)

    with pytest.raises(AIProviderError):
        provider.generate_analysis("text", SummaryLength.SHORT)


def test_repeated_timeout_maps_to_ai_timeout_error() -> None:
    provider = _make_provider()

    def raise_timeout(kwargs):
        raise APITimeoutError(request=_request())

    _install_fake_completions(provider, raise_timeout)

    with pytest.raises(AITimeoutError):
        provider.generate_analysis("text", SummaryLength.SHORT)


def test_generic_api_error_maps_to_ai_provider_error() -> None:
    provider = _make_provider()

    def raise_generic(kwargs):
        raise APIError("boom", request=_request(), body=None)

    _install_fake_completions(provider, raise_generic)

    with pytest.raises(AIProviderError):
        provider.generate_analysis("text", SummaryLength.SHORT)


def test_generate_summary_returns_plain_text_without_json_mode() -> None:
    provider = _make_provider()
    fake = _install_fake_completions(
        provider, lambda kwargs: _content_response("  Plain summary text.  ")
    )

    result = provider.generate_summary("some document text", SummaryLength.LONG)

    assert result == "Plain summary text."
    assert "response_format" not in fake.calls[0]


def test_answer_question_returns_plain_text_without_json_mode() -> None:
    provider = _make_provider()
    fake = _install_fake_completions(
        provider, lambda kwargs: _content_response("  The answer is 42.  ")
    )

    result = provider.answer_question("some document text", "What is the answer?")

    assert result == "The answer is 42."
    assert "response_format" not in fake.calls[0]
    assert "What is the answer?" in fake.calls[0]["messages"][1]["content"]
    assert "some document text" in fake.calls[0]["messages"][1]["content"]


def test_answer_question_raises_on_timeout() -> None:
    provider = _make_provider()

    def raise_timeout(kwargs):
        raise APITimeoutError(request=_request())

    _install_fake_completions(provider, raise_timeout)

    with pytest.raises(AITimeoutError):
        provider.answer_question("text", "a question")


def test_answer_question_without_history_sends_a_single_turn() -> None:
    provider = _make_provider()
    fake = _install_fake_completions(provider, lambda kwargs: _content_response("An answer."))

    provider.answer_question("some document text", "First question?")

    messages = fake.calls[0]["messages"]
    assert len(messages) == 2  # system + the one user turn
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "some document text" in messages[1]["content"]
    assert "First question?" in messages[1]["content"]


def test_answer_question_with_history_builds_a_multi_turn_conversation() -> None:
    provider = _make_provider()
    fake = _install_fake_completions(provider, lambda kwargs: _content_response("Second answer."))

    history = [("First question?", "First answer.")]
    provider.answer_question("some document text", "Second question?", history)

    messages = fake.calls[0]["messages"]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    # The document is only sent once, in the first user turn.
    assert "some document text" in messages[1]["content"]
    assert "First question?" in messages[1]["content"]
    assert messages[2]["content"] == "First answer."
    assert "Second question?" in messages[3]["content"]
    assert "some document text" not in messages[3]["content"]


def test_answer_question_with_two_prior_exchanges_keeps_them_all() -> None:
    provider = _make_provider()
    fake = _install_fake_completions(provider, lambda kwargs: _content_response("Third answer."))

    history = [
        ("First question?", "First answer."),
        ("Second question?", "Second answer."),
    ]
    provider.answer_question("some document text", "Third question?", history)

    messages = fake.calls[0]["messages"]
    assert [m["role"] for m in messages] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert messages[2]["content"] == "First answer."
    assert "Second question?" in messages[3]["content"]
    assert messages[4]["content"] == "Second answer."
    assert "Third question?" in messages[5]["content"]


def test_compare_documents_parses_valid_json() -> None:
    provider = _make_provider()
    valid_json = (
        '{"comparison_summary": "They differ on scope.", '
        '"similarities": ["Both discuss budgets."], '
        '"differences": ["\\"a.pdf\\" covers Q1.", "\\"b.pdf\\" covers Q2."]}'
    )
    fake = _install_fake_completions(provider, lambda kwargs: _content_response(valid_json))

    result = provider.compare_documents([("a.pdf", "text a"), ("b.pdf", "text b")])

    assert result.comparison_summary == "They differ on scope."
    assert result.similarities == ["Both discuss budgets."]
    assert len(result.differences) == 2
    assert fake.calls[0]["response_format"] == {"type": "json_object"}
    assert 'name="a.pdf"' in fake.calls[0]["messages"][1]["content"]
    assert 'name="b.pdf"' in fake.calls[0]["messages"][1]["content"]


def test_compare_documents_raises_on_malformed_json() -> None:
    provider = _make_provider()
    _install_fake_completions(provider, lambda kwargs: _content_response("not json"))

    with pytest.raises(AIProviderError):
        provider.compare_documents([("a.pdf", "text a"), ("b.pdf", "text b")])


def test_compare_documents_raises_on_schema_mismatch() -> None:
    provider = _make_provider()
    # Valid JSON, but missing the required "comparison_summary" field.
    _install_fake_completions(provider, lambda kwargs: _content_response('{"similarities": []}'))

    with pytest.raises(AIProviderError):
        provider.compare_documents([("a.pdf", "text a"), ("b.pdf", "text b")])
