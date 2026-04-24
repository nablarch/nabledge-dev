"""Unit tests for tools/benchmark/section_df_ja.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.benchmark.section_df_ja import (  # noqa: E402
    compute_section_df,
    iter_sections,
    tokenize_ja,
)


def _write_page(root: Path, rel: str, data: dict) -> None:
    fp = root / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_tokenize_ja_extracts_three_patterns():
    # katakana 4+, kanji 4+, mixed kanji/katakana 4+
    text = "トランザクション管理と後方互換性と悲観ロックとABC"
    tokens = tokenize_ja(text)
    assert "トランザクション" in tokens
    assert "後方互換性" in tokens
    # "悲観ロック" is captured by the MIXED pattern (kanji + katakana)
    assert "悲観ロック" in tokens
    # ASCII must not be captured
    assert "ABC" not in tokens
    # Under 4 chars must not be captured
    assert "管理" not in tokens


def test_tokenize_ja_drops_under_4_chars():
    assert tokenize_ja("管理") == []
    assert tokenize_ja("ログ") == []
    assert tokenize_ja("abc") == []


def test_tokenize_ja_handles_empty():
    assert tokenize_ja("") == []
    assert tokenize_ja("   ") == []


def test_section_df_counts_distinct_sections(tmp_path):
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "sec1", "body": "トランザクション管理"},
            "s2": {"title": "sec2", "body": "トランザクションの話"},
        },
    })
    _write_page(root, "b.json", {
        "id": "b", "title": "B",
        "sections": {
            "s1": {"title": "sec1", "body": "バリデーション処理"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    # "トランザクション" appears in 2 distinct sections of page a
    assert df["トランザクション"]["section_df"] == 2
    # "バリデーション" appears in 1 section
    assert df["バリデーション"]["section_df"] == 1


def test_section_df_same_term_twice_in_one_section_counts_once(tmp_path):
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "t", "body": "トランザクションとトランザクション管理"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    # Same term twice in one section → section_df=1 (it's section count, not tf)
    assert df["トランザクション"]["section_df"] == 1


def test_section_df_skips_no_knowledge_content(tmp_path):
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {"s1": {"title": "t", "body": "トランザクション"}},
    })
    _write_page(root, "b.json", {
        "id": "b", "title": "B",
        "no_knowledge_content": True,
        "sections": {"s1": {"title": "t", "body": "バリデーション"}},
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert "トランザクション" in df
    # excluded page's terms must not appear
    assert "バリデーション" not in df


def test_section_df_handles_empty_body(tmp_path):
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "t", "body": ""},
            "s2": {"title": "t", "body": "トランザクション"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert df["トランザクション"]["section_df"] == 1


def test_section_df_sample_ids_use_stable_key_and_cap(tmp_path):
    root = tmp_path / "knowledge"
    # Make 8 sections all containing the term
    sections_dict = {
        f"s{i}": {"title": f"t{i}", "body": "トランザクション"}
        for i in range(1, 9)
    }
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": sections_dict,
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    sample_ids = df["トランザクション"]["sample_section_ids"]
    # Capped at 5
    assert len(sample_ids) == 5
    # Stable key form "{page_id}|{section_id}"
    for sid in sample_ids:
        assert sid.startswith("a|s")
    # Deterministic order (first 5 when sorted by section key)
    assert sample_ids == sorted(sample_ids)


def test_section_df_includes_pattern_label(tmp_path):
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "t", "body": "トランザクション"},
            "s2": {"title": "t", "body": "後方互換性"},
            "s3": {"title": "t", "body": "悲観ロック"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert df["トランザクション"]["pattern"] == "katakana"
    assert df["後方互換性"]["pattern"] == "kanji"
    assert df["悲観ロック"]["pattern"] == "mixed"


def test_tokenize_ja_katakana_also_matches_mixed_pattern():
    """Pin the contract: a pure-katakana term is emitted twice (katakana + mixed).

    Per-section dedup in compute_section_df makes this harmless for section_df,
    but if tokenize_ja is ever consumed for tf, callers must dedup explicitly.
    """
    tokens = tokenize_ja("トランザクション")
    assert tokens == ["トランザクション", "トランザクション"]


def test_tokenize_ja_kanji_also_matches_mixed_pattern():
    """Pin the contract: a pure-kanji term is emitted twice (kanji + mixed)."""
    tokens = tokenize_ja("顧客管理情報")
    assert tokens == ["顧客管理情報", "顧客管理情報"]


def test_tokenize_ja_mixed_compound_greedy_span(tmp_path):
    """Pin the contract: mixed greedily grabs the whole kanji+katakana run.

    "トランザクション管理" → PATTERN_KATAKANA grabs "トランザクション",
    PATTERN_KANJI does NOT grab "管理" (under 4 chars),
    PATTERN_MIXED grabs the whole "トランザクション管理".
    Result: 2 distinct section_df entries, atomic and compound.
    """
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "t", "body": "トランザクション管理"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert set(df.keys()) == {"トランザクション", "トランザクション管理"}
    assert df["トランザクション"]["section_df"] == 1
    assert df["トランザクション管理"]["section_df"] == 1


def test_classify_pattern_prefers_pure_script_over_mixed():
    """Pin fullmatch order: pure kanji / katakana are NOT classified as mixed."""
    from tools.benchmark.section_df_ja import classify_pattern
    assert classify_pattern("顧客管理情報") == "kanji"
    assert classify_pattern("データベース") == "katakana"
    assert classify_pattern("リクエストパラメータ") == "katakana"
    # Only real mixed (kanji + katakana) gets the mixed label
    assert classify_pattern("悲観ロック") == "mixed"


def test_iter_sections_handles_section_as_string(tmp_path):
    """A section stored as a raw string body (not a dict) is accepted."""
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": "生テキストのトランザクション",
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert df["トランザクション"]["section_df"] == 1


def test_iter_sections_non_dict_non_str_body_is_empty(tmp_path):
    """A section whose value is neither str nor dict is treated as empty."""
    root = tmp_path / "knowledge"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": ["unexpected", "list"],
            "s2": {"title": "t", "body": "トランザクション"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    # s1 produced no tokens; s2 term is the only one counted
    assert df["トランザクション"]["section_df"] == 1
    # s1 is still yielded (as an empty-body section) so it counts toward total
    assert len(sections) == 2


def test_iter_sections_warns_on_malformed_json(tmp_path, capsys):
    """Corrupted JSON files must be skipped with a stderr warning, not silently."""
    root = tmp_path / "knowledge"
    root.mkdir(parents=True, exist_ok=True)
    (root / "bad.json").write_text("{not-json", encoding="utf-8")
    _write_page(root, "good.json", {
        "id": "g", "title": "G",
        "sections": {"s1": {"title": "t", "body": "トランザクション"}},
    })
    sections = list(iter_sections(str(root)))
    err = capsys.readouterr().err
    assert "bad.json" in err
    # good page is still processed
    page_ids = {pid for pid, _, _ in sections}
    assert page_ids == {"g"}


def test_tokenize_ja_punctuation_inside_katakana_block_is_captured():
    """Pin: prolonged mark ー (U+30FC) and middle dot ・ (U+30FB) are both
    inside the [゠-ヿー] katakana range, so 4+ runs of either match.

    This is accepted as-is — such runs don't occur in the v6 corpus, and
    filtering them adds complexity without benefit. If they ever surface
    as a top-ranked term, add them to the stoplist manually.
    """
    assert tokenize_ja("ーーーー") == ["ーーーー", "ーーーー"]
    assert tokenize_ja("・・・・") == ["・・・・", "・・・・"]


def test_section_df_df_ratio_matches_section_count(tmp_path):
    root = tmp_path / "knowledge"
    # 4 sections total; term appears in 2 → df_ratio = 0.5
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {
            "s1": {"title": "t", "body": "トランザクション"},
            "s2": {"title": "t", "body": "トランザクション"},
            "s3": {"title": "t", "body": "バリデーション"},
            "s4": {"title": "t", "body": "バリデーション"},
        },
    })
    sections = list(iter_sections(str(root)))
    df = compute_section_df(sections)
    assert df["トランザクション"]["df_ratio"] == 0.5
    assert df["バリデーション"]["df_ratio"] == 0.5
