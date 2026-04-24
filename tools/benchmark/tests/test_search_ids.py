"""Tests for ids variant selection resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.benchmark.bench import io, search_ids
from tools.benchmark.bench.search_ids import (
    _render_answer_markdown,
    grep_term_hits,
    merge_term_hits_into_selections,
    resolve_selections,
    verify_read_notes,
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


def test_verify_read_notes_detects_verbatim_and_paraphrase(fake_knowledge):
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
    }
    read_notes = [{
        "file_id": "handlers-tmh",
        "relevant_sections": [
            {"sid": "s2", "evidence": "body mentions concurrentNumber"},
            # paraphrase — not a substring
            {"sid": "s3", "evidence": "talks about concurrency settings"},
        ],
    }]
    result = verify_read_notes(read_notes, id_to_path)
    verdicts = {(r["file_id"], r["sid"]): r["verdict"] for r in result["per_section"]}
    assert verdicts[("handlers-tmh", "s2")] == "match"
    assert verdicts[("handlers-tmh", "s3")] == "mismatch"
    assert result["mismatches"] == 1
    assert result["total"] == 2


def test_verify_read_notes_flags_unknown_file(fake_knowledge):
    id_to_path = {}  # no files registered
    read_notes = [{
        "file_id": "ghost",
        "relevant_sections": [{"sid": "s1", "evidence": "anything"}],
    }]
    result = verify_read_notes(read_notes, id_to_path)
    assert result["per_section"][0]["verdict"] == "file-missing"


def test_verify_read_notes_flags_unknown_sid(fake_knowledge):
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
    }
    read_notes = [{
        "file_id": "handlers-tmh",
        "relevant_sections": [{"sid": "s99", "evidence": "anything"}],
    }]
    result = verify_read_notes(read_notes, id_to_path)
    assert result["per_section"][0]["verdict"] == "section-missing"


def test_verify_read_notes_accepts_normalized_paraphrase(tmp_path, monkeypatch):
    """Whitespace collapse + markdown header strip should count as match.

    AI-1 legitimately trims leading `## ` and joins adjacent lines; those
    benign rewrites must not register as fabrication.
    """
    root = tmp_path / "knowledge"
    (root / "c").mkdir(parents=True)
    body = "## セクション見出し\n\n本文の一文目。\n\n本文の二文目。"
    (root / "c/f.json").write_text(json.dumps({
        "id": "f", "title": "F",
        "index": [{"id": "s1", "title": "t"}],
        "sections": {"s1": body},
    }), encoding="utf-8")
    monkeypatch.setattr(io, "KNOWLEDGE_ROOT", root)
    id_to_path = {"f": {"path": "c/f.json", "sections": ["s1"]}}
    read_notes = [{
        "file_id": "f",
        "relevant_sections": [
            # header stripped, whitespace collapsed — still a match
            {"sid": "s1", "evidence": "本文の一文目。 本文の二文目。"},
        ],
    }]
    result = verify_read_notes(read_notes, id_to_path)
    assert result["per_section"][0]["verdict"] == "match"


def test_verify_read_notes_rejects_real_fabrication(fake_knowledge):
    """Content that doesn't appear in the body in any form must mismatch."""
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s2", "s3"],
        },
    }
    read_notes = [{
        "file_id": "handlers-tmh",
        "relevant_sections": [
            {"sid": "s1", "evidence": "TMH has a Kafka integration"},
        ],
    }]
    result = verify_read_notes(read_notes, id_to_path)
    assert result["per_section"][0]["verdict"] == "mismatch"


def test_verify_read_notes_empty_input():
    result = verify_read_notes([], {})
    assert result == {
        "per_section": [], "total": 0, "mismatches": 0, "mismatch_rate": 0.0,
    }


def test_render_answer_markdown_shape():
    id_to_path = {
        "handlers-tmh": {
            "path": "component/handlers/handlers-tmh.json",
            "sections": ["s1", "s3"],
        },
    }
    md = _render_answer_markdown(
        conclusion="結論の一文。",
        evidence=[
            {"quote": "本文の引用", "cited": "handlers-tmh|s1"},
            {"quote": "別の引用", "cited": "handlers-tmh|s3"},
        ],
        caveats=["注意点 1"],
        cited_refs=["handlers-tmh|s1", "handlers-tmh|s3"],
        id_to_path=id_to_path,
    )
    assert "**結論**: 結論の一文。" in md
    assert "**根拠**:" in md
    # ref is resolved to path:sid form
    assert "(component/handlers/handlers-tmh.json:s1)" in md
    assert "(component/handlers/handlers-tmh.json:s3)" in md
    assert "**注意点**:\n- 注意点 1" in md
    assert md.rstrip().endswith(
        "参照: component/handlers/handlers-tmh.json:s1, "
        "component/handlers/handlers-tmh.json:s3"
    )


def test_render_answer_markdown_skips_empty_sections():
    md = _render_answer_markdown(
        conclusion="結論のみ",
        evidence=[],
        caveats=[],
        cited_refs=[],
        id_to_path={},
    )
    assert md.startswith("**結論**: 結論のみ")
    assert "**根拠**" not in md
    assert "**注意点**" not in md
    assert "参照:" not in md


def test_merge_term_hits_respects_cap():
    existing = [f"f{i}|s1" for i in range(10)]
    hits = [{"term": "x", "file_id": "extra", "sid": f"s{i}", "chars": 1} for i in range(5)]
    merged = merge_term_hits_into_selections(existing, hits, cap=12)
    assert len(merged) == 12
    assert merged[-2:] == ["extra|s0", "extra|s1"]
