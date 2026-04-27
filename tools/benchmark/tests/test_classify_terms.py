"""Unit tests for tools/benchmark/classify_terms.py (section-level TF).

The old page-level TF-IDF approach has been replaced. See
`tools/benchmark/docs/index-enrichment.md` for the current design.

Frozen param contract: boundary tests for tf_threshold / fallback_df_max pin
the semantics declared in `.work/00307/index-params-decision.md`. Changing
these boundaries is a design decision, not a test adjustment — if these
tests break, update the decision doc first.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.benchmark.classify_terms import (  # noqa: E402
    compute_candidates,
    iter_sections,
    select_keywords,
    tokenize_ja_deduped,
)


def _write_page(root: Path, rel: str, data: dict) -> None:
    fp = root / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


# ---- tokenize_ja_deduped -----------------------------------------------

def test_tokenize_dedupes_pure_katakana_span():
    """Unlike section_df_ja.tokenize_ja, TF-side tokenizer must NOT double-count
    the same character span just because both KATAKANA and MIXED patterns fire."""
    assert tokenize_ja_deduped("トランザクション") == ["トランザクション"]


def test_tokenize_dedupes_pure_kanji_span():
    assert tokenize_ja_deduped("顧客管理情報") == ["顧客管理情報"]


def test_tokenize_counts_real_occurrences():
    """Two real occurrences → TF=2 after dedup."""
    tokens = tokenize_ja_deduped("トランザクションとトランザクション")
    assert tokens.count("トランザクション") == 2


def test_tokenize_mixed_and_atomic_coexist():
    """'トランザクション管理' emits both the atomic katakana term and the
    greedy mixed compound — different terms, different spans → both kept."""
    tokens = tokenize_ja_deduped("トランザクション管理")
    assert set(tokens) == {"トランザクション", "トランザクション管理"}


def test_tokenize_rejects_under_4_chars():
    assert tokenize_ja_deduped("管理") == []
    assert tokenize_ja_deduped("ABC") == []


def test_tokenize_handles_empty_and_whitespace():
    assert tokenize_ja_deduped("") == []
    assert tokenize_ja_deduped("   ") == []


# ---- compute_candidates ------------------------------------------------

def test_compute_candidates_applies_stoplist(tmp_path):
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "ページ",
        "sections": {"s1": {"title": "t", "body": "トランザクション と ファイル"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist={"ファイル"})
    tf = per_sec["a|s1"]
    assert "トランザクション" in tf
    assert "ファイル" not in tf


def test_compute_candidates_excludes_page_title_overlap(tmp_path):
    """A term that appears in the page title is not useful as a keyword —
    the AI-1 prompt can already see the title."""
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "トランザクション管理ハンドラ",
        "sections": {"s1": {"title": "詳細", "body": "トランザクションの詳細"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist=set())
    tf = per_sec["a|s1"]
    # "トランザクション" is a substring of page title → excluded
    assert "トランザクション" not in tf


def test_compute_candidates_excludes_section_title_overlap(tmp_path):
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "ページA",
        "index": [{"id": "s1", "title": "バリデーション実行"}],
        "sections": {"s1": {"title": "バリデーション実行",
                             "body": "バリデーションを実行する"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist=set())
    tf = per_sec["a|s1"]
    # "バリデーション" is substring of section title → excluded
    assert "バリデーション" not in tf


def test_compute_candidates_tf_counts_real_occurrences(tmp_path):
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "X",
        "sections": {"s1": {"title": "t",
                             "body": "後方互換性 後方互換性 後方互換性"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist=set())
    assert per_sec["a|s1"]["後方互換性"] == 3


def test_compute_candidates_df_counts_distinct_sections(tmp_path):
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "X",
        "sections": {
            "s1": {"title": "t", "body": "トランザクション"},
            "s2": {"title": "t", "body": "トランザクション トランザクション"},
            "s3": {"title": "t", "body": "バリデーション"},
        },
    })
    sections = list(iter_sections(str(root)))
    _, df = compute_candidates(sections, stoplist=set())
    # TF doesn't affect DF: two sections contain トランザクション
    assert df["トランザクション"] == 2
    assert df["バリデーション"] == 1


def test_compute_candidates_df_respects_filters(tmp_path):
    """A term filtered out of a section (by stoplist or title overlap) must
    also not contribute to df for that section."""
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "ファイル処理",
        "sections": {
            "s1": {"title": "t", "body": "ファイル トランザクション"},
            "s2": {"title": "t", "body": "トランザクション"},
        },
    })
    sections = list(iter_sections(str(root)))
    _, df = compute_candidates(sections, stoplist={"ファイル"})
    # "ファイル" is in stoplist → df=0 (not tracked)
    assert df.get("ファイル", 0) == 0
    # "トランザクション" in s1 is excluded by title overlap (page title
    # contains it? no — page title is "ファイル処理"), so 2 sections
    assert df["トランザクション"] == 2


def test_compute_candidates_skips_no_knowledge_content(tmp_path):
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": {"s1": {"title": "t", "body": "トランザクション"}},
    })
    _write_page(root, "b.json", {
        "id": "b", "title": "B", "no_knowledge_content": True,
        "sections": {"s1": {"title": "t", "body": "バリデーション"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, df = compute_candidates(sections, stoplist=set())
    assert "a|s1" in per_sec
    assert "b|s1" not in per_sec
    assert "バリデーション" not in df


# ---- select_keywords (frozen params) -----------------------------------

def _sel(counter, df=None, **overrides):
    defaults = dict(
        tf_threshold=2, top_n=5,
        fallback_tf=1, fallback_df_max=20, fallback_top_n=3,
    )
    defaults.update(overrides)
    from collections import Counter
    return select_keywords(
        Counter(counter), Counter(df or {}), **defaults
    )


def test_select_primary_path_picks_tf_ge_2_top_n():
    counter = {"a": 5, "b": 3, "c": 2, "d": 1, "e": 1}
    # Primary: a(5), b(3), c(2) — all tf>=2; d,e drop. Top 5 = [a,b,c].
    assert _sel(counter) == ["a", "b", "c"]


def test_select_primary_respects_top_n_cap():
    counter = {"a": 9, "b": 8, "c": 7, "d": 6, "e": 5, "f": 4, "g": 3}
    # All tf>=2, top 5 by tf desc
    assert _sel(counter) == ["a", "b", "c", "d", "e"]


def test_select_primary_breaks_ties_alphabetically():
    """Deterministic output: equal-TF terms ordered by term string."""
    counter = {"zeta": 3, "alpha": 3, "mu": 3}
    assert _sel(counter) == ["alpha", "mu", "zeta"]


def test_select_fallback_triggers_when_primary_empty():
    """No term has tf>=2 → fallback uses tf>=1 AND df<=20, top 3."""
    counter = {"rare1": 1, "rare2": 1, "rare3": 1, "common": 1}
    df = {"rare1": 5, "rare2": 10, "rare3": 15, "common": 200}  # common df > 20
    # Primary empty. Fallback keeps rare* (df<=20), drops common.
    # All tf=1 → alphabetic tie-break.
    assert _sel(counter, df) == ["rare1", "rare2", "rare3"]


def test_select_fallback_drops_high_df_terms():
    """In fallback, a tf=1 term with df > 20 must not be selected even if it
    is the only remaining candidate."""
    counter = {"common": 1}
    df = {"common": 100}
    assert _sel(counter, df) == []


def test_select_fallback_respects_fallback_top_n():
    counter = {f"t{i}": 1 for i in range(10)}
    df = {f"t{i}": 5 for i in range(10)}
    result = _sel(counter, df)
    assert len(result) == 3  # fallback_top_n default


def test_select_primary_wins_over_fallback_when_any_primary_exists():
    """Even one primary candidate must prevent the fallback path."""
    counter = {"big": 2, "small1": 1, "small2": 1}
    df = {"big": 100, "small1": 5, "small2": 5}  # big has high df but primary wins
    # big passes tf>=2; primary path triggered → small* are not added
    assert _sel(counter) == ["big"]


def test_select_returns_empty_when_no_candidates():
    assert _sel({}) == []


def test_select_parameters_override():
    """Non-default params work end-to-end."""
    counter = {"a": 3, "b": 2}
    # Raise tf_threshold to 4 → primary empty → fallback (tf>=1, df<=x)
    df = {"a": 5, "b": 5}
    result = _sel(counter, df, tf_threshold=4, fallback_tf=1, fallback_df_max=10, fallback_top_n=2)
    assert result == ["a", "b"]


# ---- Boundary contract pinning (frozen params) -------------------------

def test_select_primary_tf_threshold_is_inclusive():
    """tf == tf_threshold is kept; tf == tf_threshold - 1 is dropped.

    Guards against a `>=` → `>` regression.
    """
    counter = {"x": 2, "y": 1}
    assert _sel(counter) == ["x"]


def test_select_primary_tf_threshold_respected_at_higher_value():
    counter = {"x": 3, "y": 2}
    assert _sel(counter, tf_threshold=3) == ["x"]


def test_select_fallback_df_max_is_inclusive():
    """df == fallback_df_max is kept; df == fallback_df_max + 1 is dropped.

    Guards against a `<=` → `<` regression.
    """
    counter = {"kept": 1, "dropped": 1}
    df = {"kept": 20, "dropped": 21}
    # Primary empty (both tf=1). Fallback: kept.df<=20 survives, dropped.df=21 out.
    assert _sel(counter, df) == ["kept"]


def test_select_both_paths_empty_returns_empty():
    """Primary empty AND fallback empty (all tf=1 but all df > cap) → []."""
    counter = {"a": 1, "b": 1, "c": 1}
    df = {"a": 100, "b": 100, "c": 100}
    assert _sel(counter, df) == []


def test_select_primary_tie_break_at_top_n_cutoff():
    """When equal-TF count > top_n, alphabetic order determines which survive.

    Guards against a regression to insertion-order tie-breaking.
    """
    counter = {"f": 3, "b": 3, "e": 3, "a": 3, "d": 3, "c": 3, "g": 3}
    assert _sel(counter) == ["a", "b", "c", "d", "e"]


# ---- Filter interaction pinning ----------------------------------------

def test_compute_candidates_double_exclusion_stoplist_and_title(tmp_path):
    """A term hit by BOTH stoplist and page title must still be excluded.

    Guards against a refactor that reorders `_passes_filters` and breaks one
    branch without the test catching it.
    """
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "ファイル処理ハンドラ",
        "sections": {"s1": {"title": "詳細", "body": "ファイル関連の記述 ファイル"}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, df = compute_candidates(sections, stoplist={"ファイル"})
    assert "ファイル" not in per_sec["a|s1"]
    assert df.get("ファイル", 0) == 0


def test_compute_candidates_df_excludes_section_where_term_filtered(tmp_path):
    """df counts only sections where the term *survived* all filters.

    Term survives in s1 (section title doesn't contain it) but is excluded in
    s2 by section-title overlap. df must be 1, not 2.
    """
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "ページA",
        "index": [
            {"id": "s1", "title": "詳細説明"},
            {"id": "s2", "title": "バリデーション実行"},
        ],
        "sections": {
            "s1": {"title": "詳細説明", "body": "バリデーション処理の詳細"},
            "s2": {"title": "バリデーション実行", "body": "バリデーションを実行する"},
        },
    })
    sections = list(iter_sections(str(root)))
    _, df = compute_candidates(sections, stoplist=set())
    assert df["バリデーション"] == 1


# ---- iter_sections shape coverage --------------------------------------

def test_iter_sections_accepts_string_body(tmp_path):
    """A section value that is a raw string (not a dict) is treated as body."""
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "index": [{"id": "s1", "title": "t"}],
        "sections": {"s1": "生テキストのトランザクション"},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist=set())
    assert per_sec["a|s1"]["トランザクション"] == 1


def test_iter_sections_non_string_body_is_empty(tmp_path):
    """A section whose body field is neither str nor missing (e.g., list)
    must not crash the tokenizer."""
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "index": [{"id": "s1", "title": "t"}],
        "sections": {"s1": {"title": "t", "body": ["unexpected"]}},
    })
    sections = list(iter_sections(str(root)))
    per_sec, _ = compute_candidates(sections, stoplist=set())
    # Section key is still produced, but TF counter is empty.
    assert per_sec["a|s1"] == __import__("collections").Counter()


def test_iter_sections_warns_on_malformed_json(tmp_path, capsys):
    """Corrupted JSON must be skipped with stderr warning, not crash."""
    root = tmp_path / "k"
    root.mkdir(parents=True, exist_ok=True)
    (root / "bad.json").write_text("{not-json", encoding="utf-8")
    _write_page(root, "good.json", {
        "id": "g", "title": "G",
        "index": [{"id": "s1", "title": "t"}],
        "sections": {"s1": {"title": "t", "body": "トランザクション"}},
    })
    sections = list(iter_sections(str(root)))
    err = capsys.readouterr().err
    assert "bad.json" in err
    page_ids = {rec["page_id"] for rec in sections}
    assert page_ids == {"g"}


def test_iter_sections_skips_non_dict_sections_value(tmp_path):
    """A page whose `sections` value is not a dict is skipped entirely."""
    root = tmp_path / "k"
    _write_page(root, "a.json", {
        "id": "a", "title": "A",
        "sections": ["unexpected", "list"],
    })
    _write_page(root, "b.json", {
        "id": "b", "title": "B",
        "sections": {"s1": {"title": "t", "body": "トランザクション"}},
    })
    sections = list(iter_sections(str(root)))
    page_ids = {rec["page_id"] for rec in sections}
    assert page_ids == {"b"}


# ---- Tokenizer document-order contract ---------------------------------

def test_tokenize_preserves_document_order():
    """Matches are sorted by start position; document order is load-bearing."""
    tokens = tokenize_ja_deduped("バリデーション-後方互換性-トランザクション")
    assert tokens == ["バリデーション", "後方互換性", "トランザクション"]


def test_tokenize_mixed_and_atomic_in_stable_order():
    """Atomic katakana and the greedy mixed compound at the same start offset
    come out in (start, end) order — atomic first (shorter end), then mixed."""
    tokens = tokenize_ja_deduped("トランザクション管理")
    assert tokens == ["トランザクション", "トランザクション管理"]
