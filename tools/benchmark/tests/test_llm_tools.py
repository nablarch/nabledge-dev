"""Tests for tools/benchmark/llm_tools scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

LLM_TOOLS = Path(__file__).resolve().parent.parent / "llm_tools"
VERIFY_SCRIPT = LLM_TOOLS / "verify_kb_evidence.py"


def _run(knowledge_root: str, file_rel: str, sid: str, quote: str) -> str:
    """Call verify_kb_evidence.py using the stdin-based interface (argv[4] == "-").

    The quote is passed via stdin to avoid shell-expansion of backticks and
    dollar-signs, which is the same mechanism the judge LLM is instructed to use.
    """
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), knowledge_root, file_rel, sid, "-"],
        input=quote,
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def _make_kb(tmp_path: Path, file_rel: str, sections: dict[str, str]) -> str:
    """Create a minimal knowledge JSON and return the knowledge_root path."""
    kb_root = tmp_path / "knowledge"
    kb_root.mkdir(exist_ok=True)
    target = kb_root / file_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"sections": sections}, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(kb_root)


class TestVerifyKbEvidence:
    def test_match_verbatim(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "ThymeleafResponseWriter is used here"})
        assert _run(root, "foo.json", "s1", "ThymeleafResponseWriter") == "match"

    def test_mismatch_quote_not_in_sid(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {
            "s1": "something else entirely",
            "s2": "ThymeleafResponseWriter is here",
        })
        out = _run(root, "foo.json", "s1", "ThymeleafResponseWriter")
        assert out.startswith("mismatch")

    def test_mismatch_file_not_found(self, tmp_path):
        """File missing within an existing knowledge root."""
        root = str(tmp_path / "knowledge")
        (tmp_path / "knowledge").mkdir()
        out = _run(root, "nonexistent.json", "s1", "some quote")
        assert out.startswith("mismatch")

    def test_mismatch_sid_not_found(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "body text"})
        out = _run(root, "foo.json", "s99", "body text")
        assert out.startswith("mismatch")

    def test_match_normalized_whitespace(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "hello  world\nfoo"})
        assert _run(root, "foo.json", "s1", "hello world foo") == "match"

    def test_mismatch_empty_quote(self, tmp_path):
        root = _make_kb(tmp_path, "foo.json", {"s1": "some body"})
        out = _run(root, "foo.json", "s1", "")
        assert out.startswith("mismatch")

    def test_section_body_as_dict(self, tmp_path):
        """Sections whose value is a dict with a 'body' key."""
        kb_root = tmp_path / "knowledge"
        kb_root.mkdir()
        target = kb_root / "foo.json"
        target.write_text(
            json.dumps({"sections": {"s1": {"body": "ThymeleafResponseWriter here"}}}),
            encoding="utf-8",
        )
        assert _run(str(kb_root), "foo.json", "s1", "ThymeleafResponseWriter") == "match"

    def test_mismatch_double_underscore_not_stripped_from_quote(self, tmp_path):
        """quote with __ must NOT match body that only contains the bare identifier."""
        root = _make_kb(tmp_path, "foo.json", {"s1": "The constant value is used"})
        out = _run(root, "foo.json", "s1", "__constant__")
        assert out.startswith("mismatch")

    def test_match_backtick_stripped_from_body(self, tmp_path):
        """quote without backticks should match body containing `code` with backticks (review-07 scenario)."""
        root = _make_kb(tmp_path, "foo.json", {"s1": "the value `unsafe-inline` is allowed"})
        assert _run(root, "foo.json", "s1", "unsafe-inline") == "match"

    def test_match_backtick_stripped_from_quote(self, tmp_path):
        """quote with backticks should match body that contains the text without backticks (impact-01 scenario)."""
        root = _make_kb(tmp_path, "foo.json", {"s1": "use the unsafe-inline value here"})
        assert _run(root, "foo.json", "s1", "`unsafe-inline`") == "match"

    def test_match_multiple_backtick_tokens_in_quote(self, tmp_path):
        """quote with multiple backtick-wrapped tokens matches plain-text body (impact-01 exact pattern)."""
        body = "chunk要素のitem-count属性でwriteItems一回当たりの処理件数を設定する"
        root = _make_kb(tmp_path, "foo.json", {"s1": body})
        quote = "`chunk`要素の`item-count`属性で`writeItems`一回当たりの処理件数を設定する"
        assert _run(root, "foo.json", "s1", quote) == "match"

    def test_match_quote_with_dollar_sign_via_stdin(self, tmp_path):
        """quote containing $ is passed safely via stdin and does not expand."""
        body = "Set $HOME to the installation directory"
        root = _make_kb(tmp_path, "foo.json", {"s1": body})
        assert _run(root, "foo.json", "s1", "Set $HOME to the installation directory") == "match"

    def test_stdin_interface_with_backtick_and_dollar(self, tmp_path):
        """Stdin interface must survive a quote that has both backticks and $ without shell expansion."""
        body = "`$HOME` and `item-count` are both set"
        root = _make_kb(tmp_path, "foo.json", {"s1": body})
        # quote passes both chars through stdin; they must arrive unmangled
        assert _run(root, "foo.json", "s1", "$HOME and item-count are both set") == "match"


class TestComputeLevel:
    """Unit tests for judge.compute_level scoring engine."""

    def _make_verdict(self, a_statuses, b_count=0, c_reasons=None):
        a_facts = [{"fact": f"fact{i}", "status": s} for i, s in enumerate(a_statuses)]
        b_claims = [{"claim": f"b{i}"} for i in range(b_count)]
        c_claims = [{"claim": f"c{i}", "reason": r, "why": "x"} for i, r in enumerate(c_reasons or [])]
        return {"a_facts": a_facts, "b_claims": b_claims, "c_claims": c_claims, "level": 0, "reasoning": ""}

    def test_all_covered_no_c_no_b_returns_level2(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED", "COVERED"])
        assert compute_level(v) == 2

    def test_all_covered_with_b_returns_level3(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED", "COVERED"], b_count=1)
        assert compute_level(v) == 3

    def test_all_covered_with_supported_by_kb_returns_level3(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED"], c_reasons=["SUPPORTED_BY_KB"])
        assert compute_level(v) == 3

    def test_partial_returns_level1(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED", "PARTIAL"])
        assert compute_level(v) == 1

    def test_penalizing_c_with_all_covered_returns_level1(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED", "COVERED"], c_reasons=["UNSUPPORTED_KB_VERIFIED"])
        assert compute_level(v) == 1

    def test_off_topic_c_returns_level1(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED"], c_reasons=["OFF-TOPIC"])
        assert compute_level(v) == 1

    def test_contradiction_c_returns_level1(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["COVERED"], c_reasons=["CONTRADICTION"])
        assert compute_level(v) == 1

    def test_majority_missing_returns_level0(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["MISSING", "MISSING", "COVERED"])
        assert compute_level(v) == 0

    def test_exactly_half_missing_not_majority_returns_level1(self):
        """1 MISSING out of 2 = 50%, not majority (>50%) → level 1 not 0."""
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = self._make_verdict(["MISSING", "COVERED"])
        assert compute_level(v) == 1

    def test_empty_a_facts_returns_level0(self):
        from tools.benchmark.bench.judge import compute_level  # noqa: PLC0415
        v = {"a_facts": [], "b_claims": [], "c_claims": [], "level": 0, "reasoning": ""}
        assert compute_level(v) == 0
