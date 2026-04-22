"""Reference-answer-based grading for the benchmark.

Stage 2 is graded deterministically: the reference answer's `path#sid`
citations list the paths a correct answer must be grounded in, and we
check whether the filter produced candidates on those paths. No LLM is
involved.

Stage 3 still requires an LLM judge, but it is given the reference
answer as ground truth rather than being asked to self-estimate what a
correct answer should contain.
"""

from __future__ import annotations

import re

# Matches a citation written as `{path}.json#{sid}` inside backticks.
# Paths are relative to the knowledge root, may contain slashes/hyphens,
# and always end in .json. sid is always "s" followed by one or more digits.
_CITATION_RE = re.compile(r"`([^`]+\.json)#(s\d+)`")


def extract_citations(md: str) -> set[tuple[str, str]]:
    """Extract (path, sid) citations from reference-answer markdown.

    Returns a set so duplicates collapse. The caller usually only cares
    about the path set (via `{p for p, _ in cites}`); the sid is kept so
    Stage 3 judges can be told which section supports which fact.
    """
    return set(_CITATION_RE.findall(md))


def level_from_ratio(ratio: float) -> int:
    """Map a coverage ratio (0.0–1.0) to a 4-level verdict.

    - 1.0   → 3 (full)
    - ≥0.67 → 2 (partial)
    - ≥0.33 → 1 (insufficient)
    - <0.33 → 0 (miss)

    Thresholds mirror the existing LLM-judge rubric so Stage 2 verdicts
    are directly comparable to Stage 3 verdicts.
    """
    if ratio >= 1.0:
        return 3
    if ratio >= 2 / 3:
        return 2
    if ratio >= 1 / 3:
        return 1
    return 0


def score_stage2(
    expected_citations: set[tuple[str, str]],
    candidate_paths: set[str],
) -> dict:
    """Score Stage 2 by path-level inclusion.

    Stage 2 only asks: "did the filter surface the files a correct
    answer is grounded in?". Section-level detail is Stage 3's problem,
    so we dedupe citations to their file path and check set membership.

    If the reference answer has no citations (out-of-scope with no
    near-neighbor), any candidate list is trivially sufficient — we
    return level 3.
    """
    expected_paths = {p for p, _ in expected_citations}
    if not expected_paths:
        return {
            "level": 3,
            "ratio": 1.0,
            "covered": 0,
            "total": 0,
            "missing_paths": [],
        }

    missing = sorted(expected_paths - candidate_paths)
    covered = len(expected_paths) - len(missing)
    ratio = covered / len(expected_paths)
    return {
        "level": level_from_ratio(ratio),
        "ratio": ratio,
        "covered": covered,
        "total": len(expected_paths),
        "missing_paths": missing,
    }
