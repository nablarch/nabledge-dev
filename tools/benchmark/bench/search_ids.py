"""ids search variant: AI-1 picks file_id|sid from the LLM index, script resolves
to path:sid, read-sections fetches content, AI-3 composes the answer."""

from __future__ import annotations

import json
from pathlib import Path

from . import io
from .claude import invoke
from .types import SearchResult


SCHEMA_SELECT = {
    "type": "object",
    "required": ["selections"],
    "additionalProperties": False,
    "properties": {
        "selections": {
            "type": "array",
            "maxItems": 10,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9_-]+\|[a-zA-Z0-9_-]+$",
            },
        },
    },
}

SCHEMA_ANSWER = {
    "type": "object",
    "required": ["answer", "cited"],
    "additionalProperties": False,
    "properties": {
        "answer": {"type": "string", "maxLength": 4000},
        "cited": {
            "type": "array",
            "items": {"type": "string", "pattern": r"^[^:]+\.json:[a-zA-Z0-9_-]+$"},
        },
    },
}


def resolve_selections(
    raw: list[str], id_to_path: dict[str, dict]
) -> tuple[list[str], list[dict]]:
    """Map `file_id|sid` tokens to `path:sid` selectors using the script index.

    Drops malformed tokens, unknown file_ids, and unknown sids; records each
    rejection reason for audit.
    """
    resolved: list[str] = []
    unresolved: list[dict] = []
    for sel in raw:
        if "|" not in sel:
            unresolved.append({"selector": sel, "reason": "malformed"})
            continue
        fid, sid = sel.split("|", 1)
        info = id_to_path.get(fid)
        if not info:
            unresolved.append({"selector": sel, "reason": "unknown file_id"})
            continue
        if sid not in info.get("sections", []):
            unresolved.append({"selector": sel, "reason": "unknown sid"})
            continue
        resolved.append(f"{info['path']}:{sid}")
    return resolved, unresolved


def run(*, question: str, model: str, scen_dir: Path, id_to_path: dict[str, dict]) -> SearchResult:
    # AI-1 — select file_id|sid from the index.
    select_prompt = (
        (io.PROMPTS_DIR / "search_ids.md").read_text(encoding="utf-8")
        .replace("{{index}}", io.INDEX_LLM_PATH.read_text(encoding="utf-8"))
        .replace("{{question}}", question)
    )
    select = invoke(
        prompt=select_prompt,
        schema=SCHEMA_SELECT,
        model=model,
        max_turns=2,
        log_path=scen_dir / "stream" / "select.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=[],
        timeout_s=300,
    )
    raw_selections = list((select.structured or {}).get("selections") or [])
    resolved, unresolved = resolve_selections(raw_selections, id_to_path)

    # Load section content.
    sections_text, section_records = io.read_selected_sections(resolved)

    # AI-3 — compose the answer. If no sections were resolvable, return empty.
    if not sections_text:
        return SearchResult(
            variant="ids",
            answer="",
            cited=[],
            cost_usd=select.cost_usd,
            duration_s=select.duration_s,
            steps={
                "raw_selections": raw_selections,
                "resolved": resolved,
                "unresolved": unresolved,
                "sections_read": section_records,
            },
            error=select.error or "no sections resolved",
        )
    answer_prompt = (
        (io.PROMPTS_DIR / "answer.md").read_text(encoding="utf-8")
        .replace("{{question}}", question)
        .replace("{{sections_text}}", sections_text)
    )
    answer = invoke(
        prompt=answer_prompt,
        schema=SCHEMA_ANSWER,
        model=model,
        max_turns=2,
        log_path=scen_dir / "stream" / "answer.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=[],
        timeout_s=300,
    )
    ans = answer.structured or {}
    return SearchResult(
        variant="ids",
        answer=ans.get("answer") or "",
        cited=list(ans.get("cited") or []),
        cost_usd=select.cost_usd + answer.cost_usd,
        duration_s=select.duration_s + answer.duration_s,
        steps={
            "raw_selections": raw_selections,
            "resolved": resolved,
            "unresolved": unresolved,
            "sections_read": section_records,
            "select_cost_usd": select.cost_usd,
            "answer_cost_usd": answer.cost_usd,
        },
        error=answer.error or select.error or None,
    )


def load_id_to_path() -> dict[str, dict]:
    return json.loads(io.INDEX_SCRIPT_PATH.read_text(encoding="utf-8"))
