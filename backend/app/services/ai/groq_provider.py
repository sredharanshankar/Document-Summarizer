import json
import logging

import groq
from pydantic import ValidationError

from app.models.schemas import SummaryLength
from app.services.ai.base import AIProvider, QAHistory, StructuredAnalysis, StructuredComparison
from app.services.ai.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    COMPARISON_SYSTEM_PROMPT,
    QA_SYSTEM_PROMPT,
    SUMMARY_ONLY_SYSTEM_PROMPT,
    build_analysis_user_prompt,
    build_comparison_user_prompt,
    build_qa_followup_prompt,
    build_qa_user_prompt,
    build_summary_user_prompt,
)
from app.services.ai.schema import AIAnalysisPayload, ComparisonPayload
from app.utils.errors import AIProviderError, AIRateLimitError, AITimeoutError

logger = logging.getLogger("document_summary_assistant")

# One retry for transient failures (timeout/rate limit) - enough to smooth
# over a brief blip without masking a genuinely broken configuration.
MAX_ATTEMPTS = 2


class GroqProvider(AIProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str, timeout_seconds: int) -> None:
        self._client = groq.Groq(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
        raw = self._complete(
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": build_analysis_user_prompt(text, summary_length)},
            ],
            json_mode=True,
        )
        payload = self._parse_analysis(raw)
        return StructuredAnalysis(
            summary=payload.summary,
            key_points=payload.key_points,
            main_ideas=payload.main_ideas,
            improvement_suggestions=payload.improvement_suggestions,
        )

    def generate_summary(self, text: str, summary_length: SummaryLength) -> str:
        raw = self._complete(
            messages=[
                {"role": "system", "content": SUMMARY_ONLY_SYSTEM_PROMPT},
                {"role": "user", "content": build_summary_user_prompt(text, summary_length)},
            ],
            json_mode=False,
        )
        return raw.strip()

    def answer_question(self, text: str, question: str, history: QAHistory | None = None) -> str:
        # The document is only sent once, in the first user turn - a
        # follow-up question ("what about the remote policy?") relies on
        # the model still having it in the conversation, not on resending
        # it every time (which would also multiply token usage per turn).
        messages: list[dict[str, str]] = [{"role": "system", "content": QA_SYSTEM_PROMPT}]
        if not history:
            messages.append({"role": "user", "content": build_qa_user_prompt(text, question)})
        else:
            first_question, first_answer = history[0]
            messages.append({"role": "user", "content": build_qa_user_prompt(text, first_question)})
            messages.append({"role": "assistant", "content": first_answer})
            for prior_question, prior_answer in history[1:]:
                messages.append({"role": "user", "content": build_qa_followup_prompt(prior_question)})
                messages.append({"role": "assistant", "content": prior_answer})
            messages.append({"role": "user", "content": build_qa_followup_prompt(question)})

        raw = self._complete(messages=messages, json_mode=False)
        return raw.strip()

    def compare_documents(self, documents: list[tuple[str, str]]) -> StructuredComparison:
        raw = self._complete(
            messages=[
                {"role": "system", "content": COMPARISON_SYSTEM_PROMPT},
                {"role": "user", "content": build_comparison_user_prompt(documents)},
            ],
            json_mode=True,
        )
        payload = self._parse_comparison(raw)
        return StructuredComparison(
            comparison_summary=payload.comparison_summary,
            similarities=payload.similarities,
            differences=payload.differences,
        )

    def _complete(self, *, messages: list[dict[str, str]], json_mode: bool) -> str:
        last_error: Exception | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                kwargs = {}
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=0.3,
                    **kwargs,
                )
                content = completion.choices[0].message.content
                if not content:
                    raise AIProviderError("The AI returned an empty response. Please try again.")
                return content
            except groq.APITimeoutError as exc:
                last_error = exc
                logger.warning("Groq request timed out (attempt %d/%d)", attempt, MAX_ATTEMPTS)
                continue
            except groq.RateLimitError as exc:
                raise AIRateLimitError(
                    "The AI service is receiving too many requests right now. Please try again shortly."
                ) from exc
            except groq.AuthenticationError as exc:
                logger.error("Groq authentication failed - check AI_API_KEY")
                raise AIProviderError(
                    "The AI service is not configured correctly on the server."
                ) from exc
            except groq.APIError as exc:
                logger.exception("Groq API error")
                raise AIProviderError(
                    "The AI service could not process this document right now. Please try again."
                ) from exc

        logger.error("Groq request timed out after %d attempts", MAX_ATTEMPTS)
        raise AITimeoutError(
            "The AI service took too long to respond. Please try again."
        ) from last_error

    def _parse_json(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("Groq returned non-JSON output: %s", raw[:500])
            raise AIProviderError(
                "The AI returned a response we couldn't understand. Please try again."
            ) from exc

    def _parse_analysis(self, raw: str) -> AIAnalysisPayload:
        data = self._parse_json(raw)
        try:
            return AIAnalysisPayload.model_validate(data)
        except ValidationError as exc:
            logger.error("Groq JSON failed schema validation: %s", exc)
            raise AIProviderError(
                "The AI returned an incomplete response. Please try again."
            ) from exc

    def _parse_comparison(self, raw: str) -> ComparisonPayload:
        data = self._parse_json(raw)
        try:
            return ComparisonPayload.model_validate(data)
        except ValidationError as exc:
            logger.error("Groq comparison JSON failed schema validation: %s", exc)
            raise AIProviderError(
                "The AI returned an incomplete comparison. Please try again."
            ) from exc
