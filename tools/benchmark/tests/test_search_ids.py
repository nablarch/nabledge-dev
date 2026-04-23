"""Tests for ids variant selection resolution."""

from __future__ import annotations

from tools.benchmark.bench.search_ids import resolve_selections


ID_TO_PATH = {
    "handlers-tmh": {
        "path": "component/handlers/handlers-tmh.json",
        "sections": ["s1", "s2", "s3"],
    },
    "libraries-dao": {
        "path": "component/libraries/libraries-dao.json",
        "sections": ["s1"],
    },
}


def test_resolve_selections_happy_path():
    resolved, unresolved = resolve_selections(
        ["handlers-tmh|s3", "libraries-dao|s1"], ID_TO_PATH,
    )
    assert resolved == [
        "component/handlers/handlers-tmh.json:s3",
        "component/libraries/libraries-dao.json:s1",
    ]
    assert unresolved == []


def test_resolve_selections_flags_malformed_and_unknown():
    resolved, unresolved = resolve_selections(
        [
            "no-pipe",                    # malformed
            "unknown-file|s1",            # unknown file_id
            "handlers-tmh|s99",           # unknown sid
            "handlers-tmh|s2",            # valid
        ],
        ID_TO_PATH,
    )
    assert resolved == ["component/handlers/handlers-tmh.json:s2"]
    reasons = [u["reason"] for u in unresolved]
    assert reasons == ["malformed", "unknown file_id", "unknown sid"]


def test_resolve_selections_empty_input():
    assert resolve_selections([], ID_TO_PATH) == ([], [])
