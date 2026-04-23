"""Filesystem layout: scenarios, results dir, path resolution."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .types import JudgeResult, JudgeVerdict, Scenario, ScenarioRun, SearchResult, Variant


BENCH_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BENCH_DIR.parent.parent

SCENARIOS_PATH = BENCH_DIR / "scenarios" / "qa-v6.json"
ANSWERS_DIR = BENCH_DIR / "scenarios" / "qa-v6-answers"
PROMPTS_DIR = BENCH_DIR / "prompts"
RESULTS_DIR = BENCH_DIR / ".results"

KNOWLEDGE_ROOT = REPO_ROOT / ".claude" / "skills" / "nabledge-6" / "knowledge"
INDEX_LLM_PATH = KNOWLEDGE_ROOT / "index-llm.md"
INDEX_SCRIPT_PATH = KNOWLEDGE_ROOT / "index-script.json"


def load_scenarios(path: Path = SCENARIOS_PATH) -> list[Scenario]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: list[Scenario] = []
    for item in raw:
        sid = item["id"]
        answer_path = ANSWERS_DIR / f"{sid}.md"
        reference = answer_path.read_text(encoding="utf-8") if answer_path.exists() else ""
        out.append(Scenario(
            id=sid,
            question=item["expected_question"],
            expected_sections=list(item.get("expected_sections") or []),
            expected_keywords=list(item.get("expected_keywords") or []),
            review_perspective=item.get("review_perspective", ""),
            context=item.get("context", ""),
            reference_answer=reference,
        ))
    return out


def new_results_dir(variant: Variant, model: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    model_slug = model.replace("/", "_").replace(":", "_")
    out = RESULTS_DIR / f"{ts}-{variant}-{model_slug}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def scen_dir(results_dir: Path, scenario_id: str) -> Path:
    d = results_dir / scenario_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "stream").mkdir(exist_ok=True)
    return d


def write_search(scen: Path, search: SearchResult) -> None:
    (scen / "search.json").write_text(
        json.dumps(asdict(search), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (scen / "answer.md").write_text(search.answer or "", encoding="utf-8")


def read_search(scen: Path) -> SearchResult:
    data = json.loads((scen / "search.json").read_text(encoding="utf-8"))
    return SearchResult(
        variant=data["variant"],
        answer=data["answer"],
        cited=data.get("cited") or [],
        cost_usd=data.get("cost_usd") or 0.0,
        duration_s=data.get("duration_s") or 0.0,
        steps=data.get("steps") or {},
        error=data.get("error"),
    )


def write_judge(scen: Path, judge: JudgeResult) -> None:
    body: dict = {
        "verdict": asdict(judge.verdict) if judge.verdict else None,
        "ref_sources_loaded": judge.ref_sources_loaded,
        "ref_sources_total": judge.ref_sources_total,
        "cost_usd": judge.cost_usd,
        "duration_s": judge.duration_s,
        "error": judge.error,
    }
    (scen / "judge.json").write_text(
        json.dumps(body, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_selected_sections(selectors: list[str]) -> tuple[str, list[dict]]:
    """Load text for each `path:sid` selector from the knowledge base."""
    chunks: list[str] = []
    records: list[dict] = []
    for sel in selectors:
        if ":" not in sel:
            records.append({"selector": sel, "status": "malformed"})
            continue
        path, sid = sel.split(":", 1)
        kf = KNOWLEDGE_ROOT / path
        try:
            data = json.loads(kf.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            records.append({"selector": sel, "status": "file-missing"})
            continue
        text = (data.get("sections") or {}).get(sid)
        title = next(
            (s["title"] for s in data.get("index") or [] if s.get("id") == sid),
            None,
        )
        if text is None:
            records.append({"selector": sel, "status": "section-missing", "title": title})
            continue
        chunks.append(f"=== {sel} — {title or ''} ===\n{text}\n=== END ===")
        records.append({"selector": sel, "status": "ok", "title": title, "chars": len(text)})
    return "\n\n".join(chunks), records


CITATION_RE = re.compile(r"([a-zA-Z0-9_\-./]+\.json)[:#]([a-zA-Z0-9_\-]+)")


def extract_reference_citations(reference_md: str) -> list[tuple[str, str]]:
    """Extract `path:sid` or `path#sid` citations from a reference answer markdown."""
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for m in CITATION_RE.finditer(reference_md):
        key = (m.group(1), m.group(2))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def load_reference_sources(reference_md: str) -> tuple[str, list[dict]]:
    """Load bodies for each citation path:sid in the reference answer.

    Returns (formatted_text, per-citation records) analogous to
    read_selected_sections but driven by the reference answer's citations.
    """
    citations = extract_reference_citations(reference_md)
    chunks: list[str] = []
    records: list[dict] = []
    for path, sid in citations:
        kf = KNOWLEDGE_ROOT / path
        try:
            data = json.loads(kf.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            records.append({"path": path, "sid": sid, "status": "file-missing"})
            continue
        text = (data.get("sections") or {}).get(sid)
        title = next(
            (s["title"] for s in data.get("index") or [] if s.get("id") == sid),
            None,
        )
        if text is None:
            records.append({"path": path, "sid": sid, "status": "section-missing", "title": title})
            continue
        chunks.append(f"=== {path}:{sid} — {title or ''} ===\n{text}\n=== END ===")
        records.append({"path": path, "sid": sid, "status": "ok", "title": title, "chars": len(text)})
    return "\n\n".join(chunks), records


def verdict_from_structured(s: dict | None) -> JudgeVerdict | None:
    if s is None:
        return None
    return JudgeVerdict(
        level=int(s.get("level", 0)),
        required_facts=list(s.get("required_facts") or []),
        over_reach=list(s.get("over_reach") or []),
        reasoning=s.get("reasoning", ""),
    )
