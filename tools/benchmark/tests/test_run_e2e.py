"""Tests for E2E benchmark runner: runs skill workflow end-to-end."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.benchmark.scripts.run_e2e import (
    build_e2e_prompt,
    parse_e2e_response,
    save_e2e_results,
    run_e2e_all,
    run_e2e_scenario,
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
    "id": "pre-01",
    "phase": "pre-benchmark",
    "given": {
        "usecase": "テスト用ユースケース",
        "category": "batch-architecture",
        "description": "テスト説明",
    },
    "when": {
        "workflow": "qa",
        "input": "テスト質問です",
        "expected_hearing": "should_skip",
        "hearing_answer": {
            "processing_type": "Nablarchバッチ",
            "goal": "バッチを起動する",
        },
    },
    "then": {
        "must": [
            {
                "section": "processing-pattern/nablarch-batch/architecture.json:s1",
                "fact": "テスト事実",
            }
        ],
        "acceptable": [],
    },
}


class TestBuildE2ePrompt:
    def setup_method(self):
        self.workflow_content = "# QA Workflow\n\nStep 1: Search\nStep 2: Answer"

    def test_includes_workflow(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "# QA Workflow" in prompt

    def test_includes_question(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "テスト質問です" in prompt

    def test_includes_hearing_answer_processing_type(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "Nablarchバッチ" in prompt

    def test_includes_hearing_answer_goal(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "バッチを起動する" in prompt

    def test_includes_benchmark_markers_instruction(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "BENCHMARK_HEARING" in prompt
        assert "BENCHMARK_SEARCH" in prompt
        assert "BENCHMARK_ANSWER" in prompt

    def test_no_hearing_answer_excludes_hearing_section(self):
        scenario_no_hearing = {
            **SAMPLE_SCENARIO,
            "when": {**SAMPLE_SCENARIO["when"], "hearing_answer": None},
        }
        prompt = build_e2e_prompt(scenario_no_hearing, self.workflow_content)
        assert "Nablarchバッチ" not in prompt
        assert "バッチを起動する" not in prompt

    def test_hearing_answer_present_injects_context(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "Nablarchバッチ" in prompt
        assert "バッチを起動する" in prompt

    def test_hearing_answer_injected_into_question_not_separate_section(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "コンテキスト（ヒアリング結果）" not in prompt

    def test_no_unreplaced_placeholders(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "{question}" not in prompt
        assert "{workflow}" not in prompt


class TestParseE2eResponse:
    def _make_response(self, hearing_json, search_json, answer_text):
        return (
            f"何か前置きテキスト\n"
            f"<<<BENCHMARK_HEARING>>>\n{hearing_json}\n<<<END_BENCHMARK_HEARING>>>\n"
            f"<<<BENCHMARK_SEARCH>>>\n{search_json}\n<<<END_BENCHMARK_SEARCH>>>\n"
            f"<<<BENCHMARK_ANSWER>>>\n{answer_text}\n<<<END_BENCHMARK_ANSWER>>>"
        )

    def test_parses_hearing_skipped(self):
        response = self._make_response(
            '{"status": "skipped", "questions": []}',
            '{"section_ids": []}',
            "回答テキスト",
        )
        result = parse_e2e_response(response)
        assert result["hearing"]["status"] == "skipped"
        assert result["hearing"]["questions"] == []

    def test_parses_hearing_asked(self):
        response = self._make_response(
            '{"status": "asked", "questions": ["処理方式は？"]}',
            '{"section_ids": []}',
            "回答テキスト",
        )
        result = parse_e2e_response(response)
        assert result["hearing"]["status"] == "asked"
        assert "処理方式は？" in result["hearing"]["questions"]

    def test_parses_search_section_ids(self):
        response = self._make_response(
            '{"status": "skipped", "questions": []}',
            '{"section_ids": ["path/to/file.json:s1", "other/file.json:s2"]}',
            "回答テキスト",
        )
        result = parse_e2e_response(response)
        assert "path/to/file.json:s1" in result["search"]["section_ids"]
        assert "other/file.json:s2" in result["search"]["section_ids"]

    def test_parses_answer_text(self):
        answer = "**結論**: バッチは-requestPathで起動します\n\n**根拠**: ..."
        response = self._make_response(
            '{"status": "skipped", "questions": []}',
            '{"section_ids": []}',
            answer,
        )
        result = parse_e2e_response(response)
        assert result["answer"] == answer

    def test_raises_on_missing_hearing_marker(self):
        response = (
            "<<<BENCHMARK_SEARCH>>>\n{}\n<<<END_BENCHMARK_SEARCH>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n回答\n<<<END_BENCHMARK_ANSWER>>>"
        )
        with pytest.raises(ValueError, match="BENCHMARK_HEARING"):
            parse_e2e_response(response)

    def test_raises_on_missing_search_marker(self):
        response = (
            "<<<BENCHMARK_HEARING>>>\n{}\n<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n回答\n<<<END_BENCHMARK_ANSWER>>>"
        )
        with pytest.raises(ValueError, match="BENCHMARK_SEARCH"):
            parse_e2e_response(response)

    def test_raises_on_missing_answer_marker(self):
        response = (
            "<<<BENCHMARK_HEARING>>>\n{}\n<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_SEARCH>>>\n{}\n<<<END_BENCHMARK_SEARCH>>>"
        )
        with pytest.raises(ValueError, match="BENCHMARK_ANSWER"):
            parse_e2e_response(response)

    def test_empty_section_ids(self):
        response = self._make_response(
            '{"status": "skipped", "questions": []}',
            '{"section_ids": []}',
            "回答なし",
        )
        result = parse_e2e_response(response)
        assert result["search"]["section_ids"] == []


class TestSaveE2eResults:
    def _make_data(self, **overrides):
        base = {
            "scenario_id": "pre-01",
            "hearing": {"status": "skipped", "questions": []},
            "search": {"section_ids": ["file.json:s1"]},
            "answer": "テスト回答",
            "metrics": DUMMY_METRICS,
            "trace": {"result": "テスト", "duration_ms": 1000},
        }
        base.update(overrides)
        return base

    def test_saves_hearing_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_e2e_results(tmpdir, "pre-01", self._make_data())
            hearing = json.loads((Path(tmpdir) / "pre-01" / "hearing.json").read_text())
            assert hearing["status"] == "skipped"

    def test_saves_search_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_e2e_results(tmpdir, "pre-01", self._make_data())
            search = json.loads((Path(tmpdir) / "pre-01" / "search.json").read_text())
            assert "file.json:s1" in search["section_ids"]

    def test_saves_answer_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_e2e_results(tmpdir, "pre-01", self._make_data(answer="テスト回答テキスト"))
            answer = (Path(tmpdir) / "pre-01" / "answer.md").read_text()
            assert "テスト回答テキスト" in answer

    def test_saves_metrics_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_e2e_results(tmpdir, "pre-01", self._make_data())
            metrics = json.loads((Path(tmpdir) / "pre-01" / "metrics.json").read_text())
            assert metrics["duration_ms"] == 45230
            assert metrics["total_cost_usd"] == 0.045

    def test_saves_trace_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trace_data = {"result": "raw output", "duration_ms": 5000, "num_turns": 3}
            save_e2e_results(tmpdir, "pre-01", self._make_data(trace=trace_data))
            trace = json.loads((Path(tmpdir) / "pre-01" / "trace.json").read_text())
            assert trace["duration_ms"] == 5000

    def test_creates_scenario_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_e2e_results(tmpdir, "qa-001", self._make_data(scenario_id="qa-001"))
            assert (Path(tmpdir) / "qa-001").is_dir()


class TestRunE2eScenario:
    def _make_claude_output(self, result_text):
        output = {
            "result": result_text,
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
        return json.dumps(output)

    def _make_valid_e2e_response(self):
        return (
            "<<<BENCHMARK_HEARING>>>\n"
            '{"status": "skipped", "questions": []}\n'
            "<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_SEARCH>>>\n"
            '{"section_ids": ["path/to/file.json:s1"]}\n'
            "<<<END_BENCHMARK_SEARCH>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n"
            "**結論**: テスト回答\n"
            "<<<END_BENCHMARK_ANSWER>>>"
        )

    def _make_mock_proc(self, result_text=None, returncode=0):
        stdout = self._make_claude_output(result_text or self._make_valid_e2e_response())
        return type("P", (), {
            "returncode": returncode,
            "stdout": stdout if returncode == 0 else "",
            "stderr": "" if returncode == 0 else "Error occurred",
        })()

    def test_returns_scenario_id(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert result["scenario_id"] == "pre-01"

    def test_returns_hearing(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert result["hearing"]["status"] == "skipped"

    def test_returns_search(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert "section_ids" in result["search"]

    def test_returns_answer(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert "テスト回答" in result["answer"]

    def test_returns_metrics(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert result["metrics"]["duration_ms"] == 45230
            assert result["metrics"]["total_cost_usd"] == 0.045

    def test_returns_trace(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert "trace" in result
            assert "result" in result["trace"]

    def test_raises_on_nonzero_returncode(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc(returncode=1)):
                with pytest.raises(RuntimeError, match="claude"):
                    run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

    def test_uses_skill_dir_as_cwd(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            call_kwargs = mock_run.call_args[1]
            assert str(call_kwargs.get("cwd", "")) == str(skill_dir)

    def test_uses_sonnet_model_by_default(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            cmd = mock_run.call_args[0][0]
            assert "sonnet" in cmd

    def test_uses_allowed_tools_as_specified(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            cmd = mock_run.call_args[0][0]
            allowed_tools_idx = cmd.index("--allowedTools")
            allowed_tools_value = cmd[allowed_tools_idx + 1]
            assert "Bash(keyword-search.sh *)" in allowed_tools_value
            assert "Bash(read-sections.sh *)" in allowed_tools_value
            assert "Read" in allowed_tools_value

    def test_uses_default_timeout_360(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs.get("timeout") == 360

    def test_metrics_includes_model_usage(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            output_with_model_usage = {
                "result": self._make_valid_e2e_response(),
                "duration_ms": 10000,
                "duration_api_ms": 9000,
                "num_turns": 3,
                "total_cost_usd": 0.01,
                "usage": {"input_tokens": 5000, "output_tokens": 1000,
                          "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                "modelUsage": {"claude-sonnet-4-6": {"input_tokens": 5000, "cost_usd": 0.01}},
            }
            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": json.dumps(output_with_model_usage),
                "stderr": "",
            })()
            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert "model_usage" in result["metrics"]
            assert "claude-sonnet-4-6" in result["metrics"]["model_usage"]

    def test_metrics_model_usage_defaults_to_empty_dict(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            with patch("subprocess.run", return_value=self._make_mock_proc()):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)
            assert "model_usage" in result["metrics"]
            assert result["metrics"]["model_usage"] == {}

    def test_hearing_answer_injected_when_set(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            captured_prompts = []

            def capture_run(*args, **kwargs):
                captured_prompts.append(kwargs.get("input", ""))
                return self._make_mock_proc()

            with patch("subprocess.run", side_effect=capture_run):
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert "Nablarchバッチ" in captured_prompts[0]

    def test_hearing_answer_not_injected_when_none(self):
        scenario_no_hearing = {
            **SAMPLE_SCENARIO,
            "when": {**SAMPLE_SCENARIO["when"], "hearing_answer": None},
        }
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")
            captured_prompts = []

            def capture_run(*args, **kwargs):
                captured_prompts.append(kwargs.get("input", ""))
                return self._make_mock_proc()

            with patch("subprocess.run", side_effect=capture_run):
                run_e2e_scenario(scenario_no_hearing, skill_dir)

            assert "Nablarchバッチ" not in captured_prompts[0]


class TestRunE2eAll:
    def _make_claude_output(self, result_text):
        output = {
            "result": result_text,
            "duration_ms": 10000,
            "duration_api_ms": 9000,
            "num_turns": 3,
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 5000, "output_tokens": 1000,
                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
        }
        return json.dumps(output)

    def _make_valid_e2e_response(self):
        return (
            "<<<BENCHMARK_HEARING>>>\n"
            '{"status": "skipped", "questions": []}\n'
            "<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_SEARCH>>>\n"
            '{"section_ids": []}\n'
            "<<<END_BENCHMARK_SEARCH>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n"
            "テスト回答\n"
            "<<<END_BENCHMARK_ANSWER>>>"
        )

    def _make_mock_proc(self):
        return type("P", (), {
            "returncode": 0,
            "stdout": self._make_claude_output(self._make_valid_e2e_response()),
            "stderr": "",
        })()

    def _setup_skill_dir(self, base_dir):
        skill_dir = Path(base_dir) / "skill"
        skill_dir.mkdir()
        (skill_dir / "workflows").mkdir()
        (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")
        (skill_dir / "knowledge").mkdir()
        return skill_dir

    def _setup_scenarios(self, base_dir, scenarios=None):
        if scenarios is None:
            scenarios = [SAMPLE_SCENARIO]
        scenarios_path = Path(base_dir) / "qa.json"
        scenarios_path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
        return scenarios_path

    FAKE_EVAL = {"scenario_id": "pre-01", "scores": {"accuracy": 1.0, "hallucination": 1}}

    def _run_all(self, tmpdir, scenarios=None, scenario_ids=None):
        skill_dir = self._setup_skill_dir(tmpdir)
        scenarios_path = self._setup_scenarios(tmpdir, scenarios)
        output_dir = Path(tmpdir) / "results"
        with patch("subprocess.run", return_value=self._make_mock_proc()), \
             patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=self.FAKE_EVAL):
            summary = run_e2e_all(
                str(scenarios_path), str(skill_dir),
                output_dir=str(output_dir),
                scenario_ids=scenario_ids,
            )
        return summary, output_dir

    def test_runs_all_scenarios(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary, _ = self._run_all(tmpdir)
            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "pre-01"

    def test_filters_by_scenario_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario2 = {**SAMPLE_SCENARIO, "id": "pre-02"}
            summary, _ = self._run_all(tmpdir, [SAMPLE_SCENARIO, scenario2], scenario_ids=["pre-01"])
            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "pre-01"

    def test_saves_summary_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary_path = output_dir / "summary.json"
            assert summary_path.exists()
            summary = json.loads(summary_path.read_text())
            assert summary["total_scenarios"] == 1

    def test_summary_includes_skill_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary = json.loads((output_dir / "summary.json").read_text())
            assert "skill_dir" in summary

    def test_summary_includes_scenarios_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary = json.loads((output_dir / "summary.json").read_text())
            assert "scenarios_file" in summary

    def test_summary_includes_executed_at(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary = json.loads((output_dir / "summary.json").read_text())
            assert "executed_at" in summary

    def test_calls_evaluate_scenario_for_each_scenario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir)
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", return_value=self._make_mock_proc()), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=self.FAKE_EVAL) as mock_eval:
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))
            assert mock_eval.call_count == 1

    def test_saves_evaluation_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            eval_path = output_dir / "pre-01" / "evaluation.json"
            assert eval_path.exists()
            eval_data = json.loads(eval_path.read_text())
            assert eval_data["scenario_id"] == "pre-01"


class TestRunE2eAllErrorHandling:
    """Tests for error handling in run_e2e_all: failures are isolated per scenario."""

    def _setup_skill_dir(self, base_dir):
        skill_dir = Path(base_dir) / "skill"
        skill_dir.mkdir()
        (skill_dir / "workflows").mkdir()
        (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")
        (skill_dir / "knowledge").mkdir()
        return skill_dir

    def _setup_scenarios(self, base_dir, scenarios):
        scenarios_path = Path(base_dir) / "qa.json"
        scenarios_path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
        return scenarios_path

    def _make_valid_proc(self):
        valid_response = (
            "<<<BENCHMARK_HEARING>>>\n"
            '{"status": "skipped", "questions": []}\n'
            "<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_SEARCH>>>\n"
            '{"section_ids": []}\n'
            "<<<END_BENCHMARK_SEARCH>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n"
            "テスト回答\n"
            "<<<END_BENCHMARK_ANSWER>>>"
        )
        claude_out = json.dumps({
            "result": valid_response,
            "duration_ms": 10000,
            "duration_api_ms": 9000,
            "num_turns": 3,
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 5000, "output_tokens": 1000,
                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
        })
        return type("P", (), {"returncode": 0, "stdout": claude_out, "stderr": ""})()

    FAKE_EVAL = {"scenario_id": "s1", "scores": {"accuracy": 1.0}}

    def test_continues_after_timeout(self):
        """TimeoutExpired on scenario 1 must not prevent scenario 2 from running."""
        import subprocess
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}
        scenario2 = {**SAMPLE_SCENARIO, "id": "s2"}
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise subprocess.TimeoutExpired(cmd="claude", timeout=360)
            return self._make_valid_proc()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1, scenario2])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=self.FAKE_EVAL):
                summary = run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

        assert summary["total_scenarios"] == 2
        assert summary["scenarios"][1]["id"] == "s2"
        assert summary["scenarios"][1].get("status") != "error"

    def test_error_scenario_has_status_error_in_summary(self):
        """A scenario that raises must appear in summary with status='error'."""
        import subprocess
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}

        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=360)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                summary = run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

        assert summary["scenarios"][0]["status"] == "error"

    def test_error_json_saved_for_failed_scenario(self):
        """error.json must be written to the scenario dir when a scenario fails."""
        import subprocess
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}

        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=360)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            error_path = output_dir / "s1" / "error.json"
            assert error_path.exists()
            error_data = json.loads(error_path.read_text())
            assert "error" in error_data
            assert "exception_type" in error_data

    def test_summary_json_written_even_when_all_scenarios_fail(self):
        """summary.json must be written even if every scenario fails."""
        import subprocess

        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=360)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [SAMPLE_SCENARIO])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            assert (output_dir / "summary.json").exists()

    def test_marker_missing_does_not_crash_other_scenarios(self):
        """ValueError (missing marker) on scenario 1 must not prevent scenario 2."""
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}
        scenario2 = {**SAMPLE_SCENARIO, "id": "s2"}
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                broken_out = json.dumps({"result": "no markers here", "duration_ms": 1,
                                         "duration_api_ms": 1, "num_turns": 1,
                                         "total_cost_usd": 0.0,
                                         "usage": {"input_tokens": 0, "output_tokens": 0,
                                                   "cache_read_input_tokens": 0,
                                                   "cache_creation_input_tokens": 0}})
                return type("P", (), {"returncode": 0, "stdout": broken_out, "stderr": ""})()
            return self._make_valid_proc()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1, scenario2])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=self.FAKE_EVAL):
                summary = run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

        assert summary["total_scenarios"] == 2
        assert summary["scenarios"][0]["status"] == "error"
        assert summary["scenarios"][1].get("status") != "error"

    def test_trace_json_saved_on_marker_missing(self):
        """trace.json must be written even when marker parsing fails."""
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}
        raw_result_text = "no markers here"
        fake_trace = {
            "result": raw_result_text,
            "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1,
            "total_cost_usd": 0.0,
            "usage": {"input_tokens": 0, "output_tokens": 0,
                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
        }

        def side_effect(*args, **kwargs):
            return type("P", (), {"returncode": 0, "stdout": json.dumps(fake_trace), "stderr": ""})()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            trace_path = output_dir / "s1" / "trace.json"
            assert trace_path.exists(), "trace.json must be saved even on marker error"
            saved = json.loads(trace_path.read_text(encoding="utf-8"))
            assert saved["result"] == raw_result_text

    def test_trace_json_not_saved_on_timeout(self):
        """trace.json must NOT be written when subprocess.TimeoutExpired (no response available)."""
        import subprocess
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}

        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=360)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            trace_path = output_dir / "s1" / "trace.json"
            assert not trace_path.exists(), "trace.json must not be saved when there is no response"

    def test_trace_json_not_saved_on_nonzero_exit(self):
        """trace.json must NOT be written when claude exits non-zero (no parseable output)."""
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}

        def side_effect(*args, **kwargs):
            return type("P", (), {"returncode": 1, "stdout": "", "stderr": "error"})()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            trace_path = output_dir / "s1" / "trace.json"
            assert not trace_path.exists(), "trace.json must not be saved when claude exits non-zero"

    def test_raw_response_saved_on_marker_missing(self):
        """raw_response.txt must be written to the scenario dir when markers are missing."""
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}
        raw_result_text = "no markers here — raw LLM output"

        def side_effect(*args, **kwargs):
            broken_out = json.dumps({
                "result": raw_result_text,
                "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1,
                "total_cost_usd": 0.0,
                "usage": {"input_tokens": 0, "output_tokens": 0,
                          "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
            })
            return type("P", (), {"returncode": 0, "stdout": broken_out, "stderr": ""})()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            raw_path = output_dir / "s1" / "raw_response.txt"
            assert raw_path.exists(), "raw_response.txt must be saved on marker error"
            assert raw_result_text in raw_path.read_text(encoding="utf-8")

    def test_raw_response_not_saved_on_timeout(self):
        """raw_response.txt must NOT be written when subprocess.TimeoutExpired (no response available)."""
        import subprocess
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}

        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=360)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_e2e_all(str(scenarios_path), str(skill_dir), output_dir=str(output_dir))

            raw_path = output_dir / "s1" / "raw_response.txt"
            assert not raw_path.exists(), "raw_response.txt must not be saved when there is no response"


class TestMain:
    """Tests for main() CLI entrypoint."""

    def _make_valid_proc(self):
        return type("P", (), {"returncode": 0, "stdout": json.dumps({
            "result": self._make_valid_e2e_response(),
            "duration_ms": 1, "duration_api_ms": 1, "num_turns": 1,
            "total_cost_usd": 0.0,
            "usage": {"input_tokens": 0, "output_tokens": 0,
                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
        }), "stderr": ""})()

    def _make_valid_e2e_response(self):
        return (
            "<<<BENCHMARK_HEARING>>>\n{\"status\": \"skipped\", \"questions\": []}\n<<<END_BENCHMARK_HEARING>>>\n"
            "<<<BENCHMARK_SEARCH>>>\n{\"section_ids\": [\"f.json:s1\"]}\n<<<END_BENCHMARK_SEARCH>>>\n"
            "<<<BENCHMARK_ANSWER>>>\n回答\n<<<END_BENCHMARK_ANSWER>>>"
        )

    def _setup_skill_dir(self, tmpdir):
        skill_dir = Path(tmpdir) / "skill"
        (skill_dir / "workflows").mkdir(parents=True)
        (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")
        (skill_dir / "knowledge").mkdir()
        return skill_dir

    def _setup_scenarios(self, tmpdir, scenarios):
        path = Path(tmpdir) / "scenarios.json"
        path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
        return path

    FAKE_EVAL = {"must": [], "acceptable": [], "hallucination": []}

    def test_main_does_not_crash_when_scenario_has_error(self):
        """main() must not raise KeyError when summary contains error scenarios."""
        import sys
        from tools.benchmark.scripts.run_e2e import main
        scenario_ok = {**SAMPLE_SCENARIO, "id": "s1"}
        scenario_err = {**SAMPLE_SCENARIO, "id": "s2"}
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                broken = json.dumps({"result": "no markers", "duration_ms": 1,
                                     "duration_api_ms": 1, "num_turns": 1,
                                     "total_cost_usd": 0.0,
                                     "usage": {"input_tokens": 0, "output_tokens": 0,
                                               "cache_read_input_tokens": 0,
                                               "cache_creation_input_tokens": 0}})
                return type("P", (), {"returncode": 0, "stdout": broken, "stderr": ""})()
            return self._make_valid_proc()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario_ok, scenario_err])
            output_dir = Path(tmpdir) / "results"
            argv = ["run_e2e.py", "--scenarios", str(scenarios_path),
                    "--skill-dir", str(skill_dir)]
            with patch("subprocess.run", side_effect=side_effect), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=self.FAKE_EVAL), \
                 patch("tools.benchmark.scripts.run_e2e.default_output_dir", return_value=output_dir), \
                 patch.object(sys, "argv", argv):
                main()  # must not raise


class TestDefaultOutputDir:
    def test_default_output_dir_uses_timestamp(self):
        import re
        from tools.benchmark.scripts.run_e2e import default_output_dir
        result = default_output_dir()
        assert re.match(r".*/tools/benchmark/results/\d{8}-\d{6}$", str(result))

    def test_default_output_dir_is_under_results(self):
        from tools.benchmark.scripts.run_e2e import default_output_dir
        result = default_output_dir()
        assert "tools/benchmark/results/" in str(result)

    def test_default_output_dir_changes_each_second(self):
        import time
        from tools.benchmark.scripts.run_e2e import default_output_dir
        d1 = default_output_dir()
        time.sleep(1.1)
        d2 = default_output_dir()
        assert d1 != d2
