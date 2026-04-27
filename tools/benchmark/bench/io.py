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

PROMPTS_DIR = BENCH_DIR / "prompts"
RESULTS_DIR = BENCH_DIR / ".results"

# Default version — all accessors honor the `version` kwarg so other versions
# (v5 / v1.2 / v1.3 / v1.4) can run through the same benchmark code paths.
DEFAULT_VERSION = "6"


def knowledge_root(version: str = DEFAULT_VERSION) -> Path:
    # Honor monkeypatches on the module-level KNOWLEDGE_ROOT for the default
    # version — existing tests set KNOWLEDGE_ROOT to a fake tree and expect
    # all downstream code to pick it up.
    if version == DEFAULT_VERSION:
        mod_default = globals().get("KNOWLEDGE_ROOT")
        if mod_default is not None:
            return mod_default
    return REPO_ROOT / ".claude" / "skills" / f"nabledge-{version}" / "knowledge"


def index_llm_path(version: str = DEFAULT_VERSION) -> Path:
    return knowledge_root(version) / "index-llm.md"


def index_script_path(version: str = DEFAULT_VERSION) -> Path:
    return knowledge_root(version) / "index-script.json"


def scenarios_path(version: str = DEFAULT_VERSION) -> Path:
    return BENCH_DIR / "scenarios" / f"qa-v{version}.json"


def answers_dir(version: str = DEFAULT_VERSION) -> Path:
    return BENCH_DIR / "scenarios" / f"qa-v{version}-answers"


# Legacy module-level constants (default to v6). Prefer the helpers above for
# new code. Existing tests and tools still reference these names.
SCENARIOS_PATH = scenarios_path()
ANSWERS_DIR = answers_dir()
KNOWLEDGE_ROOT = knowledge_root()
INDEX_LLM_PATH = index_llm_path()
INDEX_SCRIPT_PATH = index_script_path()


def load_scenarios(
    path: Path | None = None, *, version: str = DEFAULT_VERSION,
) -> list[Scenario]:
    path = path or scenarios_path(version)
    answers = answers_dir(version)
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: list[Scenario] = []
    for item in raw:
        sid = item["id"]
        answer_path = answers / f"{sid}.md"
        reference = answer_path.read_text(encoding="utf-8") if answer_path.exists() else ""
        out.append(Scenario(
            id=sid,
            question=item["expected_question"],
            expected_sections=list(item.get("expected_sections") or []),
            expected_keywords=list(item.get("expected_keywords") or []),
            review_perspective=item.get("review_perspective", ""),
            context=item.get("context", ""),
            reference_answer=reference,
            a_facts=list(item.get("a_facts") or []),
        ))
    return out


def new_results_dir(
    variant: Variant, model: str, *, version: str = DEFAULT_VERSION,
) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    model_slug = model.replace("/", "_").replace(":", "_")
    out = RESULTS_DIR / f"{ts}-v{version}-{variant}-{model_slug}"
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


def load_retrieved_sections(
    selectors: list[str], *, version: str = DEFAULT_VERSION,
) -> str:
    """Load text for selectors (path:sid or path#sid) as a single block.

    Used to give the judge the KB evidence the AI actually cited, so it
    can tell "faithful quote of a non-reference section" apart from
    "fabrication".
    """
    normalized = [s.replace("#", ":", 1) for s in selectors if s]
    text, _ = read_selected_sections(normalized, version=version)
    return text


def read_selected_sections(
    selectors: list[str], *, version: str = DEFAULT_VERSION,
) -> tuple[str, list[dict]]:
    """Load text for each `path:sid` selector from the knowledge base."""
    root = knowledge_root(version)
    chunks: list[str] = []
    records: list[dict] = []
    for sel in selectors:
        if ":" not in sel:
            records.append({"selector": sel, "status": "malformed"})
            continue
        path, sid = sel.split(":", 1)
        kf = root / path
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


def load_reference_sources(
    reference_md: str, *, version: str = DEFAULT_VERSION,
) -> tuple[str, list[dict]]:
    """Load bodies for each citation path:sid in the reference answer.

    Returns (formatted_text, per-citation records) analogous to
    read_selected_sections but driven by the reference answer's citations.
    """
    root = knowledge_root(version)
    citations = extract_reference_citations(reference_md)
    chunks: list[str] = []
    records: list[dict] = []
    for path, sid in citations:
        kf = root / path
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
    def _facts(v):
        return v if isinstance(v, list) else []
    return JudgeVerdict(
        level=int(s.get("level", 0)),
        a_facts=_facts(s.get("a_facts")),
        b_claims=_facts(s.get("b_claims") or s.get("b_facts")),
        c_claims=_facts(s.get("c_claims")),
        reasoning=s.get("reasoning", "") if isinstance(s.get("reasoning"), str) else "",
    )
