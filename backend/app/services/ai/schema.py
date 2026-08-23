from pydantic import BaseModel, Field


class AIAnalysisPayload(BaseModel):
    """Validates the JSON an LLM returns before it's trusted anywhere else.

    Malformed or missing fields raise a pydantic ValidationError, which
    GroqProvider turns into a clean AIProviderError rather than letting bad
    AI output reach the frontend.
    """

    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    main_ideas: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class ComparisonPayload(BaseModel):
    """Validates the JSON an LLM returns for a document comparison."""

    comparison_summary: str = Field(min_length=1)
    similarities: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
