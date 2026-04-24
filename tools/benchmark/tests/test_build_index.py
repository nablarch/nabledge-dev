"""Unit tests for tools/benchmark/build_index.py.

The index-llm.md format attaches section-level Japanese keywords produced by
classify_terms.py. `collect` now takes a {`page_id|section_id`: [keyword,...]}
map (not a flat allowlist) and places each keyword only on its own section.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.benchmark.build_index import (  # noqa: E402
    build_llm_index,
    build_script_index,
    collect,
)


def _make_knowledge(tmp_path: Path, files: list[dict]) -> Path:
    root = tmp_path / "knowledge"
    for f in files:
        fp = root / f["rel"]
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(json.dumps(f["data"], ensure_ascii=False), encoding="utf-8")
    return root


def test_collect_skips_no_knowledge_content(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a/x.json", "data": {"id": "x", "title": "X", "index": []}},
        {"rel": "a/y.json", "data": {"id": "y", "title": "Y", "no_knowledge_content": True}},
    ])
    entries = collect(str(root), {})
    ids = [e["id"] for e in entries]
    assert ids == ["x"]


def test_collect_preserves_sections_order(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "a", "title": "A",
            "index": [
                {"id": "s1", "title": "First"},
                {"id": "s2", "title": "Second"},
                {"id": "s3", "title": "Third"},
            ],
        }},
    ])
    entries = collect(str(root), {})
    assert entries[0]["sections"] == [
        {"id": "s1", "title": "First", "keywords": []},
        {"id": "s2", "title": "Second", "keywords": []},
        {"id": "s3", "title": "Third", "keywords": []},
    ]


def test_collect_attaches_keywords_by_section_key(tmp_path):
    """keywords[page_id|section_id] → section.keywords (no body matching)."""
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "handlers-tx", "title": "トランザクションハンドラ",
            "index": [
                {"id": "s1", "title": "概要"},
                {"id": "s2", "title": "設定"},
            ],
        }},
    ])
    keyword_map = {
        "handlers-tx|s1": ["コールバック", "ロールバック"],
        "handlers-tx|s2": ["transactionName"],
    }
    entries = collect(str(root), keyword_map)
    sections = entries[0]["sections"]
    assert sections[0]["keywords"] == ["コールバック", "ロールバック"]
    assert sections[1]["keywords"] == ["transactionName"]


def test_collect_empty_keywords_for_unmapped_sections(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "p", "title": "P",
            "index": [{"id": "s1", "title": "セクション1"}],
        }},
    ])
    entries = collect(str(root), {})
    assert entries[0]["sections"][0]["keywords"] == []


def test_llm_index_renders_keywords_with_separator(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "secure_handler", "title": "セキュアハンドラ",
            "index": [
                {"id": "s6", "title": "CSP対応"},
                {"id": "s8", "title": "nonce生成"},
            ],
        }},
    ])
    keyword_map = {
        "secure_handler|s6": ["ポリシー設定", "違反レポート"],
        "secure_handler|s8": [],
    }
    entries = collect(str(root), keyword_map)
    out = build_llm_index(entries, version="6")
    assert "[secure_handler] セキュアハンドラ  (a.json)" in out
    assert "  s6:CSP対応 — ポリシー設定 / 違反レポート" in out
    # Section with no keywords: no trailing separator.
    assert "  s8:nonce生成\n" in out
    assert "s8:nonce生成 —" not in out


def test_llm_index_handles_sectionless_file(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {"id": "solo", "title": "単独", "index": []}},
    ])
    entries = collect(str(root), {})
    out = build_llm_index(entries, version="6")
    assert "[solo] 単独  (a.json)" in out
    lines = [ln for ln in out.splitlines() if ln.startswith("  s")]
    assert not lines


def test_script_index_maps_id_to_path_and_sections(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "component/handlers/secure_handler.json", "data": {
            "id": "secure_handler", "title": "セキュアハンドラ",
            "index": [
                {"id": "s1", "title": "概要"},
                {"id": "s6", "title": "CSP"},
            ],
        }},
    ])
    entries = collect(str(root), {})
    s = json.loads(build_script_index(entries))
    assert s["secure_handler"]["path"] == "component/handlers/secure_handler.json"
    assert s["secure_handler"]["sections"] == ["s1", "s6"]


def test_collect_ignores_files_without_id_or_title(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "bad1.json", "data": {"title": "no id"}},
        {"rel": "bad2.json", "data": {"id": "no-title"}},
        {"rel": "ok.json", "data": {"id": "ok", "title": "OK", "index": []}},
    ])
    entries = collect(str(root), {})
    assert [e["id"] for e in entries] == ["ok"]


def test_collect_ignores_unmapped_keyword_keys(tmp_path):
    """Extra keys in keyword_map that don't match any section must be
    silently dropped, not raise — the map is a lookup, not a schema."""
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "real", "title": "R",
            "index": [{"id": "s1", "title": "t"}],
        }},
    ])
    keyword_map = {
        "ghost|s99": ["should not appear"],
        "real|s1": ["keep"],
    }
    entries = collect(str(root), keyword_map)
    assert entries[0]["sections"][0]["keywords"] == ["keep"]


def test_collect_skips_bad_index_entries(tmp_path):
    """Index entries without id or that are not dicts are skipped."""
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "p", "title": "P",
            "index": [
                {"title": "no id"},
                "not a dict",
                {"id": "s1", "title": "ok"},
            ],
        }},
    ])
    entries = collect(str(root), {})
    assert [s["id"] for s in entries[0]["sections"]] == ["s1"]


def test_llm_index_header_carries_relative_path(tmp_path):
    """AI-1 needs the file path on the header line to call Read directly."""
    root = _make_knowledge(tmp_path, [
        {"rel": "component/handlers/secure_handler.json", "data": {
            "id": "secure_handler", "title": "セキュアハンドラ",
            "index": [{"id": "s1", "title": "概要"}],
        }},
    ])
    entries = collect(str(root), {})
    out = build_llm_index(entries, version="6")
    assert "(component/handlers/secure_handler.json)" in out
    # Path comes after title on the same header line, not on its own line.
    header = [ln for ln in out.splitlines() if ln.startswith("[secure_handler]")]
    assert len(header) == 1
    assert "component/handlers/secure_handler.json" in header[0]


def test_collect_preserves_keyword_order(tmp_path):
    """Output keyword order must match the input list order exactly."""
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "p", "title": "P",
            "index": [{"id": "s1", "title": "t"}],
        }},
    ])
    kw = ["zeta", "alpha", "mu"]
    entries = collect(str(root), {"p|s1": kw})
    assert entries[0]["sections"][0]["keywords"] == kw
