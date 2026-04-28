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
            anchor="my-label",
        )
        assert t.title == "A"
        assert t.file_id == "libraries-foo"
        assert t.section_title == "Usage"
        assert t.category == "libraries"
        # Phase 22-B-16b step 2b: anchor is the label-name slug used in the
        # MD link's ``#anchor`` portion (Sphinx parity).
        assert t.anchor == "my-label"

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

        real = LabelTarget(
            title="", file_id="", section_title="", category="", anchor="",
        )
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
        # Phase 22-B-16b step 2b: anchor is the label name slug, not the
        # heading slug — Sphinx parity.
        assert lt.anchor == "my-label"

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


class TestCommonLayering:
    """F1 regression (review-22-b-16b-step3-4-16c.md): scripts/common/
    modules must not import scripts/create/.  Spec §2-2 independence.
    """

    def test_labels_does_not_import_from_create(self):
        import ast
        from pathlib import Path
        labels_src = Path(
            Path(__file__).resolve().parents[4]
            / "tools/rbkc/scripts/common/labels.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(labels_src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = (node.module or "")
                assert not module.startswith("scripts.create"), (
                    f"common/labels.py imports from {module!r} — "
                    f"spec §2-2 forbids common → create dependency"
                )

    def test_common_file_id_does_not_import_from_create(self):
        import ast
        from pathlib import Path
        src = Path(
            Path(__file__).resolve().parents[4]
            / "tools/rbkc/scripts/common/file_id.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = (node.module or "")
                assert not module.startswith("scripts.create"), (
                    f"common/file_id.py imports from {module!r}"
                )


class TestMDRelativeLinkInsideNestedBlock:
    """F3 regression (review-22-b-16b-step3-4-16c.md): relative MD links
    inside list items / blockquotes must be rewritten too, and any
    dangling-link warnings must propagate to the outer visitor.
    """

    def test_warning_propagates_from_nested_block(self, tmp_path):
        """A relative link inside a list item triggers a warning when
        the target is not in doc_map.  F3 fix ensures the sub-visitor
        forwards its warnings to the parent.
        """
        from scripts.common.md_ast import parse
        from scripts.common.md_ast_visitor import _MDVisitor
        from scripts.common.labels import LabelTarget

        # Non-empty doc_map (at least one unrelated entry) activates the
        # dangling-target path when foo.md isn't found.
        doc_map = {
            "other.md": LabelTarget(
                title="O", file_id="x", section_title="", category="c", type="t"
            )
        }
        text = "- See [Foo](foo.md)\n"
        v = _MDVisitor(doc_map=doc_map, source_path=tmp_path / "x.md")
        v.walk(parse(text))
        assert any("foo.md" in w for w in v.warnings), v.warnings

    def test_rewrite_inside_list_item(self, tmp_path):
        """Positive path: relative link resolves to doc_map even when
        nested in a list item — tests sub-visitor's doc_map propagation.
        """
        from scripts.common.md_ast import parse
        from scripts.common.md_ast_visitor import _MDVisitor
        from scripts.common.labels import LabelTarget

        # Target key matches source-path-parent + href.resolve() suffix.
        source_path = tmp_path / "foo" / "src.md"
        source_path.parent.mkdir(parents=True)
        target = tmp_path / "foo" / "bar.md"
        doc_map = {
            str(target.resolve()).replace("\\", "/").lstrip("/"): LabelTarget(
                title="Bar", file_id="libraries-bar", section_title="",
                category="libraries", type="component",
            )
        }
        text = "- See [Bar](bar.md)\n"
        v = _MDVisitor(doc_map=doc_map, source_path=source_path)
        parts = v.walk(parse(text))
        # Rewritten link must appear in top-level content (the sub-visitor
        # renders the list item content back into the parent).
        assert "../../component/libraries/libraries-bar.md" in parts.content, parts.content


class TestWarningsPropagation:
    """F1 regression guard (spec §3-2-2): visitor warnings about dangling
    links must reach the caller — silent-skip is forbidden.
    """

    def test_normalise_rst_emits_warnings_for_dangling_ref(self):
        from scripts.common.rst_normaliser import normalise_rst

        # Dangling `:ref:` (label not in label_map) must log a WARNING.
        text = "See :ref:`nonexistent`.\n"
        warnings: list = []
        normalise_rst(
            text,
            label_map={},
            doc_map={},
            strict_unknown=True,
            warnings_out=warnings,
        )
        assert any("nonexistent" in w for w in warnings), warnings

    def test_normalise_rst_warnings_out_none_does_not_crash(self):
        """Backward compat: callers that don't care about warnings pass
        ``warnings_out=None`` (or omit it) — normalisation must still run.
        """
        from scripts.common.rst_normaliser import normalise_rst

        text = "See :ref:`nonexistent`.\n"
        # No assertion beyond "doesn't raise" — warnings just get dropped.
        normalise_rst(text, label_map={}, strict_unknown=True)


class TestHeadingTextAnchor:
    """LabelTarget.anchor must equal github_slug(heading_title) — the same
    slug GitHub Web auto-generates for the heading, so ``#anchor`` fragments
    in docs MD resolve correctly on GitHub.

    Spec §3-2-1: anchor is derived from heading text, not the RST label name.
    """

    def test_japanese_heading_anchor(self, tmp_path):
        """Japanese heading → anchor uses lowercased CJK text (GitHub keeps CJK)."""
        from scripts.common.labels import build_label_map
        from scripts.common.github_slug import github_slug

        rst = tmp_path / "x.rst"
        rst.write_text(
            ".. _universal_dao:\n\n"
            "ユニバーサルDAO\n"
            "================\n\n"
            "Body.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("universal_dao")
        assert lt is not None
        assert lt.anchor == github_slug("ユニバーサルDAO"), (
            f"got {lt.anchor!r}, expected {github_slug('ユニバーサルDAO')!r}"
        )

    def test_english_heading_anchor(self, tmp_path):
        """ASCII heading → anchor is lowercased with spaces replaced by hyphens."""
        from scripts.common.labels import build_label_map
        from scripts.common.github_slug import github_slug

        rst = tmp_path / "x.rst"
        rst.write_text(
            ".. _universal_dao_overview:\n\n"
            "Universal DAO\n"
            "=============\n\n"
            "Body.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("universal_dao_overview")
        assert lt is not None
        assert lt.anchor == github_slug("Universal DAO"), (
            f"got {lt.anchor!r}, expected {github_slug('Universal DAO')!r}"
        )

    def test_anchor_differs_from_label_slug_for_japanese(self, tmp_path):
        """Confirm the new behaviour: anchor is NOT the RST label slug.

        Previously anchor = github_slug(label.replace('_', '-')) which would
        give 'universal-dao' for label 'universal_dao'.  The heading 'ユニバーサルDAO'
        should instead yield 'ユニバーサルdao'.
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "x.rst"
        rst.write_text(
            ".. _universal_dao:\n\n"
            "ユニバーサルDAO\n"
            "================\n\n"
            "Body.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("universal_dao")
        assert lt is not None
        # New: title-based slug
        assert lt.anchor == "ユニバーサルdao", f"got {lt.anchor!r}"
        # Confirm it is NOT the old label-based slug
        assert lt.anchor != "universal-dao", (
            "anchor must be heading-text-based, not RST-label-based"
        )

    def test_enclosing_section_anchor(self, tmp_path):
        """Label not directly before heading resolves to enclosing section title."""
        from scripts.common.labels import build_label_map
        from scripts.common.github_slug import github_slug

        rst = tmp_path / "x.rst"
        rst.write_text(
            "親セクション\n"
            "============\n\n"
            "本文。\n\n"
            " .. _nested_orphan:\n\n"
            " block_quote 内の段落\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("nested_orphan")
        assert lt is not None
        assert lt.anchor == github_slug("親セクション"), (
            f"got {lt.anchor!r}, expected {github_slug('親セクション')!r}"
        )

    def test_build_label_doc_map_anchor_is_title_based(self, tmp_path):
        """build_label_doc_map must also use heading-text anchor (not label slug)."""
        from scripts.common.labels import build_label_doc_map
        from scripts.common.github_slug import github_slug

        src_root = (
            tmp_path / ".lw/nab-official/v6/nablarch-document/ja/"
            "application_framework/application_framework/libraries/foo"
        )
        src_root.mkdir(parents=True)
        (src_root / "index.rst").write_text(
            ".. _my_label:\n\n"
            "日本語の見出し\n"
            "==============\n\n"
            "Body.\n",
            encoding="utf-8",
        )

        mappings_dir = tmp_path / "tools/rbkc/mappings"
        mappings_dir.mkdir(parents=True)
        (mappings_dir / "v6.json").write_text(
            '{"rst":[{"pattern":"application_framework/application_framework/libraries/",'
            '"type":"component","category":"libraries"}],"md":{},"xlsx":{},"xlsx_patterns":[]}',
            encoding="utf-8",
        )

        label_map, _ = build_label_doc_map("6", tmp_path)

        lt = label_map.get("my_label")
        assert lt is not None
        assert lt.anchor == github_slug("日本語の見出し"), (
            f"got {lt.anchor!r}, expected {github_slug('日本語の見出し')!r}"
        )
        assert lt.anchor != "my-label", "anchor must not be the RST label slug"


class TestEnclosingSectionResolution:
    """Orphan labels (declared but not followed by a heading) resolve to
    the enclosing section's heading — matching Sphinx's default anchor
    behaviour.  Only labels that appear before any heading in the file
    remain UNRESOLVED.
    """

    def test_label_inside_block_quote_resolves_to_enclosing_section(self, tmp_path):
        """A label nested inside a block_quote under a section must
        resolve to that section's title (not to UNRESOLVED).
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "big_picture.rst"
        rst.write_text(
            "様々な処理方式に対応できる\n"
            "============================\n\n"
            "本文。\n\n"
            " .. _runtime_platform:\n\n"
            " 実行制御基盤\n"
            "  * :ref:`web_application`\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)

        assert "runtime_platform" in m
        lt = m["runtime_platform"]
        assert isinstance(lt, LabelTarget)
        assert lt.title == "様々な処理方式に対応できる"
        assert lt.section_title == "様々な処理方式に対応できる"

    def test_label_before_any_heading_remains_unresolved(self, tmp_path):
        """A label that appears before the first heading in a file has no
        enclosing section — it stays UNRESOLVED.
        """
        from scripts.common.labels import build_label_map, UNRESOLVED

        rst = tmp_path / "orphan_first.rst"
        rst.write_text(
            ".. _top_level_orphan:\n\n"
            "Some paragraph that is not a heading.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)

        assert m.get("top_level_orphan") is UNRESOLVED

    def test_label_in_subsection_resolves_to_subsection_not_parent(self, tmp_path):
        """Enclosing section is the *innermost* enclosing heading — when a
        label is under h3, it resolves to the h3 title, not the h2 parent.
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "nested.rst"
        rst.write_text(
            "親セクション\n"
            "============\n\n"
            "親の本文。\n\n"
            "子セクション\n"
            "-------------\n\n"
            "子の本文。\n\n"
            " .. _nested_orphan:\n\n"
            " block_quote 内の段落\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)

        lt = m.get("nested_orphan")
        assert lt is not None
        assert lt.title == "子セクション"
        assert lt.section_title == "子セクション"

    def test_label_directly_before_heading_still_wins(self, tmp_path):
        """When a label *is* directly followed by a heading, the heading
        (not the outer enclosing section) is the target — the existing
        behaviour must not regress.
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "direct.rst"
        rst.write_text(
            "親セクション\n"
            "============\n\n"
            "親の本文。\n\n"
            ".. _direct_label:\n\n"
            "直接の見出し\n"
            "--------------\n\n"
            "本文。\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)

        lt = m.get("direct_label")
        assert lt is not None
        assert lt.title == "直接の見出し"


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
