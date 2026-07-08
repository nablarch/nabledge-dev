#!/usr/bin/env python3
"""Generate DeepEval review MD files from benchmark results.

Generates .work/00393/checks/{run}-{scenario}.md for each run × scenario (102 files).
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tools/benchmark/results/20260616-1214-fullbench-classes-v6"
KNOWLEDGE_DIR = REPO_ROOT / ".claude/skills/nabledge-6/knowledge"
OUTPUT_DIR = REPO_ROOT / ".work/00393/checks"
GITHUB_BASE = "https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs"

THRESHOLDS = {
    "answer_correctness": 0.99,
    "answer_relevancy": 0.95,
    "faithfulness": 0.99,
}
METRIC_ORDER = ["answer_correctness", "answer_relevancy", "faithfulness"]


def make_anchor(title: str) -> str:
    """Convert section title to GitHub Markdown anchor."""
    anchor = title.lower()
    anchor = anchor.replace(" ", "-")
    # Remove characters that GitHub strips from anchors
    anchor = re.sub(r"[^\w\-]", "", anchor)
    anchor = re.sub(r"-+", "-", anchor)
    anchor = anchor.strip("-")
    return anchor


def resolve_section(section_ref: str) -> tuple[str, str]:
    """Resolve a search_section ref like 'component/libraries/foo.json:s9'.

    Returns (title, github_link) or (section_ref, "") on failure.
    """
    try:
        json_path_part, section_id = section_ref.rsplit(":", 1)
        # json_path_part: e.g. "component/libraries/libraries-database.json"
        base = json_path_part.replace(".json", "")
        json_file = KNOWLEDGE_DIR / json_path_part

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        sections = data.get("sections", [])
        title = None
        for sec in sections:
            if sec.get("id") == section_id:
                title = sec.get("title", "")
                break

        if title is None:
            return section_ref, ""

        anchor = make_anchor(title)
        github_link = f"{GITHUB_BASE}/{base}.md#{anchor}"
        return title, github_link
    except Exception:
        return section_ref, ""


def ok_ng(metric: str, score: float) -> str:
    threshold = THRESHOLDS.get(metric, 1.0)
    return "OK" if score >= threshold else "NG"


def generate_md(run: str, scenario: str) -> str:
    scenario_dir = RESULTS_DIR / run / scenario
    eval_file = scenario_dir / "evaluation.json"
    answer_file = scenario_dir / "answer.md"

    with open(eval_file, encoding="utf-8") as f:
        evaluation = json.load(f)

    answer_text = ""
    if answer_file.exists():
        with open(answer_file, encoding="utf-8") as f:
            answer_text = f.read()

    scenario_id = evaluation.get("scenario_id", scenario)
    input_text = evaluation.get("input", "")
    scores = evaluation.get("scores", {})
    expected_facts = evaluation.get("expected_facts", [])
    diagnostics = evaluation.get("diagnostics", {})
    search_sections = diagnostics.get("search_sections", [])

    # Build 参照ナレッジ section
    knowledge_lines = []
    for sec_ref in search_sections:
        title, link = resolve_section(sec_ref)
        section_id = sec_ref.rsplit(":", 1)[-1] if ":" in sec_ref else sec_ref
        if link:
            knowledge_lines.append(f"- [{title}]({link}) ({section_id})")
        else:
            knowledge_lines.append(f"- {sec_ref}")
    knowledge_section = "\n".join(knowledge_lines) if knowledge_lines else "（なし）"

    # Build DeepEval判定 table
    table_rows = []
    for metric in METRIC_ORDER:
        metric_data = scores.get(metric, {})
        score = metric_data.get("score", "")
        reason = metric_data.get("reason", "")
        threshold = THRESHOLDS.get(metric, 1.0)
        if isinstance(score, float):
            verdict = ok_ng(metric, score)
            score_str = f"{score:.2f}" if score != int(score) else f"{score:.1f}"
        else:
            verdict = "—"
            score_str = str(score)
        # Escape pipe in reason
        reason_escaped = reason.replace("|", "&#124;").replace("\n", " ")
        table_rows.append(
            f"| {metric} | {threshold} | {score_str} | {verdict} | {reason_escaped} |"
        )
    table = "\n".join(table_rows)

    # Build 参照事実 list
    facts_lines = [f"- {fact}" for fact in expected_facts] if expected_facts else ["（なし）"]
    facts_section = "\n".join(facts_lines)

    md = f"""# {scenario_id} — {run}

## 質問

{input_text}

## 回答

{answer_text.rstrip()}

## 参照ナレッジ

{knowledge_section}

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
{table}

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

{facts_section}
"""
    return md


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0
    errors = 0

    for run_dir in sorted(RESULTS_DIR.iterdir()):
        if not run_dir.is_dir() or not run_dir.name.startswith("run-"):
            continue
        run = run_dir.name
        for scenario_dir in sorted(run_dir.iterdir()):
            if not scenario_dir.is_dir():
                continue
            eval_file = scenario_dir / "evaluation.json"
            if not eval_file.exists():
                continue
            scenario = scenario_dir.name
            out_file = OUTPUT_DIR / f"{run}-{scenario}.md"
            try:
                content = generate_md(run, scenario)
                out_file.write_text(content, encoding="utf-8")
                generated += 1
            except Exception as e:
                print(f"ERROR: {run}/{scenario}: {e}", file=sys.stderr)
                errors += 1

    print(f"Generated {generated} files to {OUTPUT_DIR}")
    if errors:
        print(f"Errors: {errors}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
