"""Unit tests for ``scripts.common.labels`` Phase 22-B-16b extensions:

- :class:`LabelTarget` dataclass
- :data:`UNRESOLVED` as a ``LabelTarget`` singleton (identity-compared)
- :func:`build_label_doc_map` returning ``(label_map, doc_map)`` for a
  whole version at once, with ``file_id`` / ``category`` resolved via
  :func:`scripts.common.file_id.derive_file_id`.

Oracle is spec-pinned: every assertion is derivable from the mapping file
(``mappings/v{N}.json``) plus the documented naming rules, not from the
current output of ``classify_sources``.
"""
from __future__ import annotations

import textwrap
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


class TestLabelTargetDataclass:
    def test_fields_and_frozen(self):
        from scripts.common.labels import LabelTarget

        t = LabelTarget(
            title="A", file_id="libraries-foo",
            section_title="Usage", category="libraries",
        )
        assert t.title == "A"
        assert t.file_id == "libraries-foo"
        assert t.section_title == "Usage"
        assert t.category == "libraries"

        # frozen: assignment must raise
        import dataclasses
        assert dataclasses.is_dataclass(t) and dataclasses.fields(t)
        try:
            t.title = "B"  # type: ignore[misc]
        except Exception:
            return
        raise AssertionError("LabelTarget must be frozen")


class TestUnresolvedSingleton:
    def test_unresolved_is_labeltarget_singleton(self):
        from scripts.common.labels import LabelTarget, UNRESOLVED

        assert isinstance(UNRESOLVED, LabelTarget)

        from scripts.common.labels import UNRESOLVED as U2
        assert U2 is UNRESOLVED  # singleton identity

    def test_unresolved_identity_distinguishes_from_real_target(self):
        from scripts.common.labels import LabelTarget, UNRESOLVED

        real = LabelTarget(title="", file_id="", section_title="", category="")
        # Even a value-equal LabelTarget is NOT the sentinel
        assert real is not UNRESOLVED


class TestBuildLabelDocMap:
    """Integration-ish test: build a small RST tree and check label+doc maps."""

    def test_label_map_resolves_to_labeltarget_with_file_id(self, tmp_path, monkeypatch):
        """Label declared in an RST file that maps to category=libraries
        must resolve to a LabelTarget with file_id='libraries-foo',
        category='libraries', section_title='Usage'.
        """
        from scripts.common.labels import build_label_doc_map, LabelTarget

        # Build a fake repo tree mirroring v6 layout
        src_root = (
            tmp_path / ".lw/nab-official/v6/nablarch-document/ja/"
            "application_framework/application_framework/libraries/foo"
        )
        src_root.mkdir(parents=True)
        (src_root / "index.rst").write_text(textwrap.dedent("""\
            .. _my-label:

            Usage
            =====

            Body.
            """), encoding="utf-8")

        # Minimal mappings file
        mappings_dir = tmp_path / "tools/rbkc/mappings"
        mappings_dir.mkdir(parents=True)
        (mappings_dir / "v6.json").write_text(
            '{"rst":[{"pattern":"application_framework/application_framework/libraries/",'
            '"type":"component","category":"libraries"}],"md":{},"xlsx":{},"xlsx_patterns":[]}',
            encoding="utf-8",
        )

        label_map, doc_map = build_label_doc_map("6", tmp_path)

        assert "my-label" in label_map
        lt = label_map["my-label"]
        assert isinstance(lt, LabelTarget)
        assert lt.title == "Usage"
        assert lt.section_title == "Usage"
        assert lt.category == "libraries"
        assert lt.file_id == "libraries-foo"

    def test_orphan_label_stamped_with_unresolved_sentinel(self, tmp_path):
        """Label declared but not followed by a heading must map to
        UNRESOLVED (not dropped). Preserves 22-B-16a horizontal-class fix.
        """
        from scripts.common.labels import build_label_doc_map, UNRESOLVED

        src_root = (
            tmp_path / ".lw/nab-official/v6/nablarch-document/ja/"
            "application_framework/application_framework/libraries/foo"
        )
        src_root.mkdir(parents=True)
        # Label at end of file with no heading following
        (src_root / "index.rst").write_text(".. _orphan-label:\n", encoding="utf-8")

        mappings_dir = tmp_path / "tools/rbkc/mappings"
        mappings_dir.mkdir(parents=True)
        (mappings_dir / "v6.json").write_text(
            '{"rst":[{"pattern":"application_framework/application_framework/libraries/",'
            '"type":"component","category":"libraries"}],"md":{},"xlsx":{},"xlsx_patterns":[]}',
            encoding="utf-8",
        )

        label_map, _ = build_label_doc_map("6", tmp_path)

        assert label_map.get("orphan-label") is UNRESOLVED

    def test_doc_map_keyed_by_relpath_returns_labeltarget(self, tmp_path):
        """doc_map maps rst relpath (relative to the matched source root) to
        LabelTarget with the document's title + file_id. `section_title` is
        '' for document-level entries.
        """
        from scripts.common.labels import build_label_doc_map, LabelTarget

        src_root = (
            tmp_path / ".lw/nab-official/v6/nablarch-document/ja/"
            "application_framework/application_framework/libraries/foo"
        )
        src_root.mkdir(parents=True)
        (src_root / "index.rst").write_text(textwrap.dedent("""\
            Document Title
            ==============

            Body.
            """), encoding="utf-8")

        mappings_dir = tmp_path / "tools/rbkc/mappings"
        mappings_dir.mkdir(parents=True)
        (mappings_dir / "v6.json").write_text(
            '{"rst":[{"pattern":"application_framework/application_framework/libraries/",'
            '"type":"component","category":"libraries"}],"md":{},"xlsx":{},"xlsx_patterns":[]}',
            encoding="utf-8",
        )

        _, doc_map = build_label_doc_map("6", tmp_path)

        # doc_map key: relpath relative to the matched source root marker.
        # For v6 this is the path after "nablarch-document/ja/".
        key = "application_framework/application_framework/libraries/foo/index.rst"
        assert key in doc_map
        lt = doc_map[key]
        assert isinstance(lt, LabelTarget)
        assert lt.title == "Document Title"
        assert lt.file_id == "libraries-foo"
        assert lt.category == "libraries"
        assert lt.section_title == ""


class TestBuildLabelMapBackwardCompat:
    """The old ``build_label_map(source_dir) -> dict[label, str|UNRESOLVED]``
    must keep working so downstream callers that haven't migrated keep going.
    But the returned values are now LabelTargets (or UNRESOLVED singleton)
    — callers that used ``.title`` via ``getattr`` keep working; callers
    that expected a bare ``str`` title need to read ``.title``."""

    def test_build_label_map_returns_labeltarget(self, tmp_path):
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "x.rst"
        rst.write_text(textwrap.dedent("""\
            .. _foo:

            Heading
            =======
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "foo" in m
        v = m["foo"]
        # Must expose .title for cross-doc consumers
        assert isinstance(v, LabelTarget)
        assert v.title == "Heading"
        assert v.section_title == "Heading"
        # No file_id available in single-dir mode
        assert v.file_id == ""
        assert v.category == ""
