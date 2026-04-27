"""Judge flow: compare generated answer against reference answer + reference source text.

The judge is Grep-enabled so it can verify C-claims against the full
knowledge base, not just the retrieved subset. A claim that looks
"unsupported by retrieved" may actually be a correct KB statement whose
source section AI-1 happened not to select. Penalizing those is wrong —
they reflect a retrieval miss, not an answer defect.

The judge also uses verify_kb_evidence.py (in llm_tools/) via Bash to
self-correct SUPPORTED_BY_KB citations before emitting StructuredOutput.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import io
from .claude import invoke
from .types import JudgeResult, Scenario, SearchResult

_LLM_TOOLS_DIR = Path(__file__).resolve().parent.parent / "llm_tools"
_VERIFY_SCRIPT = _LLM_TOOLS_DIR / "verify_kb_evidence.py"


_FACT_ITEM = {
    "type": "object",
    "required": ["fact", "status"],
    "additionalProperties": False,
    "properties": {
        "fact": {"type": "string", "maxLength": 300},
        "status": {"enum": ["COVERED", "PARTIAL", "MISSING"]},
    },
}

_CLAIM_ITEM = {
    "type": "object",
    "required": ["claim"],
    "additionalProperties": False,
    "properties": {"claim": {"type": "string", "maxLength": 200}},
}

# Reason taxonomy:
#   UNSUPPORTED_KB_VERIFIED — judge searched the KB and could not find the claim
#   SUPPORTED_BY_KB         — claim is grounded in a KB section outside retrieved
#   OFF-TOPIC               — supported somewhere but misapplied to THIS question
#   CONTRADICTION           — contradicts an A-fact or the KB
# SUPPORTED_BY_KB does NOT penalize level (it's a retrieval miss, not an answer defect).
_C_REASONS = ["UNSUPPORTED_KB_VERIFIED", "SUPPORTED_BY_KB", "OFF-TOPIC", "CONTRADICTION"]

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
                    "claim": {"type": "string", "maxLength": 300},
                    "reason": {"enum": _C_REASONS},
                    "why": {"type": "string", "maxLength": 300},
                    "kb_evidence": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["file", "sid", "quote"],
                        "properties": {
                            "file": {"type": "string", "maxLength": 200},
                            "sid": {"type": "string", "maxLength": 20},
                            "quote": {"type": "string", "maxLength": 300},
                        },
                    },
                },
            },
        },
        "level": {"type": "integer", "enum": [0, 1, 2, 3]},
        "reasoning": {"type": "string", "maxLength": 600},
    },
}


def compute_level(verdict: dict) -> int:
    """Apply the new level rule given a raw verdict dict.

    Level 3: A all COVERED AND no penalizing C AND at least one B or SUPPORTED_BY_KB.
    Level 2: A all COVERED AND no penalizing C AND no supporting B/SUPPORTED_BY_KB.
    Level 1: A partial/missing OR any penalizing C (UNSUPPORTED_KB_VERIFIED / OFF-TOPIC / CONTRADICTION).
    Level 0: majority of A_facts MISSING.
    """
    a_facts = verdict.get("a_facts") or []
    if not a_facts:
        return 0
    covered = sum(1 for f in a_facts if f.get("status") == "COVERED")
    missing = sum(1 for f in a_facts if f.get("status") == "MISSING")
    if missing > len(a_facts) / 2:
        return 0
    all_covered = covered == len(a_facts)
    c_claims = verdict.get("c_claims") or []
    penalizing = sum(
        1 for c in c_claims
        if c.get("reason") in ("UNSUPPORTED_KB_VERIFIED", "OFF-TOPIC", "CONTRADICTION")
    )
    supported = sum(1 for c in c_claims if c.get("reason") == "SUPPORTED_BY_KB")
    b_claims = verdict.get("b_claims") or []
    if not all_covered or penalizing > 0:
        return 1
    if b_claims or supported:
        return 3
    return 2


def run(*, scenario: Scenario, search: SearchResult, model: str, scen_dir: Path,
        version: str = io.DEFAULT_VERSION) -> JudgeResult:
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

    ref_text, ref_records = io.load_reference_sources(
        scenario.reference_answer, version=version,
    )
    retrieved_text = io.load_retrieved_sections(search.cited, version=version)
    a_facts_text = "\n".join(f"- {f}" for f in scenario.a_facts)
    knowledge_root_abs = str(io.knowledge_root(version))
    knowledge_rel = f".claude/skills/nabledge-{version}/knowledge"
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
        .replace("{{knowledge_root}}", knowledge_rel)
        .replace("{{knowledge_root_abs}}", knowledge_root_abs)
        .replace("{{verify_script}}", str(_VERIFY_SCRIPT))
        .replace("{{python}}", sys.executable)
    )
    call = invoke(
        prompt=prompt,
        schema=SCHEMA_JUDGE,
        model=model,
        max_turns=15,
        log_path=scen_dir / "stream" / "judge.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=["Grep", "Bash"],
        timeout_s=420,
    )
    structured = call.structured or {}
    if isinstance(structured, dict):
        structured["level"] = compute_level(structured)
    return JudgeResult(
        verdict=io.verdict_from_structured(structured),
        ref_sources_loaded=sum(1 for r in ref_records if r.get("status") == "ok"),
        ref_sources_total=len(ref_records),
        cost_usd=call.cost_usd,
        duration_s=call.duration_s,
        error=call.error or None,
    )
