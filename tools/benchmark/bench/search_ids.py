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
        "term_queries": {
            "type": "array",
            "maxItems": 3,
            "uniqueItems": True,
            "items": {"type": "string", "maxLength": 60},
        },
    },
}

# Per-term cap on how many sections we auto-include from a body substring match.
TERM_HITS_PER_TERM = 3
# Total cap on how many term-based selections we may add on top of selections.
TERM_HITS_TOTAL = 6
# Path prefixes whose bodies we do NOT grep for terms: sample code, migration,
# setup guides. These carry concrete code examples that AI-3 tends to quote
# verbatim and produce over-reach claims. The AI-1 selections still pick them
# up via title when they truly answer the question.
TERM_SEARCH_EXCLUDE_PREFIXES = (
    "guide/",
    "about/migration/",
    "setup/",
)

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


def grep_term_hits(
    terms: list[str], id_to_path: dict[str, dict]
) -> list[dict]:
    """Grep each term in each knowledge JSON's section bodies.

    Returns a list of hit records: [{term, file_id, sid, chars}, ...].
    Limits per-term hits (TERM_HITS_PER_TERM) and total (TERM_HITS_TOTAL).
    Order: preserves input term order; within a term, files are alphabetical.
    """
    hits: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for term in terms:
        if not term or len(hits) >= TERM_HITS_TOTAL:
            break
        per_term = 0
        for fid in sorted(id_to_path.keys()):
            if per_term >= TERM_HITS_PER_TERM or len(hits) >= TERM_HITS_TOTAL:
                break
            info = id_to_path[fid]
            path = info.get("path")
            if not path:
                continue
            if any(path.startswith(p) for p in TERM_SEARCH_EXCLUDE_PREFIXES):
                continue
            try:
                data = json.loads((io.KNOWLEDGE_ROOT / path).read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError):
                continue
            sections = data.get("sections") or {}
            if not isinstance(sections, dict):
                continue
            for sid, body in sections.items():
                if per_term >= TERM_HITS_PER_TERM or len(hits) >= TERM_HITS_TOTAL:
                    break
                if not isinstance(body, str):
                    continue
                if term in body:
                    key = (fid, sid)
                    if key in seen:
                        continue
                    seen.add(key)
                    hits.append({"term": term, "file_id": fid, "sid": sid, "chars": len(body)})
                    per_term += 1
    return hits


def merge_term_hits_into_selections(
    selections: list[str], hits: list[dict], cap: int = 16
) -> list[str]:
    """Append term hits as `file_id|sid` to selections, skipping duplicates.

    `cap` is a soft ceiling on the merged list; selections come first, then
    term hits fill remaining capacity.
    """
    merged = list(selections)
    present = set(merged)
    for h in hits:
        sel = f"{h['file_id']}|{h['sid']}"
        if sel in present:
            continue
        if len(merged) >= cap:
            break
        merged.append(sel)
        present.add(sel)
    return merged


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
    structured = select.structured or {}
    raw_selections = list(structured.get("selections") or [])
    term_queries = [t for t in (structured.get("term_queries") or []) if isinstance(t, str) and t.strip()]
    term_hits = grep_term_hits(term_queries, id_to_path) if term_queries else []
    merged_selections = merge_term_hits_into_selections(raw_selections, term_hits)
    resolved, unresolved = resolve_selections(merged_selections, id_to_path)

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
                "term_queries": term_queries,
                "term_hits": term_hits,
                "merged_selections": merged_selections,
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
            "term_queries": term_queries,
            "term_hits": term_hits,
            "merged_selections": merged_selections,
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
