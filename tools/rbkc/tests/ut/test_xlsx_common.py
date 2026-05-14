"""Tests for xlsx_common P1-group section builder."""
from scripts.create.converters.xlsx_common import (
    RawSheet,
    _build_p1_group_sections,
    _detect_header,
    load_sheet_subtype_map,
    sheet_to_result,
)

# -- Fixture: security checklist-like sheet --
# Header: No | 脆弱性の種類 | 対策の性質 | 実施項目 | Nablarchでの対応
# Row 1:  1  | SQLインジェクション | 根本的解決 | エスケープ | ○
# Row 2:     |                    | 保険的対策 | ログ     | ×
# Row 3:  2  | XSS               | 根本的解決 | サニタイジング | ○
# Row 4:     |                    | 保険的対策 | 入力チェック | ○
# Row 5:     |                    | 根本的解決 | script禁止 | ×

HEADER = ["No", "脆弱性の種類", "対策の性質", "実施項目", "Nablarchでの対応"]

CHECKLIST_ROWS = [
    HEADER,
    ["1", "SQLインジェクション", "根本的解決", "エスケープ処理を施す", "○"],
    ["", "", "保険的対策", "ログを出力する", "×"],
    ["2", "クロスサイト・スクリプティング", "根本的解決", "サニタイジングを行う", "○"],
    ["", "", "保険的対策", "入力値をチェックする", "○"],
    ["", "", "根本的解決", "script要素を動的に生成しない", "×"],
]


def _make_sheet(rows, name="test"):
    return RawSheet(name=name, rows=rows)


class TestBuildP1GroupSections:
    def test_groups_by_no_column(self):
        sheet = _make_sheet(CHECKLIST_ROWS)
        sections, data_rows = _build_p1_group_sections(sheet, 1, HEADER)
        assert len(sections) == 2

    def test_group_title_from_vuln_name(self):
        sheet = _make_sheet(CHECKLIST_ROWS)
        sections, _ = _build_p1_group_sections(sheet, 1, HEADER)
        assert sections[0].title == "SQLインジェクション"
        assert sections[1].title == "クロスサイト・スクリプティング"

    def test_group_content_includes_all_rows(self):
        sheet = _make_sheet(CHECKLIST_ROWS)
        sections, _ = _build_p1_group_sections(sheet, 1, HEADER)
        assert "エスケープ処理を施す" in sections[0].content
        assert "ログを出力する" in sections[0].content
        assert "サニタイジングを行う" in sections[1].content
        assert "入力値をチェックする" in sections[1].content
        assert "script要素を動的に生成しない" in sections[1].content

    def test_data_rows_unchanged(self):
        """All original rows are preserved in data_rows for docs rendering."""
        sheet = _make_sheet(CHECKLIST_ROWS)
        _, data_rows = _build_p1_group_sections(sheet, 1, HEADER)
        assert len(data_rows) == 5

    def test_single_group(self):
        """All rows belong to one vulnerability."""
        rows = [
            HEADER,
            ["1", "CSRF", "根本的解決", "トークン検証", "○"],
            ["", "", "保険的対策", "Refererチェック", "×"],
        ]
        sheet = _make_sheet(rows)
        sections, _ = _build_p1_group_sections(sheet, 1, HEADER)
        assert len(sections) == 1
        assert sections[0].title == "CSRF"
        assert "トークン検証" in sections[0].content
        assert "Refererチェック" in sections[0].content

    def test_no_group_key_rows_before_first_group(self):
        """Rows before the first No-filled row are skipped."""
        rows = [
            HEADER,
            ["", "", "注記", "このシートは...", ""],
            ["1", "SQLインジェクション", "根本的解決", "エスケープ", "○"],
        ]
        sheet = _make_sheet(rows)
        sections, _ = _build_p1_group_sections(sheet, 1, HEADER)
        assert len(sections) == 1
        assert sections[0].title == "SQLインジェクション"

    def test_empty_rows_skipped(self):
        rows = [
            HEADER,
            ["1", "SQLインジェクション", "根本的解決", "エスケープ", "○"],
            ["", "", "", "", ""],
            ["", "", "保険的対策", "ログ", "×"],
        ]
        sheet = _make_sheet(rows)
        sections, data_rows = _build_p1_group_sections(sheet, 1, HEADER)
        assert len(sections) == 1
        assert "ログ" in sections[0].content
        assert len(data_rows) == 2


class TestLoadSheetSubtypeMapP1Group:
    def test_recognizes_p1_group(self, tmp_path):
        md = tmp_path / "mapping.md"
        md.write_text(
            "| セキュリティ対応表.xlsx | 2.チェックリスト | P1-group | grouped |\n"
        )
        result = load_sheet_subtype_map(md)
        assert ("セキュリティ対応表.xlsx", "2.チェックリスト") in result
        assert result[("セキュリティ対応表.xlsx", "2.チェックリスト")] == "P1-group"


class TestSheetToResultP1Group:
    def test_p1_group_produces_grouped_sections(self):
        sheet = _make_sheet(CHECKLIST_ROWS, name="2.チェックリスト")
        result, meta = sheet_to_result(sheet, sheet_subtype="P1-group")
        assert len(result.sections) == 2
        assert meta["sheet_type"] == "P1"
        assert result.sections[0].title == "SQLインジェクション"
        assert result.sections[1].title == "クロスサイト・スクリプティング"

    def test_p1_group_meta_has_all_data_rows(self):
        sheet = _make_sheet(CHECKLIST_ROWS, name="2.チェックリスト")
        _, meta = sheet_to_result(sheet, sheet_subtype="P1-group")
        assert len(meta["data_rows"]) == 5

    def test_normal_p1_unchanged(self):
        """Without P1-group subtype, normal P1 behavior (1 section per row)."""
        sheet = _make_sheet(CHECKLIST_ROWS, name="2.チェックリスト")
        result, meta = sheet_to_result(sheet, sheet_subtype=None)
        assert len(result.sections) == 5
        assert meta["sheet_type"] == "P1"
