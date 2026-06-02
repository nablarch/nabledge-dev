"""Round-trip tests for scripts.common.linkfmt.

F4 fix (review-22-b-16b-step3-4-16c.md): the emit function and the
parsing regex live in one module and must be provably consistent.
These tests assert that for every ``(display, type, cat, file_id, anchor)``
tuple, ``CROSSDOC_LINK_RE.search(emit_crossdoc_link(...))`` recovers
the same type/category/file_id/anchor.  If emit and regex drift, this
test fails.
"""
from __future__ import annotations

import re

import pytest


CASES = [
    # (display, type_, category, file_id, anchor)
    ("Foo", "component", "libraries", "libraries-foo", ""),
    ("Anchor", "component", "libraries", "libraries-foo", "usage"),
    ("jp 日本語", "about", "migration", "migration-migration", ""),
    ("multi", "development-tools", "testing-framework", "testing-framework-real", ""),
    ("underscore label", "processing-pattern", "nablarch-batch",
     "nablarch-batch-overview", "my-label"),
    ("hyphened", "component", "adapters", "adapters-doma-adaptor", "section-1"),
]


class TestCrossDocRoundTrip:
    @pytest.mark.parametrize("case", CASES)
    def test_emit_then_parse(self, case):
        from scripts.common.linkfmt import emit_crossdoc_link, CROSSDOC_LINK_RE

        display, type_, category, file_id, anchor = case
        link = emit_crossdoc_link(display, type_, category, file_id, anchor)

        m = CROSSDOC_LINK_RE.search(link)
        assert m is not None, link
        assert m.group("type") == type_, link
        assert m.group("category") == category, link
        assert m.group("file_id") == file_id, link
        assert (m.group("anchor") or "") == anchor, link

    def test_anchored_and_bare_differ_only_by_fragment(self):
        from scripts.common.linkfmt import emit_crossdoc_link

        bare = emit_crossdoc_link("D", "t", "c", "fid")
        anchored = emit_crossdoc_link("D", "t", "c", "fid", "a")
        assert bare.endswith(".json)")
        assert anchored.endswith(".json#a)")
        assert bare + "#a" not in anchored  # different closing paren placement

    def test_crossdoc_link_uses_json_extension(self):
        from scripts.common.linkfmt import emit_crossdoc_link

        link = emit_crossdoc_link("Foo", "component", "libraries", "libraries-foo")
        assert ".json" in link
        assert ".md" not in link

    def test_crossdoc_link_re_matches_json_extension(self):
        from scripts.common.linkfmt import CROSSDOC_LINK_RE

        json_link = "[Foo](../../component/libraries/libraries-foo.json)"
        m = CROSSDOC_LINK_RE.search(json_link)
        assert m is not None, f"CROSSDOC_LINK_RE must match .json links: {json_link}"
        assert m.group("file_id") == "libraries-foo"

    def test_crossdoc_link_re_matches_json_with_anchor(self):
        from scripts.common.linkfmt import CROSSDOC_LINK_RE

        json_link = "[Foo](../../component/libraries/libraries-foo.json#section)"
        m = CROSSDOC_LINK_RE.search(json_link)
        assert m is not None
        assert m.group("anchor") == "section"


class TestJavadocRoundTrip:
    def test_emit_javadoc_link_basic(self):
        from scripts.common.linkfmt import emit_javadoc_link

        result = emit_javadoc_link(
            "UniversalDao", "javadoc-nablarch-common-dao-UniversalDao"
        )
        assert result == "[UniversalDao](../javadoc/javadoc-nablarch-common-dao-UniversalDao.json)"

    def test_emit_javadoc_link_various(self):
        from scripts.common.linkfmt import emit_javadoc_link

        assert emit_javadoc_link("Foo", "javadoc-x-Foo") == "[Foo](../javadoc/javadoc-x-Foo.json)"
        assert emit_javadoc_link("日本語", "javadoc-y-Bar") == "[日本語](../javadoc/javadoc-y-Bar.json)"

    def test_emit_javadoc_link_uses_json_extension(self):
        from scripts.common.linkfmt import emit_javadoc_link

        link = emit_javadoc_link("SomeClass", "javadoc-com-example-SomeClass")
        assert ".json" in link
        assert ".md" not in link

    def test_javadoc_link_re_matches_json_extension(self):
        from scripts.common.linkfmt import JAVADOC_LINK_RE

        json_link = "[Foo](../javadoc/javadoc-x-Foo.json)"
        m = JAVADOC_LINK_RE.search(json_link)
        assert m is not None, f"JAVADOC_LINK_RE must match .json links: {json_link}"
        assert m.group("file_id") == "javadoc-x-Foo"

    def test_javadoc_link_re_detects_emit_output(self):
        from scripts.common.linkfmt import emit_javadoc_link, JAVADOC_LINK_RE

        file_id = "javadoc-nablarch-common-dao-UniversalDao"
        link = emit_javadoc_link("UniversalDao", file_id)
        m = JAVADOC_LINK_RE.search(link)
        assert m is not None, f"JAVADOC_LINK_RE did not match: {link}"
        assert m.group("file_id") == file_id

    def test_javadoc_link_re_round_trip(self):
        from scripts.common.linkfmt import emit_javadoc_link, JAVADOC_LINK_RE

        cases = [
            ("ClassA", "javadoc-com-example-ClassA"),
            ("SomeClass", "javadoc-nablarch-core-SomeClass"),
        ]
        for display, file_id in cases:
            link = emit_javadoc_link(display, file_id)
            m = JAVADOC_LINK_RE.search(link)
            assert m is not None, link
            assert m.group("file_id") == file_id


class TestAssetRoundTrip:
    @pytest.mark.parametrize(
        "case",
        [
            ("alt", "libraries-foo", "bar.png"),
            ("", "handlers-x", "图.svg"),
            ("text with spaces", "adapters-y", "file.pdf"),
        ],
    )
    def test_emit_then_parse(self, case):
        from scripts.common.linkfmt import emit_asset_link, ASSET_LINK_RE

        display, file_id, basename = case
        link = emit_asset_link(display, file_id, basename)

        m = ASSET_LINK_RE.search(link)
        assert m is not None, link
        assert m.group("file_id") == file_id
        assert m.group("basename") == basename
