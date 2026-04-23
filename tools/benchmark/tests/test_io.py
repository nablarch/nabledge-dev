"""Tests for bench.io path/citation helpers."""

from __future__ import annotations

from tools.benchmark.bench import io
from tools.benchmark.bench.types import JudgeVerdict


def test_extract_reference_citations_dedupes_and_preserves_order():
    md = (
        "See handlers-transaction_management_handler.json:s3 "
        "and handlers-database_connection_management_handler.json#s2 "
        "and handlers-transaction_management_handler.json:s3 again."
    )
    out = io.extract_reference_citations(md)
    assert out == [
        ("handlers-transaction_management_handler.json", "s3"),
        ("handlers-database_connection_management_handler.json", "s2"),
    ]


def test_extract_reference_citations_handles_no_citations():
    assert io.extract_reference_citations("nothing interesting here") == []


def test_verdict_from_structured_maps_fields():
    s = {
        "level": 2,
        "required_facts": [{"fact": "X", "status": "COVERED"}],
        "over_reach": [{"claim": "Y", "type": "OVER-REACH", "why": "Z"}],
        "reasoning": "ok",
    }
    v = io.verdict_from_structured(s)
    assert isinstance(v, JudgeVerdict)
    assert v.level == 2
    assert v.required_facts == [{"fact": "X", "status": "COVERED"}]
    assert v.over_reach[0]["type"] == "OVER-REACH"
    assert v.reasoning == "ok"


def test_verdict_from_structured_returns_none_on_empty():
    assert io.verdict_from_structured(None) is None
    assert io.verdict_from_structured({}) is not None  # empty is still a verdict at level 0


def test_load_scenarios_maps_questions_and_reference(tmp_path):
    """Sanity: load_scenarios wires question/expected_sections/reference_answer."""
    scenarios = io.load_scenarios()
    assert scenarios, "qa-v6.json should be non-empty"
    # Every scenario has an id and question; reference answer is present when the md exists.
    by_id = {s.id: s for s in scenarios}
    assert "review-01" in by_id
    s = by_id["review-01"]
    assert s.question
    assert s.expected_sections
    assert s.reference_answer  # review-01.md must exist
