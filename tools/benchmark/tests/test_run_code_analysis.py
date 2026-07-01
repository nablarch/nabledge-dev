"""Tests for code analysis benchmark runner: runs code-analysis.md skill workflow end-to-end."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.benchmark.scripts.run_code_analysis import (
    MarkerError,
    build_code_analysis_prompt,
    parse_code_analysis_response,
    save_code_analysis_results,
)

DUMMY_METRICS = {
    "duration_ms": 45230,
    "duration_api_ms": 42100,
    "num_turns": 5,
    "total_cost_usd": 0.045,
    "usage": {
        "input_tokens": 12500,
        "output_tokens": 2500,
        "cache_read_input_tokens": 10000,
        "cache_creation_input_tokens": 2500,
    },
}

SAMPLE_SCENARIO = {
    "id": "ca-01",
    "given": {
        "description": "テスト用コード分析シナリオ",
    },
    "when": {
        "workflow": "code-analysis",
        "input": "W11AC02Action",
    },
    "then": {
        "must": [
            {
                "fact": "W11AC02ActionはDbAccessSupportを継承している",
            }
        ],
    },
}

SAMPLE_CODE_ANALYSIS_DETAILS = {
    "step1": {
        "target_files": [".claude/skills/nabledge-1.4/knowledge/assets/web-application-07-insert/W11AC02Action.java"],
        "dependencies": ["DbAccessSupport", "CM311AC1Component"],
        "nablarch_components": ["DbAccessSupport", "ValidationUtil"],
    },
    "step2": {
        "searched_sections": ["web-application/web-application-insert.json:s1"],
    },
}


class TestBuildCodeAnalysisPrompt:
    def setup_method(self):
        self.workflow_content = "# Code Analysis Workflow\n\nStep 1: Find files"
        self.template_content = "# Code Analysis: {{CLASS_NAME}}\n\n## Overview\n{{OVERVIEW}}"
        self.template_guide_content = "## Template Guide\n\nFill each placeholder..."
        self.prompt_template = (
            "Workflow:\n{workflow}\n\n"
            "Template:\n{template}\n\n"
            "Guide:\n{template_guide}\n\n"
            "Target: {target_class}\n"
        )

    def test_includes_workflow(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "# Code Analysis Workflow" in prompt

    def test_includes_template(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "# Code Analysis: {{CLASS_NAME}}" in prompt

    def test_includes_template_guide(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "Fill each placeholder" in prompt

    def test_includes_target_class(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "W11AC02Action" in prompt

    def test_no_unreplaced_workflow_placeholder(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "{workflow}" not in prompt

    def test_no_unreplaced_template_placeholder(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "{template}" not in prompt

    def test_no_unreplaced_template_guide_placeholder(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "{template_guide}" not in prompt

    def test_no_unreplaced_target_class_placeholder(self):
        prompt = build_code_analysis_prompt(
            SAMPLE_SCENARIO,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "{target_class}" not in prompt

    def test_uses_scenario_when_input_as_target_class(self):
        scenario = {**SAMPLE_SCENARIO, "when": {**SAMPLE_SCENARIO["when"], "input": "CM311AC1Component"}}
        prompt = build_code_analysis_prompt(
            scenario,
            self.workflow_content,
            self.template_content,
            self.template_guide_content,
            self.prompt_template,
        )
        assert "CM311AC1Component" in prompt
        assert "W11AC02Action" not in prompt


class TestParseCodeAnalysisResponse:
    def _make_response(self, answer_text, details=None):
        """Build a valid response with all required markers."""
        d = details if details is not None else SAMPLE_CODE_ANALYSIS_DETAILS
        return (
            f"### Answer\n"
            f"{answer_text}\n\n"
            f"<<<CODE_ANALYSIS_DETAILS_JSON>>>\n"
            f"```json\n{json.dumps(d, ensure_ascii=False, indent=2)}\n```\n"
            f"<<<END_CODE_ANALYSIS_DETAILS>>>\n"
        )

    def test_parses_answer_text(self):
        answer = "# Code Analysis: W11AC02Action\n\n## Overview\nThis class handles user registration."
        response = self._make_response(answer)
        result = parse_code_analysis_response(response)
        assert result["answer"] == answer

    def test_parses_code_analysis_details(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        assert "step1" in result["code_analysis_details"]
        assert "step2" in result["code_analysis_details"]

    def test_parses_step1_target_files(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        assert result["code_analysis_details"]["step1"]["target_files"] == [
            ".claude/skills/nabledge-1.4/knowledge/assets/web-application-07-insert/W11AC02Action.java"
        ]

    def test_parses_step1_dependencies(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        assert "DbAccessSupport" in result["code_analysis_details"]["step1"]["dependencies"]

    def test_parses_step1_nablarch_components(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        assert "ValidationUtil" in result["code_analysis_details"]["step1"]["nablarch_components"]

    def test_parses_step2_searched_sections(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        assert result["code_analysis_details"]["step2"]["searched_sections"] == [
            "web-application/web-application-insert.json:s1"
        ]

    def test_raises_marker_error_on_missing_start_marker(self):
        response = "回答テキストだけでマーカーがない"
        with pytest.raises(MarkerError, match="CODE_ANALYSIS_DETAILS_JSON"):
            parse_code_analysis_response(response)

    def test_raises_marker_error_on_invalid_json(self):
        response = (
            "### Answer\n回答\n\n"
            "<<<CODE_ANALYSIS_DETAILS_JSON>>>\n"
            "```json\n{invalid json\n```\n"
            "<<<END_CODE_ANALYSIS_DETAILS>>>\n"
        )
        with pytest.raises(MarkerError, match="JSON"):
            parse_code_analysis_response(response)

    def test_answer_excludes_details_section(self):
        response = self._make_response("本文ドキュメント")
        result = parse_code_analysis_response(response)
        assert "CODE_ANALYSIS_DETAILS_JSON" not in result["answer"]
        assert "step1" not in result["answer"]

    def test_answer_excludes_pre_marker_narration(self):
        """Narration before ### Answer must not appear in answer."""
        narration = "Step 2完了。keyword-search実行中...\n\n"
        response = (
            f"{narration}"
            f"### Answer\n"
            f"本文ドキュメント\n\n"
            f"<<<CODE_ANALYSIS_DETAILS_JSON>>>\n"
            f"```json\n{json.dumps(SAMPLE_CODE_ANALYSIS_DETAILS, ensure_ascii=False)}\n```\n"
            f"<<<END_CODE_ANALYSIS_DETAILS>>>\n"
        )
        result = parse_code_analysis_response(response)
        assert "Step 2完了" not in result["answer"]
        assert result["answer"] == "本文ドキュメント"

    def test_answer_marker_absent_falls_back_to_full_text_before_details(self):
        """Without ### Answer marker: text before <<<CODE_ANALYSIS_DETAILS_JSON>>> is the answer."""
        response = (
            "レガシー回答テキスト\n\n"
            f"<<<CODE_ANALYSIS_DETAILS_JSON>>>\n"
            f"```json\n{json.dumps(SAMPLE_CODE_ANALYSIS_DETAILS, ensure_ascii=False)}\n```\n"
            "<<<END_CODE_ANALYSIS_DETAILS>>>\n"
        )
        result = parse_code_analysis_response(response)
        assert result["answer"] == "レガシー回答テキスト"

    def test_valid_json_in_details_block(self):
        response = self._make_response("ドキュメント本文")
        result = parse_code_analysis_response(response)
        # The parsed details should be a proper dict, not a string
        assert isinstance(result["code_analysis_details"], dict)
        assert isinstance(result["code_analysis_details"]["step1"], dict)
        assert isinstance(result["code_analysis_details"]["step2"], dict)


class TestSaveCodeAnalysisResults:
    def _make_data(self, **overrides):
        base = {
            "scenario_id": "ca-01",
            "code_analysis_details": SAMPLE_CODE_ANALYSIS_DETAILS,
            "answer": "# Code Analysis: W11AC02Action\n\n## Overview\nテスト回答",
            "metrics": DUMMY_METRICS,
            "trace": {"result": "テスト", "duration_ms": 1000},
        }
        base.update(overrides)
        return base

    def test_saves_answer_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_code_analysis_results(tmpdir, "ca-01", self._make_data(answer="テスト回答テキスト"))
            answer = (Path(tmpdir) / "ca-01" / "answer.md").read_text()
            assert "テスト回答テキスト" in answer

    def test_saves_code_analysis_details_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_code_analysis_results(tmpdir, "ca-01", self._make_data())
            details = json.loads((Path(tmpdir) / "ca-01" / "code_analysis_details.json").read_text())
            assert "step1" in details
            assert "step2" in details

    def test_saves_metrics_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_code_analysis_results(tmpdir, "ca-01", self._make_data())
            metrics = json.loads((Path(tmpdir) / "ca-01" / "metrics.json").read_text())
            assert metrics["duration_ms"] == 45230
            assert metrics["total_cost_usd"] == 0.045

    def test_saves_trace_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_data = {"result": "raw output", "duration_ms": 5000, "num_turns": 3}
            save_code_analysis_results(tmpdir, "ca-01", self._make_data(trace=trace_data))
            trace = json.loads((Path(tmpdir) / "ca-01" / "trace.json").read_text())
            assert trace["duration_ms"] == 5000

    def test_creates_scenario_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_code_analysis_results(tmpdir, "ca-999", self._make_data(scenario_id="ca-999"))
            assert (Path(tmpdir) / "ca-999").is_dir()

    def test_all_four_files_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_code_analysis_results(tmpdir, "ca-01", self._make_data())
            scenario_dir = Path(tmpdir) / "ca-01"
            assert (scenario_dir / "answer.md").exists()
            assert (scenario_dir / "code_analysis_details.json").exists()
            assert (scenario_dir / "metrics.json").exists()
            assert (scenario_dir / "trace.json").exists()
