"""Judge flow: compare generated answer against reference answer + reference source text."""

from __future__ import annotations

from pathlib import Path

from . import io
from .claude import invoke
from .types import JudgeResult, Scenario, SearchResult


_FACT_ITEM = {
    "type": "object",
    "required": ["fact", "status"],
    "additionalProperties": False,
    "properties": {
        "fact": {"type": "string", "maxLength": 200},
        "status": {"enum": ["COVERED", "PARTIAL", "MISSING"]},
    },
}

_CLAIM_ITEM = {
    "type": "object",
    "required": ["claim"],
    "additionalProperties": False,
    "properties": {"claim": {"type": "string", "maxLength": 200}},
}

SCHEMA_JUDGE = {
    "type": "object",
    "required": ["a_facts", "b_claims", "c_claims", "level", "reasoning"],
    "additionalProperties": False,
    "properties": {
        "a_facts": {"type": "array", "minItems": 1, "maxItems": 15, "items": _FACT_ITEM},
        "b_claims": {"type": "array", "maxItems": 15, "items": _CLAIM_ITEM},
        "c_claims": {
            "type": "array",
            "maxItems": 10,
            "items": {
                "type": "object",
                "required": ["claim", "reason", "why"],
                "additionalProperties": False,
                "properties": {
                    "claim": {"type": "string", "maxLength": 200},
                    "reason": {"enum": ["UNSUPPORTED", "OFF-TOPIC", "CONTRADICTION"]},
                    "why": {"type": "string", "maxLength": 200},
                },
            },
        },
        "level": {"type": "integer", "enum": [0, 1, 2, 3]},
        "reasoning": {"type": "string", "maxLength": 600},
    },
}


def run(*, scenario: Scenario, search: SearchResult, model: str, scen_dir: Path) -> JudgeResult:
    if not search.answer:
        return JudgeResult(
            verdict=None,
            ref_sources_loaded=0,
            ref_sources_total=0,
            cost_usd=0.0,
            duration_s=0.0,
            error="no answer produced",
        )
    if not scenario.reference_answer:
        return JudgeResult(
            verdict=None,
            ref_sources_loaded=0,
            ref_sources_total=0,
            cost_usd=0.0,
            duration_s=0.0,
            error="reference answer missing",
        )
    if not scenario.a_facts:
        return JudgeResult(
            verdict=None,
            ref_sources_loaded=0,
            ref_sources_total=0,
            cost_usd=0.0,
            duration_s=0.0,
            error="a_facts missing in scenario",
        )

    ref_text, ref_records = io.load_reference_sources(scenario.reference_answer)
    retrieved_text = io.load_retrieved_sections(search.cited)
    a_facts_text = "\n".join(f"- {f}" for f in scenario.a_facts)
    prompt = (
        (io.PROMPTS_DIR / "judge.md").read_text(encoding="utf-8")
        .replace("{{question}}", scenario.question)
        .replace("{{a_facts}}", a_facts_text)
        .replace("{{reference_answer}}", scenario.reference_answer)
        .replace("{{reference_sources}}", ref_text or "(none)")
        .replace("{{retrieved_sections}}", retrieved_text or "(none)")
        .replace("{{generated_answer}}", search.answer)
        .replace(
            "{{generated_cited}}",
            "\n".join(f"- {c}" for c in search.cited) if search.cited else "(none)",
        )
    )
    call = invoke(
        prompt=prompt,
        schema=SCHEMA_JUDGE,
        model=model,
        max_turns=4,
        log_path=scen_dir / "stream" / "judge.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=[],
        timeout_s=300,
    )
    return JudgeResult(
        verdict=io.verdict_from_structured(call.structured),
        ref_sources_loaded=sum(1 for r in ref_records if r.get("status") == "ok"),
        ref_sources_total=len(ref_records),
        cost_usd=call.cost_usd,
        duration_s=call.duration_s,
        error=call.error or None,
    )
