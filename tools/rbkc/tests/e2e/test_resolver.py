"""E2E tests for Phase 4: resolver against actual Nablarch v6 documentation."""
from pathlib import Path

import pytest

from scripts.resolver import AssetRef, build_label_map, collect_asset_refs, copy_assets

_REPO_ROOT = Path(__file__).parents[4]
V6_DOC_ROOT = _REPO_ROOT / ".lw/nab-official/v6/nablarch-document/ja"


# ---------------------------------------------------------------------------
# E2E: build_label_map against full v6 source
# ---------------------------------------------------------------------------

class TestBuildLabelMapV6:
    @pytest.fixture(scope="class")
    def label_map(self):
        return build_label_map(V6_DOC_ROOT)

    def test_returns_non_empty_dict(self, label_map):
        assert len(label_map) > 100, f"Expected >100 labels, got {len(label_map)}"

    def test_known_label_present(self, label_map):
        # universal_dao.rst defines this label
        assert "universal_dao" in label_map

    def test_label_maps_to_file_stem(self, label_map):
        assert label_map["universal_dao"] == "universal_dao"

    def test_all_values_are_strings(self, label_map):
        for key, val in label_map.items():
            assert isinstance(key, str) and isinstance(val, str), \
                f"Non-string entry: {key!r} → {val!r}"


# ---------------------------------------------------------------------------
# E2E: collect_asset_refs for mail.rst (known images)
# ---------------------------------------------------------------------------

class TestCollectAssetRefsV6:
    @pytest.fixture(scope="class")
    def mail_refs(self):
        mail_rst = next(V6_DOC_ROOT.rglob("mail.rst"))
        return collect_asset_refs(mail_rst, "mail")

    def test_finds_images(self, mail_refs):
        names = [ref.source_path.name for ref in mail_refs]
        assert "mail_sender_flow.png" in names

    def test_dest_rel_uses_file_id(self, mail_refs):
        dest_rels = [ref.dest_rel for ref in mail_refs]
        assert any(d.startswith("assets/mail/") for d in dest_rels)

    def test_source_paths_exist(self, mail_refs):
        for ref in mail_refs:
            assert ref.source_path.exists(), f"Missing: {ref.source_path}"

    def test_no_duplicates(self, mail_refs):
        dest_rels = [ref.dest_rel for ref in mail_refs]
        assert len(dest_rels) == len(set(dest_rels))


# ---------------------------------------------------------------------------
# E2E: copy_assets integration
# ---------------------------------------------------------------------------

class TestCopyAssetsV6:
    def test_copy_mail_images(self, tmp_path):
        mail_rst = next(V6_DOC_ROOT.rglob("mail.rst"))
        refs = collect_asset_refs(mail_rst, "mail")
        assert refs, "No assets found in mail.rst"

        copied = copy_assets(refs, tmp_path)

        assert len(copied) == len(refs)
        for dest in copied:
            assert dest.exists(), f"Not copied: {dest}"
            assert dest.stat().st_size > 0
