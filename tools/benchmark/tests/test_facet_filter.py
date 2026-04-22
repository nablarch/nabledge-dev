"""Unit tests for facet_filter.

Covers parsing, AND filter semantics, wildcard behavior, fallback ladder,
and the five benchmark scenarios' expected candidate sets against the real
`index.toon`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.benchmark.filter.facet_filter import (
    IndexRow,
    filter_rows,
    filter_with_fallback,
    load_index,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = REPO_ROOT / ".claude/skills/nabledge-6/knowledge/index.toon"


@pytest.fixture(scope="module")
def rows() -> list[IndexRow]:
    return load_index(INDEX_PATH)


def test_load_index_parses_all_295_rows(rows: list[IndexRow]) -> None:
    assert len(rows) == 295


def test_load_index_skips_header_and_comments(rows: list[IndexRow]) -> None:
    assert not any(r.title.startswith("#") for r in rows)
    assert not any(r.title.startswith("files[") for r in rows)


def test_load_index_captures_path_ending_in_json(rows: list[IndexRow]) -> None:
    assert all(r.path.endswith(".json") for r in rows)


def test_filter_and_semantics() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "component", "libraries", "p2"),
        IndexRow("C", "processing-pattern", "web-application", "p3"),
        IndexRow("D", "processing-pattern", "nablarch-batch", "p4"),
    ]
    r = filter_rows(rows, ["component"], ["handlers"])
    assert [x.title for x in r] == ["A"]


def test_filter_or_within_axis() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "component", "libraries", "p2"),
        IndexRow("C", "processing-pattern", "web-application", "p3"),
    ]
    r = filter_rows(rows, ["component"], ["handlers", "libraries"])
    assert sorted(x.title for x in r) == ["A", "B"]


def test_filter_empty_type_is_wildcard() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "processing-pattern", "handlers", "p2"),
    ]
    r = filter_rows(rows, [], ["handlers"])
    assert len(r) == 2


def test_filter_empty_category_is_wildcard() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "component", "libraries", "p2"),
    ]
    r = filter_rows(rows, ["component"], [])
    assert len(r) == 2


def test_filter_both_empty_returns_all() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "processing-pattern", "web-application", "p2"),
    ]
    r = filter_rows(rows, [], [])
    assert len(r) == 2


def test_filter_no_match_returns_empty() -> None:
    rows = [IndexRow("A", "component", "handlers", "p1")]
    r = filter_rows(rows, ["guide"], ["biz-samples"])
    assert r == []


def test_fallback_none_when_primary_has_results() -> None:
    rows = [IndexRow("A", "component", "handlers", "p1")]
    outcome = filter_with_fallback(rows, ["component"], ["handlers"])
    assert outcome.fallback_used == "none"
    assert [r.title for r in outcome.rows] == ["A"]


def test_fallback_drops_category_when_primary_empty() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "component", "libraries", "p2"),
    ]
    outcome = filter_with_fallback(rows, ["component"], ["biz-samples"])
    assert outcome.fallback_used == "drop-category"
    assert sorted(r.title for r in outcome.rows) == ["A", "B"]


def test_fallback_drops_type_when_category_only_matches() -> None:
    rows = [
        IndexRow("A", "component", "handlers", "p1"),
        IndexRow("B", "guide", "biz-samples", "p2"),
    ]
    outcome = filter_with_fallback(rows, ["check"], ["biz-samples"])
    assert outcome.fallback_used == "drop-type"
    assert [r.title for r in outcome.rows] == ["B"]


def test_fallback_all_when_nothing_matches_either_axis() -> None:
    rows = [IndexRow("A", "component", "handlers", "p1")]
    outcome = filter_with_fallback(rows, ["guide"], ["biz-samples"])
    assert outcome.fallback_used == "all"
    assert len(outcome.rows) == 1


def test_fallback_empty_on_empty_index() -> None:
    outcome = filter_with_fallback([], ["component"], ["handlers"])
    assert outcome.fallback_used == "empty"
    assert outcome.rows == []


# --- Scenario-level coverage: for every benchmark scenario, confirm the
#     expected_facets produce a candidate set that contains every expected
#     file path. This is the Stage 1 → Stage 2 contract.

EXPECTED_SCENARIOS = [
    # (id, type, category, expected_paths)
    (
        "review-01",
        ["processing-pattern", "component"],
        ["nablarch-batch", "libraries"],
        [
            "processing-pattern/nablarch-batch/nablarch-batch-architecture.json",
            "processing-pattern/nablarch-batch/nablarch-batch-feature_details.json",
        ],
    ),
    (
        "review-04",
        ["processing-pattern", "component"],
        ["web-application", "libraries"],
        [
            "processing-pattern/web-application/web-application-feature_details.json",
            "component/libraries/libraries-bean_validation.json",
            "component/libraries/libraries-validation.json",
        ],
    ),
    (
        "impact-01",
        ["component"],
        ["handlers"],
        [
            "component/handlers/handlers-transaction_management_handler.json",
            "component/handlers/handlers-database_connection_management_handler.json",
        ],
    ),
    (
        "req-02",
        ["processing-pattern", "component"],
        ["web-application", "handlers", "libraries"],
        [
            "processing-pattern/web-application/web-application-feature_details.json",
            "component/handlers/handlers-permission_check_handler.json",
            "component/libraries/libraries-permission_check.json",
        ],
    ),
    # req-09 has empty expected_sections (uncertain / not-built-in). The
    # filter should still return a non-empty near-neighbor set.
    (
        "req-09",
        ["component", "processing-pattern"],
        ["handlers", "restful-web-service"],
        [],  # nothing required to be present, but set must not be empty
    ),
]


@pytest.mark.parametrize(
    "scenario_id,want_type,want_category,required_paths", EXPECTED_SCENARIOS
)
def test_scenario_filter_covers_expected_paths(
    rows: list[IndexRow],
    scenario_id: str,
    want_type: list[str],
    want_category: list[str],
    required_paths: list[str],
) -> None:
    outcome = filter_with_fallback(rows, want_type, want_category)
    assert outcome.fallback_used == "none", (
        f"{scenario_id}: expected primary AND to hit, got {outcome.fallback_used}"
    )
    got_paths = {r.path for r in outcome.rows}
    for p in required_paths:
        assert p in got_paths, (
            f"{scenario_id}: expected path {p!r} not in filter result "
            f"(got {len(got_paths)} paths, fallback={outcome.fallback_used})"
        )
    # Non-empty result for every scenario, including req-09.
    assert len(outcome.rows) > 0, f"{scenario_id}: filter returned empty set"
