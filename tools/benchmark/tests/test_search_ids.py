"""Tests for ids variant selection resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.benchmark.bench import io, search_ids
from tools.benchmark.bench.search_ids import (
    grep_term_hits,
    merge_term_hits_into_selections,
    resolve_selections,
)


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


@pytest.fixture
def fake_knowledge(tmp_path, monkeypatch):
    """Set up a minimal knowledge tree with two files for grep tests."""
    root = tmp_path / "knowledge"
    (root / "component/handlers").mkdir(parents=True)
    (root / "component/libraries").mkdir(parents=True)
    (root / "component/handlers/handlers-tmh.json").write_text(json.dumps({
        "id": "handlers-tmh",
        "title": "TMH",
        "index": [{"id": "s1", "title": "x"}, {"id": "s2", "title": "y"}, {"id": "s3", "title": "z"}],
        "sections": {
            "s1": "overview without term",
            "s2": "body mentions concurrentNumber explicitly",
            "s3": "body mentions concurrentNumber and HiddenStore",
        },
    }), encoding="utf-8")
    (root / "component/libraries/libraries-dao.json").write_text(json.dumps({
        "id": "libraries-dao",
        "title": "DAO",
        "index": [{"id": "s1", "title": "x"}],
        "sections": {"s1": "no match here"},
    }), encoding="utf-8")
    monkeypatch.setattr(io, "KNOWLEDGE_ROOT", root)
    return root


def test_grep_term_hits_finds_matching_sections(fake_knowledge):
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
        "libraries-dao": {
            "path": "component/libraries/libraries-dao.json",
            "sections": ["s1"],
        },
    }
    hits = grep_term_hits(["concurrentNumber"], id_to_path)
    assert len(hits) == 2
    assert {(h["file_id"], h["sid"]) for h in hits} == {
        ("handlers-tmh", "s2"),
        ("handlers-tmh", "s3"),
    }
    assert all(h["term"] == "concurrentNumber" for h in hits)


def test_grep_term_hits_respects_per_term_cap(fake_knowledge, monkeypatch):
    monkeypatch.setattr(search_ids, "TERM_HITS_PER_TERM", 1)
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
    }
    hits = grep_term_hits(["concurrentNumber"], id_to_path)
    assert len(hits) == 1


def test_grep_term_hits_empty_and_unknown(fake_knowledge):
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
    }
    assert grep_term_hits([], id_to_path) == []
    assert grep_term_hits(["noSuchIdentifier"], id_to_path) == []


def test_merge_term_hits_deduplicates():
    existing = ["handlers-tmh|s2"]
    hits = [
        {"term": "concurrentNumber", "file_id": "handlers-tmh", "sid": "s2", "chars": 10},
        {"term": "concurrentNumber", "file_id": "handlers-tmh", "sid": "s3", "chars": 10},
    ]
    merged = merge_term_hits_into_selections(existing, hits)
    assert merged == ["handlers-tmh|s2", "handlers-tmh|s3"]


def test_grep_term_hits_excludes_sample_guide(tmp_path, monkeypatch):
    root = tmp_path / "knowledge"
    (root / "component/handlers").mkdir(parents=True)
    (root / "guide/biz-samples").mkdir(parents=True)
    (root / "component/handlers/handlers-tmh.json").write_text(json.dumps({
        "id": "handlers-tmh",
        "title": "TMH",
        "index": [{"id": "s1", "title": "x"}],
        "sections": {"s1": "term AAA in handler"},
    }), encoding="utf-8")
    (root / "guide/biz-samples/biz-samples-01.json").write_text(json.dumps({
        "id": "biz-samples-01",
        "title": "Sample",
        "index": [{"id": "s1", "title": "x"}],
        "sections": {"s1": "term AAA in sample code"},
    }), encoding="utf-8")
    monkeypatch.setattr(io, "KNOWLEDGE_ROOT", root)
    id_to_path = {
        "biz-samples-01": {
            "path": "guide/biz-samples/biz-samples-01.json",
            "sections": ["s1"],
        },
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1"],
        },
    }
    hits = grep_term_hits(["AAA"], id_to_path)
    # biz-samples is excluded; only the handler body hit remains.
    assert [(h["file_id"], h["sid"]) for h in hits] == [("handlers-tmh", "s1")]


def test_merge_term_hits_respects_cap():
    existing = [f"f{i}|s1" for i in range(10)]
    hits = [{"term": "x", "file_id": "extra", "sid": f"s{i}", "chars": 1} for i in range(5)]
    merged = merge_term_hits_into_selections(existing, hits, cap=12)
    assert len(merged) == 12
    assert merged[-2:] == ["extra|s0", "extra|s1"]
