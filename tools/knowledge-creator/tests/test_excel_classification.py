"""Tests for Excel file scanning and classification."""
import pytest
import os
import tempfile
import shutil
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify, classify_excel_by_pattern, XLSX_MAPPING


@pytest.fixture
def temp_repo():
    """Create temporary repository structure with Excel files."""
    repo = tempfile.mkdtemp()

    # Create releases directory with Excel files
    releases_dir = f"{repo}/.lw/nab-official/v6/nablarch-document/ja/releases"
    os.makedirs(releases_dir, exist_ok=True)

    # Create dummy Excel files
    for filename in [
        "nablarch6-releasenote.xlsx",
        "nablarch6u1-releasenote.xlsx",
        "nablarch6u3-releasenote.xlsx",
    ]:
        with open(f"{releases_dir}/{filename}", "w") as f:
            f.write("dummy")

    # Create security check Excel
    security_dir = (
        f"{repo}/.lw/nab-official/v6/"
        "nablarch-system-development-guide/"
        "Sample_Project/設計書"
    )
    os.makedirs(security_dir, exist_ok=True)
    with open(f"{security_dir}/Nablarch機能のセキュリティ対応表.xlsx", "w") as f:
        f.write("dummy")

    yield repo
    shutil.rmtree(repo)


class TestExcelScanning:
    """Test Excel file scanning in step1_list_sources.py."""

    def test_releases_excel_scanned(self, temp_repo):
        """releases/ディレクトリのExcelファイルがスキャンされる。"""
        from run import Context
        ctx = Context(version="6", repo=temp_repo, concurrency=1)
        result = Step1ListSources(ctx, dry_run=True).run()

        xlsx_files = [s for s in result["sources"] if s["format"] == "xlsx"]
        release_files = [
            f for f in xlsx_files
            if "releasenote" in f["filename"]
        ]

        assert len(release_files) == 3
        assert any("nablarch6-releasenote.xlsx" in f["filename"] for f in release_files)
        assert any("nablarch6u1-releasenote.xlsx" in f["filename"] for f in release_files)
        assert any("nablarch6u3-releasenote.xlsx" in f["filename"] for f in release_files)

    def test_security_check_excel_scanned(self, temp_repo):
        """セキュリティ対応表がスキャンされる。"""
        from run import Context
        ctx = Context(version="6", repo=temp_repo, concurrency=1)
        result = Step1ListSources(ctx, dry_run=True).run()

        xlsx_files = [s for s in result["sources"] if s["format"] == "xlsx"]
        security_files = [
            f for f in xlsx_files
            if "セキュリティ対応表" in f["filename"]
        ]

        assert len(security_files) == 1
        assert security_files[0]["filename"] == "Nablarch機能のセキュリティ対応表.xlsx"


class TestExcelClassification:
    """Test Excel file classification in step2_classify.py."""

    def test_classify_excel_by_pattern_v6_release(self):
        """nablarch6*-releasenote.xlsx → releases/releases"""
        result = classify_excel_by_pattern("nablarch6-releasenote.xlsx")
        assert result == ("releases", "releases")

        result = classify_excel_by_pattern("nablarch6u1-releasenote.xlsx")
        assert result == ("releases", "releases")

        result = classify_excel_by_pattern("nablarch6u3-releasenote.xlsx")
        assert result == ("releases", "releases")

    def test_classify_excel_by_pattern_v5_release(self):
        """nablarch5*-releasenote.xlsx → releases/releases"""
        result = classify_excel_by_pattern("nablarch5u12-releasenote.xlsx")
        assert result == ("releases", "releases")

        result = classify_excel_by_pattern("nablarch5u26-releasenote.xlsx")
        assert result == ("releases", "releases")

    def test_classify_excel_by_pattern_non_release(self):
        """リリースノート以外 → None"""
        result = classify_excel_by_pattern("other.xlsx")
        assert result is None

        result = classify_excel_by_pattern("data.xlsx")
        assert result is None


class TestExcelIDGeneration:
    """Test Excel file ID generation."""

    def test_security_check_fixed_id(self, temp_repo):
        """セキュリティ対応表のIDは 'security-check' (固定)"""
        from run import Context
        ctx = Context(version="6", repo=temp_repo, concurrency=1)

        sources = Step1ListSources(ctx, dry_run=True).run()
        classifier = Step2Classify(ctx, dry_run=True, sources_data=sources)

        filename = "Nablarch機能のセキュリティ対応表.xlsx"
        file_id = classifier.generate_id(filename, "xlsx", "security-check")

        assert file_id == "security-check"
        assert "-" not in file_id or file_id.count("-") == 1  # category only

    def test_release_note_pattern_id(self, temp_repo):
        """リリースノートのIDは 'releases-{filename}'"""
        from run import Context
        ctx = Context(version="6", repo=temp_repo, concurrency=1)

        sources = Step1ListSources(ctx, dry_run=True).run()
        classifier = Step2Classify(ctx, dry_run=True, sources_data=sources)

        filename = "nablarch6u1-releasenote.xlsx"
        file_id = classifier.generate_id(filename, "xlsx", "releases")

        assert file_id == "releases-nablarch6u1-releasenote"
        assert file_id.startswith("releases-")

    def test_xlsx_mapping_takes_precedence(self, temp_repo):
        """XLSX_MAPPINGで固定指定されたファイルはcategoryのみ"""
        from run import Context
        ctx = Context(version="6", repo=temp_repo, concurrency=1)

        sources = Step1ListSources(ctx, dry_run=True).run()
        classifier = Step2Classify(ctx, dry_run=True, sources_data=sources)

        # XLSX_MAPPINGに含まれるファイル
        for filename in XLSX_MAPPING.keys():
            type_, category = XLSX_MAPPING[filename]
            file_id = classifier.generate_id(filename, "xlsx", category)
            # categoryのみがIDになる（filename部分が含まれない）
            assert file_id == category
