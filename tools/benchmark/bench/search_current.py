"""current search variant: single agent with Bash access to the production
skill's search scripts (full-text-search.sh / get-hints.sh / read-sections.sh)."""

from __future__ import annotations

from pathlib import Path

from . import io
from .claude import invoke
from .search_next import SCHEMA_ANSWER
from .types import SearchResult


def run(*, question: str, model: str, scen_dir: Path,
        version: str = io.DEFAULT_VERSION) -> SearchResult:
    skill_rel = f".claude/skills/nabledge-{version}"
    prompt = (
        (io.PROMPTS_DIR / "search_current.md").read_text(encoding="utf-8")
        .replace("{{question}}", question)
        .replace("{{skill_root}}", skill_rel)
    )
    result = invoke(
        prompt=prompt,
        schema=SCHEMA_ANSWER,
        model=model,
        max_turns=25,
        log_path=scen_dir / "stream" / "search.jsonl",
        cwd=io.REPO_ROOT,
        allowed_tools=["Bash"],
        timeout_s=900,
    )
    ans = result.structured or {}
    return SearchResult(
        variant="current",
        answer=ans.get("answer") or "",
        cited=list(ans.get("cited") or []),
        cost_usd=result.cost_usd,
        duration_s=result.duration_s,
        steps={"turns": result.turns},
        error=result.error or None,
    )
