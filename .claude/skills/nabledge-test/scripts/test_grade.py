#!/usr/bin/env python3
"""Unit tests for grade.py.

Covers the regressions found in the ad-hoc grade_v6.py drift:
- Section heading regex must match the FIRST heading even if the section text
  doesn't start with '\n' (the "\n" prefix in the pattern broke this).
- "Nablarch Framework Usage" detection must be heading-strict. A keyword that
  appears only in the body (but not in a ###/#### heading) must NOT be detected.
- Detection rules must NOT fall back to "text present in section" when the
  rule is heading-scoped.

Run: python -m unittest .claude/skills/nabledge-test/scripts/test_grade.py
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from grade import grade_ca, grade_qa, _extract_section, _headings, _mermaid_blocks


# -----------------------------------------------------------------------------
# Low-level helpers
# -----------------------------------------------------------------------------

class ExtractSectionTest(unittest.TestCase):
    def test_matches_when_section_is_at_start_of_text(self):
        # First heading with no preceding newline: must still match.
        text = "## Overview\nBody text here\n## Other\n"
        got = _extract_section(text, [r"\n##\s+Overview\s*\n"])
        self.assertIn("Body text here", got)

    def test_matches_when_section_has_preceding_newline(self):
        text = "# Top\n\n## Overview\nBody\n## Next\n"
        got = _extract_section(text, [r"\n##\s+Overview\s*\n"])
        self.assertIn("Body", got)
        self.assertNotIn("Next", got)

    def test_stops_at_same_level_heading(self):
        text = "\n## A\nbody-a\n## B\nbody-b\n"
        got = _extract_section(text, [r"\n##\s+A\s*\n"])
        self.assertIn("body-a", got)
        self.assertNotIn("body-b", got)

    def test_nu_stop_pattern_ignores_deeper_headings(self):
        text = "\n## Nablarch Framework Usage\n### Foo\nfoo-body\n#### Deep\ndeep-body\n## Next\n"
        got = _extract_section(
            text,
            [r"\n##\s+Nablarch Framework Usage\s*\n"],
            stop_pattern=r"\n##[^#]",
        )
        self.assertIn("### Foo", got)
        self.assertIn("#### Deep", got)
        self.assertNotIn("## Next", got)


class HeadingsTest(unittest.TestCase):
    def test_extracts_h3_and_h4(self):
        t = "\n### Foo\nbody\n#### Bar\nbody\n"
        self.assertEqual(_headings(t), ["Foo", "Bar"])

    def test_ignores_body_mentions(self):
        t = "\n### Real\nSessionUtil is used here\n"
        # A class name in the body must NOT be returned as a heading.
        self.assertEqual(_headings(t), ["Real"])

    def test_strips_parenthesized_suffix_left_in_heading(self):
        # We intentionally keep the full heading text; "substring" match in the
        # caller handles parenthesized suffixes.
        t = "\n### SessionUtil (セッションストア)\n"
        self.assertEqual(_headings(t), ["SessionUtil (セッションストア)"])


class MermaidBlocksTest(unittest.TestCase):
    def test_filters_by_kind(self):
        text = """```mermaid
classDiagram
  class A
```
Some text
```mermaid
sequenceDiagram
  A->>B: m
```
"""
        cd = _mermaid_blocks(text, "classDiagram")
        sd = _mermaid_blocks(text, "sequenceDiagram")
        self.assertIn("class A", cd)
        self.assertNotIn("A->>B", cd)
        self.assertIn("A->>B", sd)
        self.assertNotIn("class A", sd)


# -----------------------------------------------------------------------------
# QA grading
# -----------------------------------------------------------------------------

class GradeQaTest(unittest.TestCase):
    SCENARIO = {
        "id": "qa-x",
        "type": "qa",
        "expectations": {
            "a": ["foo", "bar"],
            "b": [["x", "y"]],  # OR: x or y
        },
    }

    def test_all_hit(self):
        g = grade_qa(self.SCENARIO, "contains foo and bar and y")
        self.assertEqual(g["summary"]["detected"], 3)
        self.assertEqual(g["summary"]["total"], 3)

    def test_or_match_any(self):
        g = grade_qa(self.SCENARIO, "foo bar x")
        self.assertTrue(all(i["detected"] for i in g["detection_items"]))

    def test_case_sensitive(self):
        g = grade_qa(self.SCENARIO, "FOO BAR")
        # substring match is case-sensitive per spec
        detected = [i for i in g["detection_items"] if i["detected"]]
        self.assertEqual(detected, [])


# -----------------------------------------------------------------------------
# CA grading — the regression tests that matter most
# -----------------------------------------------------------------------------

class GradeCaNablarchUsageStrictTest(unittest.TestCase):
    """NU detection must be heading-strict. Body mentions don't count."""

    SCENARIO = {
        "id": "ca-x",
        "type": "code-analysis",
        "expectations": {
            "nablarch_usage": ["UniversalDao", "DataReader"],
        },
    }

    def _run(self, md: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "ca-x").mkdir()
            (ws / "ca-x" / "response.md").write_text("")
            out = ws / "ca-x" / "output"
            out.mkdir()
            (out / "code-analysis.md").write_text(md)
            return grade_ca(self.SCENARIO, "", ws)

    def test_detected_when_in_heading(self):
        md = """## Nablarch Framework Usage

### UniversalDao

body...

### DataReader

body...

## Next
"""
        g = self._run(md)
        items = {i["text"]: i["detected"] for i in g["detection_items"]}
        self.assertTrue(items["Nablarch Framework Usage includes 'UniversalDao'"])
        self.assertTrue(items["Nablarch Framework Usage includes 'DataReader'"])

    def test_not_detected_when_only_in_body(self):
        """DataReader appears only in the body of another heading → False."""
        md = """## Nablarch Framework Usage

### UniversalDao

This section mentions DataReader in passing but it is not a heading.

## Next
"""
        g = self._run(md)
        items = {i["text"]: i["detected"] for i in g["detection_items"]}
        self.assertTrue(items["Nablarch Framework Usage includes 'UniversalDao'"])
        # DataReader only in body → strict rule rejects it.
        self.assertFalse(items["Nablarch Framework Usage includes 'DataReader'"])

    def test_detected_via_heading_substring(self):
        """### SessionUtil (セッションストア) should match 'SessionUtil'."""
        scenario = {
            "id": "ca-y",
            "type": "code-analysis",
            "expectations": {"nablarch_usage": ["SessionUtil"]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "ca-y").mkdir()
            (ws / "ca-y" / "response.md").write_text("")
            out = ws / "ca-y" / "output"
            out.mkdir()
            (out / "x.md").write_text(
                "## Nablarch Framework Usage\n\n### SessionUtil (セッションストア)\n\nbody\n"
            )
            g = grade_ca(scenario, "", ws)
        self.assertTrue(g["detection_items"][0]["detected"])

    def test_first_heading_at_start_of_file(self):
        """Regression: _extract_section must match first heading even without leading \\n."""
        md = "## Nablarch Framework Usage\n\n### UniversalDao\n\nbody\n\n## Next\n"
        g = self._run(md)
        items = {i["text"]: i["detected"] for i in g["detection_items"]}
        self.assertTrue(items["Nablarch Framework Usage includes 'UniversalDao'"])


class GradeCaOverviewTest(unittest.TestCase):
    SCENARIO = {
        "id": "ca-z",
        "type": "code-analysis",
        "expectations": {"overview": ["UniversalDao", "SessionUtil"]},
    }

    def _run(self, md: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "ca-z").mkdir()
            (ws / "ca-z" / "response.md").write_text("")
            out = ws / "ca-z" / "output"
            out.mkdir()
            (out / "x.md").write_text(md)
            return grade_ca(self.SCENARIO, "", ws)

    def test_english_names_in_overview(self):
        md = "## Overview\nUses `UniversalDao` and `SessionUtil`.\n\n## Next\n"
        g = self._run(md)
        items = {i["text"]: i["detected"] for i in g["detection_items"]}
        self.assertTrue(items["Overview includes 'UniversalDao'"])
        self.assertTrue(items["Overview includes 'SessionUtil'"])

    def test_japanese_paraphrase_does_not_satisfy_english_rule(self):
        md = "## Overview\nユニバーサルDAOとセッションストアを利用。\n\n## Next\n"
        g = self._run(md)
        items = {i["text"]: i["detected"] for i in g["detection_items"]}
        # Strict: Japanese paraphrase does NOT satisfy English-name rule.
        self.assertFalse(items["Overview includes 'UniversalDao'"])
        self.assertFalse(items["Overview includes 'SessionUtil'"])


class GradeCaMermaidTest(unittest.TestCase):
    SCENARIO = {
        "id": "ca-m",
        "type": "code-analysis",
        "expectations": {
            "class_diagram": {
                "classes": ["A", "B"],
                "relationships": ["A --|> B"],
            },
            "sequence_diagram": {
                "objects": ["A"],
                "messages": ["doThing"],
            },
        },
    }

    def test_mermaid_kind_isolation(self):
        md = """## Architecture

```mermaid
classDiagram
  class A
  class B
  A --|> B
```

## Flow

```mermaid
sequenceDiagram
  participant A
  A->>B: doThing
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "ca-m").mkdir()
            (ws / "ca-m" / "response.md").write_text("")
            out = ws / "ca-m" / "output"
            out.mkdir()
            (out / "x.md").write_text(md)
            g = grade_ca(self.SCENARIO, "", ws)
        for i in g["detection_items"]:
            self.assertTrue(i["detected"], msg=f"failed: {i['text']}")


if __name__ == "__main__":
    unittest.main()
