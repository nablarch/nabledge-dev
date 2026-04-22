"""Unit tests for tools/benchmark/build_index.py."""
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
    entries = collect(str(root))
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
    entries = collect(str(root))
    assert entries[0]["sections"] == [
        {"id": "s1", "title": "First"},
        {"id": "s2", "title": "Second"},
        {"id": "s3", "title": "Third"},
    ]


def test_llm_index_format_has_header_and_sections(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {
            "id": "secure_handler", "title": "セキュアハンドラ",
            "index": [
                {"id": "s6", "title": "Content Security Policy(CSP)対応"},
                {"id": "s8", "title": "nonce生成"},
            ],
        }},
    ])
    entries = collect(str(root))
    out = build_llm_index(entries, version="6")
    assert "[secure_handler] セキュアハンドラ" in out
    assert "s6:Content Security Policy(CSP)対応" in out
    assert "s8:nonce生成" in out
    # Sections are joined with " / " on one indented line.
    assert "  s6:Content Security Policy(CSP)対応 / s8:nonce生成" in out


def test_llm_index_handles_sectionless_file(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "a.json", "data": {"id": "solo", "title": "単独", "index": []}},
    ])
    entries = collect(str(root))
    out = build_llm_index(entries, version="6")
    assert "[solo] 単独" in out
    # No indented section line when no sections exist.
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
    entries = collect(str(root))
    s = json.loads(build_script_index(entries))
    assert s["secure_handler"]["path"] == "component/handlers/secure_handler.json"
    assert s["secure_handler"]["sections"] == ["s1", "s6"]


def test_collect_ignores_files_without_id_or_title(tmp_path):
    root = _make_knowledge(tmp_path, [
        {"rel": "bad1.json", "data": {"title": "no id"}},
        {"rel": "bad2.json", "data": {"id": "no-title"}},
        {"rel": "ok.json", "data": {"id": "ok", "title": "OK", "index": []}},
    ])
    entries = collect(str(root))
    assert [e["id"] for e in entries] == ["ok"]
