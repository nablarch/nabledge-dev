"""Unit tests for reference_answer grading module.

Covers:
- citation extraction from reference answer markdown
- coverage scoring against filter candidate paths (Stage 2 script judge)
- level assignment from coverage ratio
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.benchmark.grading.reference_answer import (
    extract_citations,
    level_from_ratio,
    score_stage2,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ANSWERS_DIR = (
    REPO_ROOT / "tools" / "benchmark" / "scenarios" / "qa-v6-answers"
)


# ---------------------------------------------------------------------------
# extract_citations
# ---------------------------------------------------------------------------


def test_extract_citations_basic() -> None:
    md = "see `foo/bar/baz.json#s1` and `foo/bar/baz.json#s3`."
    cites = extract_citations(md)
    assert ("foo/bar/baz.json", "s1") in cites
    assert ("foo/bar/baz.json", "s3") in cites


def test_extract_citations_deduplicates() -> None:
    md = "`a/b.json#s1` appears once, `a/b.json#s1` appears twice."
    assert extract_citations(md) == {("a/b.json", "s1")}


def test_extract_citations_ignores_non_citation_backticks() -> None:
    md = "code `BatchAction` and path `a/b.json#s1`."
    cites = extract_citations(md)
    assert ("a/b.json", "s1") in cites
    # non-citation backticks produce no tuple
    assert len(cites) == 1


def test_extract_citations_handles_multiple_per_line() -> None:
    md = "— `a/b.json#s1`、`a/b.json#s2`"
    cites = extract_citations(md)
    assert cites == {("a/b.json", "s1"), ("a/b.json", "s2")}


def test_extract_citations_empty_returns_empty_set() -> None:
    assert extract_citations("") == set()
    assert extract_citations("no citations here") == set()


def test_extract_citations_rejects_sid_without_s_prefix() -> None:
    # s{digits} is required — "#1" alone is not a section id
    assert extract_citations("`a/b.json#1`") == set()


def test_extract_citations_real_file() -> None:
    md = (ANSWERS_DIR / "review-01.md").read_text(encoding="utf-8")
    cites = extract_citations(md)
    # review-01 cites architecture, application_design, getting-started, feature_details
    paths = {p for p, _ in cites}
    assert any("architecture.json" in p for p in paths)
    assert any("application_design.json" in p for p in paths)
    assert any("getting-started-nablarch-batch.json" in p for p in paths)


# ---------------------------------------------------------------------------
# level_from_ratio
# ---------------------------------------------------------------------------


def test_level_from_ratio_thresholds() -> None:
    assert level_from_ratio(1.0) == 3
    assert level_from_ratio(0.99) == 2
    assert level_from_ratio(0.67) == 2
    assert level_from_ratio(0.66) == 1
    assert level_from_ratio(0.34) == 1  # just above 1/3
    assert level_from_ratio(0.33) == 0  # 0.33 < 1/3 = 0.333...
    assert level_from_ratio(0.0) == 0


def test_level_from_ratio_boundaries_are_inclusive_at_upper() -> None:
    # 2/3 = 0.6667 → partial (2)
    assert level_from_ratio(2 / 3) == 2
    # 1/3 = 0.3333 → insufficient (1)
    assert level_from_ratio(1 / 3) == 1


# ---------------------------------------------------------------------------
# score_stage2
# ---------------------------------------------------------------------------


def test_score_stage2_full_coverage_is_level_3() -> None:
    expected = {("a/b.json", "s1"), ("a/b.json", "s2")}
    candidate_paths = {"a/b.json", "other/c.json"}
    result = score_stage2(expected, candidate_paths)
    # Both expected paths present in candidates → 1.0 → level 3
    assert result["level"] == 3
    assert result["ratio"] == 1.0
    assert result["covered"] == 1  # unique expected path count
    assert result["total"] == 1


def test_score_stage2_partial_coverage() -> None:
    expected = {
        ("a/b.json", "s1"),
        ("x/y.json", "s1"),
        ("z/w.json", "s1"),
    }
    candidate_paths = {"a/b.json", "x/y.json"}  # 2 of 3 distinct paths
    result = score_stage2(expected, candidate_paths)
    assert result["covered"] == 2
    assert result["total"] == 3
    assert result["ratio"] == pytest.approx(2 / 3)
    assert result["level"] == 2  # ≥ 0.67


def test_score_stage2_zero_coverage() -> None:
    expected = {("a/b.json", "s1"), ("x/y.json", "s1")}
    candidate_paths: set[str] = set()
    result = score_stage2(expected, candidate_paths)
    assert result["covered"] == 0
    assert result["total"] == 2
    assert result["ratio"] == 0.0
    assert result["level"] == 0


def test_score_stage2_missing_paths_are_reported() -> None:
    expected = {("a/b.json", "s1"), ("x/y.json", "s2")}
    candidate_paths = {"a/b.json"}
    result = score_stage2(expected, candidate_paths)
    assert "x/y.json" in result["missing_paths"]
    assert "a/b.json" not in result["missing_paths"]


def test_score_stage2_dedupes_by_path_not_section() -> None:
    # Two citations to the same path but different sections count as ONE
    # expected path. Stage 2 checks file-level inclusion, not section-level.
    expected = {("a/b.json", "s1"), ("a/b.json", "s3")}
    candidate_paths = {"a/b.json"}
    result = score_stage2(expected, candidate_paths)
    assert result["total"] == 1
    assert result["covered"] == 1
    assert result["level"] == 3


def test_score_stage2_empty_expected_returns_level_3() -> None:
    # If the reference answer has no citations (out-of-scope with no known
    # near-neighbor), any candidate list is trivially sufficient. Level 3.
    result = score_stage2(set(), {"whatever.json"})
    assert result["level"] == 3
    assert result["total"] == 0
    assert result["covered"] == 0
    assert result["ratio"] == 1.0
