"""Tests for benchmark evaluation logic."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.benchmark.scripts.evaluate import (
    build_deepeval_test_case,
    call_llm,
    compute_deepeval_metrics,
    evaluate_all,
    evaluate_scenario,
    extract_json_from_result,
    load_page_content,
    load_runner_output,
    load_section_content,
    parse_section_ref,
)

DUMMY_DEEPEVAL_SCORES = {
    "answer_correctness": {"score": 0.9, "reason": "facts covered"},
    "answer_relevancy": {"score": 0.85, "reason": "relevant"},
    "faithfulness": {"score": 1.0, "reason": "no hallucination"},
}


class TestExtractJsonFromResult:
    def test_plain_json(self):
        assert extract_json_from_result('{"a": 1}') == '{"a": 1}'

    def test_json_in_code_fence(self):
        text = '```json\n{"a": 1}\n```'
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_json_in_plain_code_fence(self):
        text = '```\n{"a": 1}\n```'
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_whitespace_around(self):
        text = '  \n```json\n{"a": 1}\n```\n  '
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_multiline_json(self):
        text = '```json\n{\n  "a": 1,\n  "b": 2\n}\n```'
        result = extract_json_from_result(text)
        parsed = json.loads(result)
        assert parsed == {"a": 1, "b": 2}

    def test_text_before_code_fence(self):
        text = 'Some preamble text.\n\n```json\n{"a": 1}\n```'
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_text_before_and_after_code_fence(self):
        text = 'Explanation.\n\n```json\n{"a": 1}\n```\n\nMore text.'
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_raw_json_with_trailing_text(self):
        text = '{"a": 1}\n\nSome explanation after.'
        assert extract_json_from_result(text) == '{"a": 1}'

    def test_raw_json_no_trailing(self):
        text = '{"a": 1, "b": "hello"}'
        assert extract_json_from_result(text) == '{"a": 1, "b": "hello"}'


class TestParseSectionRef:
    def test_standard_ref(self):
        path, section_id = parse_section_ref(
            "processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1"
        )
        assert path == "processing-pattern/nablarch-batch/nablarch-batch-architecture.json"
        assert section_id == "s1"

    def test_ref_with_deep_path(self):
        path, section_id = parse_section_ref(
            "component/libraries/libraries-bean-validation.json:s8"
        )
        assert path == "component/libraries/libraries-bean-validation.json"
        assert section_id == "s8"

    def test_ref_with_colon_in_path_uses_last_colon(self):
        path, section_id = parse_section_ref("a/b/c.json:s10")
        assert path == "a/b/c.json"
        assert section_id == "s10"


class TestLoadSectionContent:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        knowledge_dir = Path(self.tmpdir) / "component" / "libs"
        knowledge_dir.mkdir(parents=True)
        data = {
            "id": "test-file",
            "title": "Test",
            "sections": [
                {"id": "s1", "title": "First", "content": "Section one content", "level": 2},
                {"id": "s2", "title": "Second", "content": "Section two content", "level": 2},
            ],
        }
        (knowledge_dir / "test.json").write_text(json.dumps(data), encoding="utf-8")

    def test_load_existing_section(self):
        content = load_section_content(self.tmpdir, "component/libs/test.json:s1")
        assert content == "Section one content"

    def test_load_second_section(self):
        content = load_section_content(self.tmpdir, "component/libs/test.json:s2")
        assert content == "Section two content"

    def test_missing_section_raises(self):
        with pytest.raises(ValueError, match="s99"):
            load_section_content(self.tmpdir, "component/libs/test.json:s99")

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_section_content(self.tmpdir, "nonexistent/file.json:s1")


class TestLoadPageContent:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        knowledge_dir = Path(self.tmpdir) / "component" / "libs"
        knowledge_dir.mkdir(parents=True)
        data = {
            "id": "test-file",
            "title": "Test",
            "sections": [
                {"id": "s1", "title": "First", "content": "Section one content", "level": 2},
                {"id": "s2", "title": "Second", "content": "Section two content", "level": 2},
                {"id": "s3", "title": "Third", "content": "Section three content", "level": 2},
            ],
        }
        (knowledge_dir / "test.json").write_text(json.dumps(data), encoding="utf-8")

    def test_load_all_sections_joined(self):
        content = load_page_content(self.tmpdir, "component/libs/test.json")
        assert "Section one content" in content
        assert "Section two content" in content
        assert "Section three content" in content

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_page_content(self.tmpdir, "nonexistent/file.json")


SAMPLE_WORKFLOW_DETAILS = {
    "step3": {
        "selected_pages": [{"path": "a.json", "reason": "relevant"}],
        "excluded_pages": [],
        "selected_sections": [{"file": "a.json", "section_id": "s1", "relevance": "high", "reason": "key"}],
        "excluded_sections": [],
    },
    "step4": {"read_sections": ["a.json:s1"]},
    "step8": {"answer_sections": {"used": [], "unused": []}},
}


class TestLoadRunnerOutput:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        scenario_dir = Path(self.tmpdir) / "pre-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("テスト回答です", encoding="utf-8")
        (scenario_dir / "workflow_details.json").write_text(
            json.dumps(SAMPLE_WORKFLOW_DETAILS), encoding="utf-8"
        )
        (scenario_dir / "metrics.json").write_text(
            json.dumps({"duration_ms": 1000, "total_tokens": 500, "tool_uses": 3}),
            encoding="utf-8",
        )

    def test_load_all_outputs(self):
        output = load_runner_output(self.tmpdir, "pre-01")
        assert output["answer"] == "テスト回答です"
        assert output["workflow_details"]["step3"]["selected_pages"][0]["path"] == "a.json"
        assert output["metrics"]["duration_ms"] == 1000

    def test_missing_scenario_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_runner_output(self.tmpdir, "nonexistent")


class TestEvaluateScenarioDeepEvalOnly:
    """evaluate_scenario calls DeepEval only — no LLM judge calls."""

    def _make_scenario(self, scenario_id="test-01", must_facts=None):
        return {
            "id": scenario_id,
            "when": {"input": "質問テキスト"},
            "then": {
                "must": must_facts or [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }

    def _make_runner_output(self):
        return {
            "answer": "テスト回答",
            "diagnostics": {"search_sections": ["a.json:s1"]},
            "metrics": {},
        }

    def test_scores_contain_three_deepeval_keys(self):
        scenario = self._make_scenario()
        runner_output = self._make_runner_output()

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            result = evaluate_scenario(scenario, runner_output, "/dummy")

        assert "answer_correctness" in result["scores"]
        assert "answer_relevancy" in result["scores"]
        assert "faithfulness" in result["scores"]

    def test_does_not_call_llm_judge(self):
        scenario = self._make_scenario()
        runner_output = self._make_runner_output()

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()), \
             patch("tools.benchmark.scripts.evaluate.call_llm") as mock_llm:
            evaluate_scenario(scenario, runner_output, "/dummy")

        mock_llm.assert_not_called()

    def test_scores_structure_has_score_and_reason(self):
        scenario = self._make_scenario()
        runner_output = self._make_runner_output()

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            result = evaluate_scenario(scenario, runner_output, "/dummy")

        for key in ("answer_correctness", "answer_relevancy", "faithfulness"):
            assert "score" in result["scores"][key]
            assert "reason" in result["scores"][key]

    def test_no_claim_verdicts_in_result(self):
        scenario = self._make_scenario()
        runner_output = self._make_runner_output()

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            result = evaluate_scenario(scenario, runner_output, "/dummy")

        assert "claim_verdicts" not in result
        assert "hallucination" not in result
        assert "needs_human_review" not in result

    def test_no_must_facts(self):
        scenario = self._make_scenario(must_facts=[])
        runner_output = self._make_runner_output()

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            result = evaluate_scenario(scenario, runner_output, "/dummy")

        assert result["scenario_id"] == "test-01"
        assert "answer_correctness" in result["scores"]


class TestEvaluateAll:
    def test_skips_missing_scenario_dir(self):
        tmpdir = tempfile.mkdtemp()
        scenario_dir = Path(tmpdir) / "pre-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("テスト回答", encoding="utf-8")
        (scenario_dir / "workflow_details.json").write_text(
            json.dumps({"step3": {"selected_pages": [], "selected_sections": [], "excluded_pages": [], "excluded_sections": []}, "step4": {}, "step8": {}}), encoding="utf-8"
        )
        (scenario_dir / "metrics.json").write_text(
            json.dumps({"duration_ms": 1000, "total_tokens": 500, "tool_uses": 3}),
            encoding="utf-8",
        )
        scenarios_path = Path(tmpdir) / "scenarios.json"
        scenarios_path.write_text(json.dumps({
            "scenarios": [
                {
                    "id": "pre-01",
                    "given": {"description": "test"},
                    "when": {"input": "input"},
                    "then": {"must": [], "acceptable": []},
                },
                {
                    "id": "pre-02",
                    "given": {"description": "test2"},
                    "when": {"input": "input2"},
                    "then": {"must": [], "acceptable": []},
                },
            ]
        }), encoding="utf-8")

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            results = evaluate_all(tmpdir, str(scenarios_path), "/dummy")

        assert len(results) == 1
        assert results[0]["scenario_id"] == "pre-01"
        eval_path = scenario_dir / "evaluation.json"
        assert eval_path.exists()

    def test_writes_evaluation_json(self):
        tmpdir = tempfile.mkdtemp()
        scenario_dir = Path(tmpdir) / "test-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("回答テキスト", encoding="utf-8")
        (scenario_dir / "workflow_details.json").write_text(
            json.dumps({"step3": {"selected_pages": [], "selected_sections": [], "excluded_pages": [], "excluded_sections": []}, "step4": {}, "step8": {}}), encoding="utf-8"
        )
        (scenario_dir / "metrics.json").write_text(
            json.dumps({"duration_ms": 2000, "total_tokens": 1000, "tool_uses": 5}),
            encoding="utf-8",
        )
        scenarios_path = Path(tmpdir) / "scenarios.json"
        scenarios_path.write_text(json.dumps({
            "scenarios": [{
                "id": "test-01",
                "given": {"description": "desc"},
                "when": {"input": "inp"},
                "then": {"must": [], "acceptable": []},
            }]
        }), encoding="utf-8")

        with patch("tools.benchmark.scripts.evaluate.compute_deepeval_metrics",
                   return_value=DUMMY_DEEPEVAL_SCORES), \
             patch("tools.benchmark.scripts.evaluate.build_deepeval_test_case",
                   return_value=MagicMock()):
            evaluate_all(tmpdir, str(scenarios_path), "/dummy")

        eval_path = scenario_dir / "evaluation.json"
        with open(eval_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["scenario_id"] == "test-01"
        assert "scores" in data


class TestCallLlm:
    """Tests for call_llm subprocess invocation."""

    def test_prompt_passed_via_stdin_not_argv(self):
        """full_prompt must be passed as stdin (input=), not as a CLI argument.

        OSError: Argument list too long occurs when long prompts are passed as argv.
        subprocess.run must not include full_prompt in the command list.
        """
        captured = {}

        def mock_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["input"] = kwargs.get("input")
            import subprocess
            mock_result = subprocess.CompletedProcess(cmd, 0, stdout='', stderr='')
            mock_result.stdout = '{"result": "{\\"verdict\\": \\"PASS\\", \\"claims\\": [], \\"reason\\": \\"ok\\"}", "usage": {}, "duration_ms": 0, "duration_api_ms": 0, "total_cost_usd": 0}'
            return mock_result

        with patch("tools.benchmark.scripts.evaluate.subprocess.run", mock_run):
            call_llm("test prompt", '{"type": "object"}')

        assert not any("test prompt" in str(arg) for arg in captured["cmd"]), (
            "full_prompt must not be passed as a CLI argument (causes OSError on long prompts)"
        )
        assert captured["input"] is not None, "prompt must be passed via stdin (input=)"
        assert "test prompt" in captured["input"]


class TestBuildDeepEvalTestCase:
    """Tests for build_deepeval_test_case: scenario + runner_output → LLMTestCase."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        knowledge_dir = Path(self.tmpdir) / "batch"
        knowledge_dir.mkdir(parents=True)
        data = {
            "id": "batch-arch",
            "title": "Batch Architecture",
            "sections": [
                {"id": "s1", "title": "Overview", "content": "Batch runs as standalone app.", "level": 2},
                {"id": "s2", "title": "RequestPath", "content": "Use -requestPath to specify action.", "level": 2},
            ],
        }
        (knowledge_dir / "batch-arch.json").write_text(json.dumps(data), encoding="utf-8")
        self.scenario = {
            "id": "pre-01",
            "when": {"input": "バッチアプリケーションはどのように起動しますか？"},
            "then": {
                "must": [
                    {"fact": "javaコマンドから起動する", "section": "batch/batch-arch.json:s1"},
                    {"fact": "-requestPathで指定する", "section": "batch/batch-arch.json:s2"},
                ],
                "acceptable": [],
            },
        }

    def test_input_mapped_from_scenario(self):
        runner_output = {
            "answer": "バッチはjavaコマンドで起動します。",
            "diagnostics": {"search_sections": ["batch/batch-arch.json:s1"]},
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.input == "バッチアプリケーションはどのように起動しますか？"

    def test_actual_output_mapped_from_answer(self):
        runner_output = {
            "answer": "バッチはjavaコマンドで起動します。",
            "diagnostics": {"search_sections": []},
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.actual_output == "バッチはjavaコマンドで起動します。"

    def test_expected_output_is_must_facts_joined(self):
        runner_output = {
            "answer": "回答",
            "diagnostics": {"search_sections": []},
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert "javaコマンドから起動する" in tc.expected_output
        assert "-requestPathで指定する" in tc.expected_output

    def test_retrieval_context_from_search_sections(self):
        runner_output = {
            "answer": "回答",
            "diagnostics": {
                "search_sections": [
                    "batch/batch-arch.json:s1",
                    "batch/batch-arch.json:s2",
                ]
            },
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.retrieval_context is not None
        assert len(tc.retrieval_context) == 2
        assert "Batch runs as standalone app." in tc.retrieval_context[0]
        assert "Use -requestPath to specify action." in tc.retrieval_context[1]

    def test_empty_search_sections_gives_empty_retrieval_context(self):
        runner_output = {
            "answer": "回答",
            "diagnostics": {"search_sections": []},
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.retrieval_context == []

    def test_unresolvable_section_ref_skipped(self):
        runner_output = {
            "answer": "回答",
            "diagnostics": {"search_sections": ["nonexistent/file.json:s1"]},
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.retrieval_context == []

    def test_missing_diagnostics_gives_empty_retrieval_context(self):
        runner_output = {"answer": "回答"}
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert tc.retrieval_context == []

    def test_workflow_details_selected_sections_as_fallback(self):
        """run_qa output format: workflow_details.step3.selected_sections."""
        runner_output = {
            "answer": "回答",
            "workflow_details": {
                "step3": {
                    "selected_sections": [
                        {"file": "batch/batch-arch.json", "section_id": "s1"},
                        {"file": "batch/batch-arch.json", "section_id": "s2"},
                    ]
                }
            },
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert len(tc.retrieval_context) == 2
        assert "Batch runs as standalone app." in tc.retrieval_context[0]

    def test_diagnostics_search_sections_takes_precedence_over_workflow_details(self):
        """When both formats present, diagnostics.search_sections wins."""
        runner_output = {
            "answer": "回答",
            "diagnostics": {"search_sections": ["batch/batch-arch.json:s1"]},
            "workflow_details": {
                "step3": {
                    "selected_sections": [
                        {"file": "batch/batch-arch.json", "section_id": "s2"},
                    ]
                }
            },
        }
        tc = build_deepeval_test_case(self.scenario, runner_output, self.tmpdir)
        assert len(tc.retrieval_context) == 1
        assert "Batch runs as standalone app." in tc.retrieval_context[0]


class TestComputeDeepEvalMetrics:
    """Tests for compute_deepeval_metrics: LLMTestCase → dict of 3 metric scores."""

    def _make_test_case(self):
        from deepeval.test_case import LLMTestCase
        return LLMTestCase(
            input="バッチはどう起動？",
            actual_output="javaコマンドで起動します。",
            expected_output="javaコマンドから起動する",
            retrieval_context=["Batch runs as standalone app."],
        )

    def _patched_compute(self, tc, run_return_value):
        mock_metric = MagicMock()

        def mock_factory(*args, **kwargs):
            return mock_metric

        with patch("deepeval.metrics.GEval", mock_factory), \
             patch("deepeval.metrics.AnswerRelevancyMetric", mock_factory), \
             patch("deepeval.metrics.FaithfulnessMetric", mock_factory), \
             patch("tools.benchmark.scripts.evaluate._run_deepeval_metric", return_value=run_return_value):
            return compute_deepeval_metrics(tc, model=MagicMock())

    def _patched_compute_failing(self, tc):
        mock_metric = MagicMock()

        def mock_factory(*args, **kwargs):
            return mock_metric

        with patch("deepeval.metrics.GEval", mock_factory), \
             patch("deepeval.metrics.AnswerRelevancyMetric", mock_factory), \
             patch("deepeval.metrics.FaithfulnessMetric", mock_factory), \
             patch("tools.benchmark.scripts.evaluate._run_deepeval_metric", side_effect=Exception("LLM error")):
            return compute_deepeval_metrics(tc, model=MagicMock())

    def test_returns_three_metric_keys(self):
        tc = self._make_test_case()
        result = self._patched_compute(tc, 0.85)
        assert "answer_correctness" in result
        assert "answer_relevancy" in result
        assert "faithfulness" in result

    def test_scores_are_floats_between_0_and_1(self):
        tc = self._make_test_case()
        result = self._patched_compute(tc, 0.85)
        for key in ("answer_correctness", "answer_relevancy", "faithfulness"):
            assert isinstance(result[key], float), f"{key} must be float"
            assert 0.0 <= result[key] <= 1.0, f"{key} must be in [0, 1]"

    def test_metric_failure_returns_none_not_raises(self):
        tc = self._make_test_case()
        result = self._patched_compute_failing(tc)
        for key in ("answer_correctness", "answer_relevancy", "faithfulness"):
            assert result[key] is None, f"{key} must be None on failure"

    def test_sets_aws_ca_bundle_from_ssl_cert_file_when_unset(self):
        """AWS_CA_BUNDLE is auto-set from SSL_CERT_FILE when not already configured."""
        tc = self._make_test_case()
        env_without_ca_bundle = {k: v for k, v in os.environ.items() if k != "AWS_CA_BUNDLE"}
        env_without_ca_bundle["SSL_CERT_FILE"] = "/some/ca.crt"

        with patch.dict(os.environ, env_without_ca_bundle, clear=True), \
             patch("deepeval.metrics.GEval", MagicMock()), \
             patch("deepeval.metrics.AnswerRelevancyMetric", MagicMock()), \
             patch("deepeval.metrics.FaithfulnessMetric", MagicMock()), \
             patch("tools.benchmark.scripts.evaluate._run_deepeval_metric", return_value=0.5):
            compute_deepeval_metrics(tc, model=MagicMock())
            assert os.environ.get("AWS_CA_BUNDLE") == "/some/ca.crt"

    def test_does_not_override_existing_aws_ca_bundle(self):
        """AWS_CA_BUNDLE is not changed when already set."""
        tc = self._make_test_case()
        env_with_ca_bundle = dict(os.environ)
        env_with_ca_bundle["AWS_CA_BUNDLE"] = "/existing/ca.crt"
        env_with_ca_bundle["SSL_CERT_FILE"] = "/other/ca.crt"

        with patch.dict(os.environ, env_with_ca_bundle, clear=True), \
             patch("deepeval.metrics.GEval", MagicMock()), \
             patch("deepeval.metrics.AnswerRelevancyMetric", MagicMock()), \
             patch("deepeval.metrics.FaithfulnessMetric", MagicMock()), \
             patch("tools.benchmark.scripts.evaluate._run_deepeval_metric", return_value=0.5):
            compute_deepeval_metrics(tc, model=MagicMock())
            assert os.environ.get("AWS_CA_BUNDLE") == "/existing/ca.crt"
