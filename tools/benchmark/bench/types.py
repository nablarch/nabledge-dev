"""Benchmark domain types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Variant = Literal["next", "current"]


@dataclass(frozen=True)
class Scenario:
    id: str
    question: str
    expected_sections: list[str]  # "path:sid"
    expected_keywords: list[str]
    review_perspective: str
    context: str
    reference_answer: str  # markdown body of qa-v6-answers/{id}.md
    a_facts: list[str] = field(default_factory=list)  # pre-authored required facts


@dataclass(frozen=True)
class ClaudeInvocation:
    """Raw result of one claude-cli call."""

    structured: dict | None
    cost_usd: float
    duration_s: float
    turns: int | None
    error: str


@dataclass
class SearchResult:
    """Output of a search flow (next or current)."""

    variant: Variant
    answer: str
    cited: list[str]  # "path:sid"
    cost_usd: float
    duration_s: float
    steps: dict = field(default_factory=dict)  # per-variant diagnostics
    error: str | None = None


@dataclass(frozen=True)
class JudgeVerdict:
    level: int  # 0-3
    a_facts: list[dict]  # [{fact, status}]
    b_claims: list[dict]  # [{claim}]
    c_claims: list[dict]  # [{claim, reason, why}]
    reasoning: str


@dataclass
class JudgeResult:
    verdict: JudgeVerdict | None
    ref_sources_loaded: int
    ref_sources_total: int
    cost_usd: float
    duration_s: float
    error: str | None = None


@dataclass
class ScenarioRun:
    scenario_id: str
    search: SearchResult
    judge: JudgeResult
