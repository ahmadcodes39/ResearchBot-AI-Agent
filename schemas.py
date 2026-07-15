from pydantic import BaseModel, Field
from typing import List


class ResearchAnswer(BaseModel):
    """Structured output format for the Research Assistant's final answer."""

    summary: str = Field(
        description="A 2-3 sentence high-level summary of the answer."
    )
    key_findings: List[str] = Field(
        description="A list of the main facts, points, or findings, each as a short bullet."
    )
    sources: List[str] = Field(
    description=(
        "The actual source names or URLs found in tool results, extracted from "
        "the search results (e.g. 'https://example.com/article' or 'BBC News'). "
        "Do NOT write the tool name itself (like 'web_search' or 'calculator'). "
        "If a calculation was performed, write 'Calculated internally' instead. "
        "If no tool was used, use an empty list."
    )
    )
    confidence: str = Field(
        description="One of: 'high', 'medium', 'low', based on how reliable and complete the information found was."
    )