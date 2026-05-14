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
        category='libraries'.

        section_title is '' for h1-direct labels (spec §3-2-3: h1 maps to
        JSON title field, not sections[] — verify skips the JSON section check).
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
        # h1-direct label: section_title="" because h1 maps to JSON title field
        # (not sections[]), so verify §3-2-3 skips the JSON section check.
        assert lt.section_title == ""
        assert lt.category == "libraries"
        assert lt.file_id == "libraries-foo"
        # Issue #316: anchor is github_slug(heading_title), not label name slug.
        assert lt.anchor == "usage"

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

        When the enclosing section is h1, section_title="" (h1 maps to JSON
        title field, not sections[]).  This test verifies the label is not
        dropped (UNRESOLVED) and that title is the h1 heading text.
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
        # Enclosing section is h1 → section_title="" (h1 is not in JSON sections[]).
        assert lt.section_title == ""

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


class TestScanRstLabelsDocutilsAST:
    """Task 17: _scan_rst_labels must use docutils AST — not ad-hoc regex line scan.

    Three correctness properties that the old line-scanner violated:

    1. h1-direct label (label immediately before h1): parent=document in docutils AST
       → section_title must be "" (not the h1 heading text).
       The old scanner returned the h1 title, which caused 692 QL1 FAILs because
       verify.py §3-2-3 checks section_title against JSON sections[].title.

    2. section-inner label (label before sub-heading, under a parent section):
       parent=section whose first child is the enclosing section's title.
       → section_title must be the *enclosing* section title (not the sub-heading).

    3. Non-RST chars (e.g. '-->') must NOT be treated as heading underlines.
       The old _is_heading_underline() accepted any mix of _RST_HEADING_CHARS,
       which includes '>' — so '-->' triggered the overline-style heading path
       and corrupted section_title for 9 labels.
    """

    def test_h1_direct_label_gives_empty_section_title(self, tmp_path):
        """Label immediately before h1 → section_title='' (docutils: parent=document).

        This is the §3-2-3 fix for the 692-count QL1 'section_title not found'
        failures: section_title="" means verify skips the section check.
        """
        from scripts.common.labels import build_label_map, UNRESOLVED

        rst = tmp_path / "x.rst"
        rst.write_text(
            ".. _universal_dao:\n\n"
            "ユニバーサルDAO\n"
            "================\n\n"
            "本文。\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("universal_dao")

        assert lt is not None
        assert lt is not UNRESOLVED
        assert lt.title == "ユニバーサルDAO"
        # KEY assertion: h1-direct label → section_title must be "" so that
        # verify.py skips the section check (no JSON section can have title=="").
        assert lt.section_title == "", (
            f"h1-direct label must have section_title='', got {lt.section_title!r}"
        )

    def test_section_inner_label_gives_enclosing_section_title(self, tmp_path):
        """Label under an h2 section (not directly before any deeper heading)
        → section_title = enclosing h2 title.

        For h1-scope labels, section_title is "" (h1 maps to JSON title field,
        not sections[]). This test uses an h2 to confirm the h2+ case.
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "x.rst"
        rst.write_text(
            "ドキュメントタイトル\n"
            "====================\n\n"
            "h1 本文。\n\n"
            "ユニバーサルDAO\n"
            "----------------\n\n"
            "h2 本文。\n\n"
            ".. _inner_label:\n\n"
            "Some paragraph inside the h2 section.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("inner_label")

        assert lt is not None
        # Label is inside h2 "ユニバーサルDAO" (not h1) → section_title = h2 title
        assert lt.section_title == "ユニバーサルDAO"

    def test_jsp_comment_arrow_does_not_corrupt_section_title(self, tmp_path):
        """'-->' (JSP comment end) between a label and an h2 heading must NOT be
        treated as a heading underline.  The old _is_heading_underline accepted '>'
        from _RST_HEADING_CHARS — this test pins the correct docutils-parity behaviour.

        RST layout mirrors the actual tag.rst pattern:
        - h1 section "タグライブラリ"
          - h2 section "二重サブミットを防ぐ"
            - label tag-double_submission_server_side
            - text with '-->'
            - h3 section "サーバ側の二重サブミット防止"
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "tag.rst"
        rst.write_text(
            "タグライブラリ\n"
            "==============\n\n"
            "本文。\n\n"
            "二重サブミットを防ぐ\n"
            "--------------------\n\n"
            "説明。\n\n"
            ".. _tag-double_submission_server_side:\n\n"
            "-->はJSPコメント終端ではない。\n\n"
            "サーバ側の二重サブミット防止\n"
            "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n"
            "本文2。\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)
        lt = m.get("tag-double_submission_server_side")

        assert lt is not None
        # The label is inside h2 "二重サブミットを防ぐ", not before h3.
        # '-->' must NOT have been treated as a heading underline that
        # corrupted section_title to something like 'はJSPコメント終端ではない。'.
        assert lt.section_title == "二重サブミットを防ぐ", (
            f"Expected '二重サブミットを防ぐ', got {lt.section_title!r}. "
            "'-->' (or similar non-RST chars) must not be treated as a heading underline."
        )
        assert lt.title == "二重サブミットを防ぐ"

    def test_label_before_subheading_resolves_to_subheading_title(self, tmp_path):
        """Label immediately before a sub-heading → section_title = sub-heading title
        (same behaviour as the old scanner for this case — must not regress).
        """
        from scripts.common.labels import build_label_map

        rst = tmp_path / "x.rst"
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
        assert lt.section_title == "直接の見出し"


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
        # h1-direct label: section_title="" (h1 maps to JSON title field, not
        # sections[], so verify §3-2-3 section check is skipped).
        assert v.section_title == ""
        # No file_id available in single-dir mode
        assert v.file_id == ""


class TestCaseInsensitiveLabelLookup:
    """Bug 1 fix: docutils normalises label names to lowercase in names[].

    build_label_map / build_label_doc_map keys are therefore lowercase.
    Callers (rst_ast_visitor, verify) must look up labels with .lower()
    to avoid UNRESOLVED → plain-text fallback on mixed-case labels like
    ``NablarchServletContextListener`` or ``guide_appendix_windowScope``.
    """

    def test_mixed_case_label_stored_as_lowercase_key(self, tmp_path):
        """docutils normalises names[] to lowercase → map key is lowercase."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "x.rst"
        rst.write_text(textwrap.dedent("""\
            .. _NablarchServletContextListener:

            NablarchServletContextListener
            ================================

            Body.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        # Key must be lowercase (docutils normalisation)
        assert "nablarchservletcontextlistener" in m
        # Original-case key must NOT be present
        assert "NablarchServletContextListener" not in m

    def test_caller_must_lowercase_before_lookup(self, tmp_path):
        """rst_ast_visitor / verify must call label_map.get(label.lower()).

        This test pins the required caller behaviour: looking up the
        original-case label name returns None (miss); lowercased lookup
        returns the correct LabelTarget.
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "y.rst"
        rst.write_text(textwrap.dedent("""\
            .. _SqlLog:

            SqlLog
            ======

            Body.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        # Caller with original case → miss (current bug behaviour to be fixed)
        assert m.get("SqlLog") is None
        # Caller with .lower() → hit (required behaviour after fix)
        v = m.get("SqlLog".lower())
        assert isinstance(v, LabelTarget)
        assert v.title == "SqlLog"

    def test_underscore_label_with_uppercase_chars(self, tmp_path):
        """Labels like ``guide_appendix_windowScope`` are stored lowercase."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "z.rst"
        rst.write_text(textwrap.dedent("""\
            .. _guide_appendix_windowScope:

            Window Scope
            ============

            Body.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "guide_appendix_windowscope" in m
        assert "guide_appendix_windowScope" not in m
        v = m.get("guide_appendix_windowScope".lower())
        assert isinstance(v, LabelTarget)
        assert v.title == "Window Scope"
        assert v.category == ""


class TestNextSectionMultiLevelClimb:
    """Bug 2 fix: _next_section_for_node must climb multiple levels.

    Pattern: a label is the last item inside a deeply-nested section, but
    the *next* section (the label's intended target) is a sibling of an
    ancestor, not a direct sibling or immediate grandparent sibling.

    Real example: v1.2 01_Log.rst
    - section ``要求`` (h2)
      - section ``未検討`` (h3)
        - bullet_list
        - ``.. _Log_LoggerProcess:``   ← target node, last in ``未検討``
    - section ``ログ出力要求受付処理`` (h2, sibling of ``要求``)

    One-level climb (grandparent = ``要求``) finds no next sibling.
    Two-level climb (great-grandparent) finds ``ログ出力要求受付処理``.
    """

    def test_label_at_3level_nesting_end_resolves_to_ancestor_sibling(self, tmp_path):
        """Label at the end of a 3-deep nest resolves to a section 2 levels up."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "deep.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Outer
            -----

            Inner
            ~~~~~

            Body text.

            .. _deep-label:

            Next Section
            ------------

            Content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "deep-label" in m
        v = m["deep-label"]
        assert isinstance(v, LabelTarget)
        # Must resolve to the section it directly precedes, not the enclosing one
        assert v.title == "Next Section", (
            f"Expected 'Next Section' but got {v.title!r} — "
            "multi-level climb not implemented"
        )

    def test_label_at_4level_nesting_end_resolves_correctly(self, tmp_path):
        """Label at the end of a 4-deep nest resolves to the correct ancestor sibling."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "deep4.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            L2
            --

            L3
            ~~

            L4
            ^^

            Body.

            .. _target-label:

            Next L2
            -------

            More content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "target-label" in m
        v = m["target-label"]
        assert isinstance(v, LabelTarget)
        assert v.title == "Next L2", (
            f"Expected 'Next L2' but got {v.title!r} — "
            "multi-level climb stops too early"
        )


class TestNextSectionTransitionSkip:
    """Issue #320: label directly before a transition resolves to the section
    after the transition.

    Real example: v1.2/v1.3/v1.4 architectural_pattern/concept.rst
      .. _method_binding:
      ++++++++++++          ← transition
      .. _request_processing:
      リクエストの識別と業務処理の実行  ← correct target

    Sphinx PropagateTargets moves the label id past the transition because
    transition cannot hold an HTML id.
    """

    def test_label_before_transition_then_section(self, tmp_path):
        """Label followed by transition then section resolves to that section."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "transition.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            First Section
            -------------

            Body text.

            .. _method_binding:

            +++++++++++++++

            Second Section
            --------------

            Content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "method_binding" in m
        v = m["method_binding"]
        assert isinstance(v, LabelTarget)
        assert v.title == "Second Section", (
            f"Expected 'Second Section' but got {v.title!r} — "
            "transition node must be skipped when searching for next section"
        )


class TestNextSectionLineBlockSkip:
    """Issue #320 Task 25: label separated from next section by a line_block (``|``)
    must still resolve to that section.

    Real example: v5/v6 biz_samples/03/index.rst
      .. _ListSearchResult_Structure:

      |

      ------------
      構成
      ------------
    """

    def test_label_before_line_block_then_section(self, tmp_path):
        """Label followed by line_block then section resolves to that section."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "line_block.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            First Section
            -------------

            Body text.

            .. _list_structure:

            |

            Second Section
            --------------

            Content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "list_structure" in m
        v = m["list_structure"]
        assert isinstance(v, LabelTarget)
        assert v.title == "Second Section", (
            f"Expected 'Second Section' but got {v.title!r} — "
            "line_block node must be skipped when searching for next section"
        )


class TestParagraphAnchorTitleResolution:
    """Issue #320 Task 25: anchors directly before a paragraph (non-heading)
    must resolve to a title derived from the paragraph text, not fall back
    to the enclosing section.

    Real examples from RST sources:
    - ``**標準ハンドラ構成** (説明文...)`` → ``標準ハンドラ構成``  (bold-start)
    - ``**用語**``                          → ``用語``              (bold-only)
    - ``*クラス名*``                        → ``クラス名``          (italic-only)
    - ``plain text``                        → enclosing section     (excluded — only explicit markup signals heading use)

    h1-scoped anchors (file has only h1, no h2+) always fall back to enclosing section
    even for bold/italic paragraphs, because DocTitle-promoted structure has no
    _walk_section call and no synthetic section is generated.
    """

    def test_bold_only_paragraph(self, tmp_path):
        """``**Term**`` paragraph → title = 'Term'."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "bold_only.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Section
            -------

            .. _my_anchor:

            **用語**

            Definition text here.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "my_anchor" in m
        v = m["my_anchor"]
        assert isinstance(v, LabelTarget)
        assert v.title == "用語", (
            f"Expected '用語' but got {v.title!r} — "
            "bold-only paragraph should be resolved as title"
        )
        assert v.section_title == "用語"

    def test_italic_only_paragraph(self, tmp_path):
        """``*ClassName*`` paragraph → title = 'ClassName'."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "italic_only.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Section
            -------

            .. _my_anchor:

            *ClassName*

            Description text.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "my_anchor" in m
        v = m["my_anchor"]
        assert isinstance(v, LabelTarget)
        assert v.title == "ClassName", (
            f"Expected 'ClassName' but got {v.title!r} — "
            "italic-only paragraph should be resolved as title"
        )

    def test_bold_start_paragraph(self, tmp_path):
        """``**Term** (extra text)`` paragraph → title = 'Term'."""
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "bold_start.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Section
            -------

            .. _my_anchor:

            **標準ハンドラ構成** (説明文をクリックすると詳細が表示されます。)

            Content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "my_anchor" in m
        v = m["my_anchor"]
        assert isinstance(v, LabelTarget)
        assert v.title == "標準ハンドラ構成", (
            f"Expected '標準ハンドラ構成' but got {v.title!r} — "
            "bold-start paragraph should use bold portion as title"
        )

    def test_plain_text_paragraph_falls_back_to_enclosing(self, tmp_path):
        """Plain text paragraph (no inline markup) falls back to enclosing section.

        Only bold/italic-marked paragraphs signal intentional heading use.
        A plain paragraph is regular body text that should not override the
        enclosing section title.
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "plain_text.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Section
            -------

            .. _my_anchor:

            リクエスト単体テスト

            Body.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "my_anchor" in m
        v = m["my_anchor"]
        assert isinstance(v, LabelTarget)
        assert v.title == "Section", (
            f"Expected 'Section' (enclosing) but got {v.title!r} — "
            "plain-text paragraph must not override enclosing section title"
        )

    def test_h1_scope_bold_paragraph_falls_back_to_h1(self, tmp_path):
        """In h1-scoped files (only h1, no h2+), bold paragraph after anchor
        must NOT create a synthetic section — falls back to h1 title.

        Guard: h1-scoped files use DocTitle-promoted structure where
        _walk_section is never called, so no synthetic section would be
        generated and the anchor would not exist in docs MD.
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "h1_scope.rst"
        rst.write_text(textwrap.dedent("""\
            H1 Title
            ========

            Body text.

            .. _my_anchor:

            **Bold Heading**

            Content.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "my_anchor" in m
        v = m["my_anchor"]
        assert isinstance(v, LabelTarget)
        # h1-scope: section_title must be "" (h1 maps to JSON title, not sections[])
        assert v.section_title == "", (
            f"Expected section_title='' (h1 scope) but got {v.section_title!r} — "
            "h1-scoped bold paragraph must not set section_title to para_title"
        )
        # Title may be the para_title or h1 title — the key constraint is section_title=""
        # which prevents verify from looking up the synthetic section in JSON sections[].

    def test_letter_paren_paragraph(self, tmp_path):
        """``e) SQL文のロードクラス`` paragraph (backslash-escaped letter + ')') → title = text.

        Real example from v1.x 04_Statement.rst:
            .. _sql-load-class-label:

            \\e) SQL文のロードクラス

        Docutils strips the backslash and parses as plain paragraph 'e) SQL文…'.
        This Nablarch 1.x convention (a)/b)/c)… subsection list) is a structural
        pattern — not arbitrary body text — and must be treated as heading.
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "letter_paren.rst"
        rst.write_text(textwrap.dedent("""\
            Title
            =====

            Section
            -------

            .. _sql-load-class-label:

            \\e) SQL文のロードクラス

            BasicSqlLoader description.
            """), encoding="utf-8")

        m = build_label_map(tmp_path)

        assert "sql-load-class-label" in m
        v = m["sql-load-class-label"]
        assert isinstance(v, LabelTarget)
        assert v.title == "e) SQL文のロードクラス", (
            f"Expected 'e) SQL文のロードクラス' but got {v.title!r} — "
            "letter+paren paragraph must resolve as title"
        )
        assert v.section_title == "e) SQL文のロードクラス"

    def test_digit_paren_paragraph(self, tmp_path):
        r"""``\2) Formクラスの精査処理実装`` paragraph (backslash + digit + ')') → title = text.

        Real example from v1.2 guide/05_create_form.rst:
            .. _form_validation:

            \2) Formクラスの精査処理実装

        Docutils strips the backslash and parses as plain paragraph '2) Formクラス…'.
        Without the backslash, docutils would treat '2) text' as an enumerated list.
        """
        from scripts.common.labels import build_label_map, LabelTarget

        rst = tmp_path / "digit_paren.rst"
        # Use raw string so \2 is written literally to the file (backslash + 2)
        rst.write_text(
            "Title\n=====\n\nSection\n-------\n\n.. _form_validation:\n\n"
            "\\2) Formクラスの精査処理実装\n\nContent.\n",
            encoding="utf-8",
        )

        m = build_label_map(tmp_path)

        assert "form_validation" in m
        v = m["form_validation"]
        assert isinstance(v, LabelTarget)
        assert v.title == "2) Formクラスの精査処理実装", (
            f"Expected '2) Formクラスの精査処理実装' but got {v.title!r} — "
            "digit+paren paragraph must resolve as title"
        )
        assert v.section_title == "2) Formクラスの精査処理実装"
