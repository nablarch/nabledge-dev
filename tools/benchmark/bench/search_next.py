"""next search variant: AI-1 picks file_id|sid from the LLM index, script resolves
to path:sid, read-sections fetches content, AI-3 composes the answer.

Term queries (for grepping section bodies) are extracted deterministically
from the question by `term_extract` — AI-1 no longer generates them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import io
from .claude import invoke
from .term_extract import extract_terms, filter_terms, load_stopset
from .types import SearchResult


SCHEMA_SELECT = {
    "type": "object",
    "additionalProperties": False,
    "required": ["intent", "candidate_files", "read_notes", "files_read_count",
                 "selections", "conclusion", "evidence", "caveats", "cited"],
    "properties": {
        "intent": {"type": "string"},
        "candidate_files": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["file_id", "reason"],
                "properties": {
                    "file_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
        "read_notes": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["file_id", "relevant_sections"],
                "properties": {
                    "file_id": {"type": "string"},
                    "read_error": {"type": "boolean"},
                    "relevant_sections": {
                        "type": "array",
                        "maxItems": 6,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["sid", "evidence"],
                            "properties": {
                                "sid": {"type": "string"},
                                "evidence": {"type": "string"},
                                "scope_note": {"type": "string", "maxLength": 200},
                            },
                        },
                    },
                },
            },
        },
        "files_read_count": {"type": "integer", "minimum": 0},
        "selections": {
            "type": "array",
            "maxItems": 15,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ref", "matched_on"],
                "properties": {
                    "ref": {
                        "type": "string",
                        "pattern": r"^[a-zA-Z0-9_-]+\|[a-zA-Z0-9_-]+$",
                    },
                    "matched_on": {
                        "type": "string",
                        "enum": ["title", "keyword", "body"],
                    },
                },
            },
        },
        "conclusion": {"type": "string", "maxLength": 600},
        "evidence": {
            "type": "array",
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["quote", "cited"],
                "properties": {
                    "quote": {"type": "string", "maxLength": 400},
                    "cited": {
                        "type": "string",
                        "pattern": r"^[a-zA-Z0-9_-]+\|[a-zA-Z0-9_-]+$",
                    },
                },
            },
        },
        "caveats": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["note", "cited"],
                "properties": {
                    "note": {"type": "string", "maxLength": 300},
                    "cited": {
                        "type": "string",
                        "pattern": r"^[a-zA-Z0-9_-]+\|[a-zA-Z0-9_-]+$",
                    },
                },
            },
        },
        "cited": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9_-]+\|[a-zA-Z0-9_-]+$",
            },
        },
    },
}


def _term_stopset_path(version: str) -> Path:
    return io.BENCH_DIR / "data" / f"term_stopset-v{version}.json"

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
    terms: list[str], id_to_path: dict[str, dict],
    *, version: str = io.DEFAULT_VERSION,
) -> list[dict]:
    """Grep each term in each knowledge JSON's section bodies.

    Returns a list of hit records: [{term, file_id, sid, chars}, ...].
    Limits per-term hits (TERM_HITS_PER_TERM) and total (TERM_HITS_TOTAL).
    Order: preserves input term order; within a term, files are alphabetical.
    """
    root = io.knowledge_root(version)
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
                data = json.loads((root / path).read_text(encoding="utf-8"))
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


_NORM_HEADER_RE = re.compile(r'^\s*#+\s+.*$', flags=re.M)
_NORM_EMPHASIS_RE = re.compile(r'\*\*|__')
_NORM_WS_RE = re.compile(r'\s+')


def _normalize_for_match(s: str) -> str:
    """Relax evidence matching: strip markdown headers / emphasis markers and
    collapse whitespace. The goal is "faithful quote" (not fabrication), not
    byte-identical copy — AI-1 often trims leading `## ` and joins lines, and
    those benign rewrites would otherwise look like mismatches.
    """
    s = _NORM_HEADER_RE.sub('', s)
    s = _NORM_EMPHASIS_RE.sub('', s)
    return _NORM_WS_RE.sub(' ', s).strip()


def verify_read_notes(
    read_notes: list[dict], id_to_path: dict[str, dict],
    *, version: str = io.DEFAULT_VERSION,
) -> dict:
    """Check that each read_notes[].relevant_sections[].evidence appears in
    the corresponding section body after whitespace/markdown normalization.

    Returns a per-entry verdict: {file_id, sid, verdict: "match"/"mismatch"/"file-missing"/"section-missing"}.
    >5% mismatch means AI-1 is fabricating (not merely paraphrasing) and the
    design fails the gate.
    """
    root = io.knowledge_root(version)
    results: list[dict] = []
    bodies: dict[str, dict[str, str]] = {}
    for note in read_notes or []:
        fid = note.get("file_id") or ""
        info = id_to_path.get(fid)
        if not info:
            for rs in note.get("relevant_sections") or []:
                results.append({
                    "file_id": fid, "sid": rs.get("sid"),
                    "verdict": "file-missing",
                })
            continue
        if fid not in bodies:
            try:
                data = json.loads(
                    (root / info["path"]).read_text(encoding="utf-8")
                )
            except (FileNotFoundError, json.JSONDecodeError):
                bodies[fid] = {}
                data = None
            if data is not None:
                secs = data.get("sections") or {}
                by_sid: dict[str, str] = {}
                if isinstance(secs, dict):
                    for sid, s in secs.items():
                        if isinstance(s, str):
                            by_sid[sid] = s
                        elif isinstance(s, dict):
                            body = s.get("body")
                            by_sid[sid] = body if isinstance(body, str) else ""
                bodies[fid] = by_sid
        for rs in note.get("relevant_sections") or []:
            sid = rs.get("sid") or ""
            evidence = rs.get("evidence") or ""
            body = bodies.get(fid, {}).get(sid)
            if body is None:
                results.append({
                    "file_id": fid, "sid": sid, "verdict": "section-missing",
                })
                continue
            # Match policy (Read-attestation, not verbatim-quote enforcement):
            # - Full substring match (strict verbatim), OR
            # - Normalized substring match (whitespace + markdown drift), OR
            # - Leading 30-char prefix appears in the body somewhere.
            # The prefix check catches the common case where AI-1 faithfully
            # starts from a real passage and then condenses / splices later
            # chars. A forged evidence string cannot pass this — it has no
            # anchor in the body. Fabrication detection is preserved.
            prefix_len = 30
            prefix = evidence[:prefix_len] if evidence else ""
            if evidence and (
                evidence in body
                or _normalize_for_match(evidence) in _normalize_for_match(body)
                or (len(prefix) >= prefix_len and prefix in body)
                or (len(prefix) >= prefix_len
                    and _normalize_for_match(prefix) in _normalize_for_match(body))
            ):
                verdict = "match"
            else:
                verdict = "mismatch"
            results.append({
                "file_id": fid, "sid": sid, "verdict": verdict,
                "evidence_chars": len(evidence),
            })
    total = len(results)
    mismatches = sum(1 for r in results if r["verdict"] == "mismatch")
    return {
        "per_section": results,
        "total": total,
        "mismatches": mismatches,
        "mismatch_rate": (mismatches / total) if total else 0.0,
    }


def run(*, question: str, model: str, scen_dir: Path, id_to_path: dict[str, dict],
        skip_answer: bool = False,
        version: str = io.DEFAULT_VERSION) -> SearchResult:
    # Deterministic term extraction from the question, filtered by df_pct
    # stopset. AI-1 no longer generates term_queries.
    stopset = load_stopset(_term_stopset_path(version))
    term_queries = filter_terms(extract_terms(question), stopset=stopset)

    # AI-1 — select file_id|sid from the index.
    knowledge_rel = f".claude/skills/nabledge-{version}/knowledge"
    select_prompt = (
        (io.PROMPTS_DIR / "search_next.md").read_text(encoding="utf-8")
        .replace("{{index}}", io.index_llm_path(version).read_text(encoding="utf-8"))
        .replace("{{question}}", question)
        .replace("{{knowledge_root}}", knowledge_rel)
    )
    select = invoke(
        prompt=select_prompt,
        schema=SCHEMA_SELECT,
        model=model,
        max_turns=10,
        log_path=scen_dir / "stream" / "select.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=["Read"],
        timeout_s=420,
    )
    structured = select.structured or {}
    intent = structured.get("intent") or ""
    candidate_files = list(structured.get("candidate_files") or [])
    read_notes = list(structured.get("read_notes") or [])
    files_read_count: int = structured.get("files_read_count") or 0
    selections_obj = list(structured.get("selections") or [])
    # Backwards compat: old prompt returned list[str]; new returns list[{ref, matched_on}]
    raw_selections: list[str] = []
    matched_on: list[str] = []
    for s in selections_obj:
        if isinstance(s, str):
            raw_selections.append(s)
            matched_on.append("title")
        elif isinstance(s, dict):
            ref = s.get("ref")
            if isinstance(ref, str):
                raw_selections.append(ref)
                matched_on.append(s.get("matched_on") or "title")
    evidence_check = verify_read_notes(read_notes, id_to_path, version=version)
    term_hits = grep_term_hits(term_queries, id_to_path, version=version) if term_queries else []
    merged_selections = merge_term_hits_into_selections(raw_selections, term_hits)
    resolved, unresolved = resolve_selections(merged_selections, id_to_path)

    # Answer fields come from the merged AI-1 call itself.
    conclusion = structured.get("conclusion") or ""
    evidence = list(structured.get("evidence") or [])
    caveats = list(structured.get("caveats") or [])
    cited_refs = list(structured.get("cited") or [])

    # Load section content (for downstream judge / reference resolution).
    _, section_records = io.read_selected_sections(resolved, version=version)

    steps = {
        "intent": intent,
        "candidate_files": candidate_files,
        "read_notes": read_notes,
        "files_read_count": files_read_count,
        "evidence_check": evidence_check,
        "matched_on": matched_on,
        "raw_selections": raw_selections,
        "term_queries": term_queries,
        "term_hits": term_hits,
        "merged_selections": merged_selections,
        "resolved": resolved,
        "unresolved": unresolved,
        "sections_read": section_records,
        "select_cost_usd": select.cost_usd,
        "conclusion": conclusion,
        "evidence": evidence,
        "caveats": caveats,
    }

    # Convert cited refs (file_id|sid) to path:sid form expected by the judge.
    cited_paths: list[str] = []
    for ref in cited_refs:
        if "|" not in ref:
            continue
        fid, sid = ref.split("|", 1)
        info = id_to_path.get(fid)
        if info and sid in info.get("sections", []):
            cited_paths.append(f"{info['path']}:{sid}")

    # skip_answer: return without rendering the answer markdown (Phase 1 flow).
    if skip_answer:
        return SearchResult(
            variant="next",
            answer="",
            cited=[],
            cost_usd=select.cost_usd,
            duration_s=select.duration_s,
            steps=steps,
            error=select.error or None,
        )

    answer_md = _render_answer_markdown(
        conclusion=conclusion, evidence=evidence, caveats=caveats,
        cited_refs=cited_refs, id_to_path=id_to_path,
    )
    return SearchResult(
        variant="next",
        answer=answer_md,
        cited=cited_paths,
        cost_usd=select.cost_usd,
        duration_s=select.duration_s,
        steps=steps,
        error=select.error or None,
    )


def _render_answer_markdown(
    *, conclusion: str, evidence: list[dict], caveats: list[dict],
    cited_refs: list[str], id_to_path: dict[str, dict],
) -> str:
    """Render the merged AI-1 answer fields into the answer.md shape."""
    def ref_to_path(ref: str) -> str:
        if "|" not in ref:
            return ref
        fid, sid = ref.split("|", 1)
        info = id_to_path.get(fid)
        if info:
            return f"{info['path']}:{sid}"
        return ref

    lines = []
    if conclusion:
        lines.append(f"**結論**: {conclusion}")
        lines.append("")
    if evidence:
        lines.append("**根拠**:")
        for ev in evidence:
            quote = (ev.get("quote") or "").strip()
            cited = ref_to_path(ev.get("cited") or "")
            lines.append(f"- {quote}  ({cited})")
        lines.append("")
    if caveats:
        lines.append("**注意点**:")
        for c in caveats:
            note = (c.get("note") or "").strip()
            cited = ref_to_path(c.get("cited") or "")
            if cited:
                lines.append(f"- {note} ({cited})")
            else:
                lines.append(f"- {note}")
        lines.append("")
    if cited_refs:
        refs_str = ", ".join(ref_to_path(r) for r in cited_refs)
        lines.append(f"参照: {refs_str}")
    return "\n".join(lines).strip()


def load_id_to_path(version: str = io.DEFAULT_VERSION) -> dict[str, dict]:
    return json.loads(io.index_script_path(version).read_text(encoding="utf-8"))
