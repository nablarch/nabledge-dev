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

    def test_no_hearing_answer(self):
        scenario_no_hearing = {
            **SAMPLE_SCENARIO,
            "when": {**SAMPLE_SCENARIO["when"], "hearing_answer": None},
        }
        prompt = build_e2e_prompt(scenario_no_hearing, self.workflow_content)
        assert "テスト質問です" in prompt

    def test_no_unreplaced_placeholders(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "{question}" not in prompt
        assert "{workflow}" not in prompt
        assert "{hearing_answer}" not in prompt

    def test_mode_current_excludes_hearing_answer(self):
        # current skill has no hearing — hearing_answer must not be injected
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content, mode="current")
        assert "Nablarchバッチ" not in prompt
        assert "バッチを起動する" not in prompt

    def test_mode_current_excludes_skip_instruction(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content, mode="current")
        assert "ヒアリングステップはスキップ" not in prompt

    def test_mode_new_includes_hearing_answer(self):
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content, mode="new")
        assert "Nablarchバッチ" in prompt
        assert "バッチを起動する" in prompt

    def test_default_mode_is_new(self):
        # backward compat: default behaviour unchanged
        prompt = build_e2e_prompt(SAMPLE_SCENARIO, self.workflow_content)
        assert "Nablarchバッチ" in prompt


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
    def test_saves_hearing_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "scenario_id": "pre-01",
                "hearing": {"status": "skipped", "questions": []},
                "search": {"section_ids": ["file.json:s1"]},
                "answer": "テスト回答",
                "metrics": DUMMY_METRICS,
            }
            save_e2e_results(tmpdir, "pre-01", data)
            hearing = json.loads((Path(tmpdir) / "pre-01" / "hearing.json").read_text())
            assert hearing["status"] == "skipped"

    def test_saves_search_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "scenario_id": "pre-01",
                "hearing": {"status": "skipped", "questions": []},
                "search": {"section_ids": ["file.json:s1"]},
                "answer": "テスト回答",
                "metrics": DUMMY_METRICS,
            }
            save_e2e_results(tmpdir, "pre-01", data)
            search = json.loads((Path(tmpdir) / "pre-01" / "search.json").read_text())
            assert "file.json:s1" in search["section_ids"]

    def test_saves_answer_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "scenario_id": "pre-01",
                "hearing": {"status": "skipped", "questions": []},
                "search": {"section_ids": []},
                "answer": "テスト回答テキスト",
                "metrics": DUMMY_METRICS,
            }
            save_e2e_results(tmpdir, "pre-01", data)
            answer = (Path(tmpdir) / "pre-01" / "answer.md").read_text()
            assert "テスト回答テキスト" in answer

    def test_saves_metrics_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "scenario_id": "pre-01",
                "hearing": {"status": "skipped", "questions": []},
                "search": {"section_ids": []},
                "answer": "回答",
                "metrics": DUMMY_METRICS,
            }
            save_e2e_results(tmpdir, "pre-01", data)
            metrics = json.loads((Path(tmpdir) / "pre-01" / "metrics.json").read_text())
            assert metrics["duration_ms"] == 45230
            assert metrics["total_cost_usd"] == 0.045

    def test_creates_scenario_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "scenario_id": "qa-001",
                "hearing": {"status": "skipped", "questions": []},
                "search": {"section_ids": []},
                "answer": "回答",
                "metrics": DUMMY_METRICS,
            }
            save_e2e_results(tmpdir, "qa-001", data)
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

    def test_returns_scenario_id(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            # Create minimal workflow
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert result["scenario_id"] == "pre-01"

    def test_returns_hearing(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert result["hearing"]["status"] == "skipped"

    def test_returns_search(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert "section_ids" in result["search"]

    def test_returns_answer(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert "テスト回答" in result["answer"]

    def test_returns_metrics(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert result["metrics"]["duration_ms"] == 45230
            assert result["metrics"]["total_cost_usd"] == 0.045

    def test_raises_on_nonzero_returncode(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 1,
                "stdout": "",
                "stderr": "Error occurred",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                with pytest.raises(RuntimeError, match="claude"):
                    run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

    def test_uses_skill_dir_as_cwd(self):
        """Ensure subprocess is called with skill_dir as cwd."""
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            call_kwargs = mock_run.call_args[1]
            assert str(call_kwargs.get("cwd", "")) == str(skill_dir)

    def test_uses_sonnet_model_by_default(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            cmd = mock_run.call_args[0][0]
            assert "sonnet" in cmd

    def test_uses_allowed_tools_as_specified(self):
        """--allowedTools must restrict Bash to the two workflow scripts."""
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            cmd = mock_run.call_args[0][0]
            allowed_tools_idx = cmd.index("--allowedTools")
            allowed_tools_value = cmd[allowed_tools_idx + 1]
            assert "Bash(keyword-search.sh *)" in allowed_tools_value
            assert "Bash(read-sections.sh *)" in allowed_tools_value
            assert "Read" in allowed_tools_value

    def test_uses_default_timeout_180(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc) as mock_run:
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            call_kwargs = mock_run.call_args[1]
            assert call_kwargs.get("timeout") == 180

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

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                result = run_e2e_scenario(SAMPLE_SCENARIO, skill_dir)

            assert "model_usage" in result["metrics"]
            assert result["metrics"]["model_usage"] == {}


    def test_mode_current_passed_to_build_prompt(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            captured_prompts = []

            def capture_run(*args, **kwargs):
                captured_prompts.append(kwargs.get("input", ""))
                return mock_proc

            with patch("subprocess.run", side_effect=capture_run):
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir, mode="current")

            assert "Nablarchバッチ" not in captured_prompts[0]

    def test_mode_new_passed_to_build_prompt(self):
        with tempfile.TemporaryDirectory() as skill_dir:
            Path(skill_dir, "workflows").mkdir(parents=True)
            (Path(skill_dir, "workflows") / "qa.md").write_text("# QA", encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            captured_prompts = []

            def capture_run(*args, **kwargs):
                captured_prompts.append(kwargs.get("input", ""))
                return mock_proc

            with patch("subprocess.run", side_effect=capture_run):
                run_e2e_scenario(SAMPLE_SCENARIO, skill_dir, mode="new")

            assert "Nablarchバッチ" in captured_prompts[0]


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

    def test_runs_all_scenarios(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "workflows").mkdir()
            (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")

            output_dir = Path(tmpdir) / "results"
            scenarios_data = {"scenarios": [SAMPLE_SCENARIO]}
            scenarios_path = Path(tmpdir) / "qa.json"
            scenarios_path.write_text(json.dumps(scenarios_data), encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                summary = run_e2e_all(str(scenarios_path), str(skill_dir), str(output_dir))

            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "pre-01"

    def test_filters_by_scenario_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "workflows").mkdir()
            (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")

            output_dir = Path(tmpdir) / "results"
            scenario2 = {**SAMPLE_SCENARIO, "id": "pre-02"}
            scenarios_data = {"scenarios": [SAMPLE_SCENARIO, scenario2]}
            scenarios_path = Path(tmpdir) / "qa.json"
            scenarios_path.write_text(json.dumps(scenarios_data), encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                summary = run_e2e_all(
                    str(scenarios_path), str(skill_dir), str(output_dir),
                    scenario_ids=["pre-01"]
                )

            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "pre-01"

    def test_saves_summary_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "workflows").mkdir()
            (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")

            output_dir = Path(tmpdir) / "results"
            scenarios_data = {"scenarios": [SAMPLE_SCENARIO]}
            scenarios_path = Path(tmpdir) / "qa.json"
            scenarios_path.write_text(json.dumps(scenarios_data), encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            with patch("subprocess.run", return_value=mock_proc):
                run_e2e_all(str(scenarios_path), str(skill_dir), str(output_dir))

            summary_path = output_dir / "summary.json"
            assert summary_path.exists()
            summary = json.loads(summary_path.read_text())
            assert summary["total_scenarios"] == 1

    def test_calls_evaluate_scenario_for_each_scenario(self):
        """run_e2e_all must call evaluate_scenario (step 4 in design doc E2E flow)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "workflows").mkdir()
            (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")
            knowledge_dir = Path(tmpdir) / "knowledge"
            knowledge_dir.mkdir()

            output_dir = Path(tmpdir) / "results"
            scenarios_data = {"scenarios": [SAMPLE_SCENARIO]}
            scenarios_path = Path(tmpdir) / "qa.json"
            scenarios_path.write_text(json.dumps(scenarios_data), encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            fake_eval = {"scenario_id": "pre-01", "scores": {"accuracy": 1.0, "hallucination": 1}}

            with patch("subprocess.run", return_value=mock_proc), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=fake_eval) as mock_eval:
                run_e2e_all(str(scenarios_path), str(skill_dir), str(output_dir),
                            knowledge_dir=str(knowledge_dir))

            assert mock_eval.call_count == 1

    def test_saves_evaluation_json(self):
        """run_e2e_all must save evaluation.json per scenario."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "skill"
            skill_dir.mkdir()
            (skill_dir / "workflows").mkdir()
            (skill_dir / "workflows" / "qa.md").write_text("# QA", encoding="utf-8")
            knowledge_dir = Path(tmpdir) / "knowledge"
            knowledge_dir.mkdir()

            output_dir = Path(tmpdir) / "results"
            scenarios_data = {"scenarios": [SAMPLE_SCENARIO]}
            scenarios_path = Path(tmpdir) / "qa.json"
            scenarios_path.write_text(json.dumps(scenarios_data), encoding="utf-8")

            mock_proc = type("P", (), {
                "returncode": 0,
                "stdout": self._make_claude_output(self._make_valid_e2e_response()),
                "stderr": "",
            })()

            fake_eval = {"scenario_id": "pre-01", "scores": {"accuracy": 1.0, "hallucination": 1}}

            with patch("subprocess.run", return_value=mock_proc), \
                 patch("tools.benchmark.scripts.run_e2e.evaluate_scenario", return_value=fake_eval):
                run_e2e_all(str(scenarios_path), str(skill_dir), str(output_dir),
                            knowledge_dir=str(knowledge_dir))

            eval_path = output_dir / "pre-01" / "evaluation.json"
            assert eval_path.exists()
            eval_data = json.loads(eval_path.read_text())
            assert eval_data["scenario_id"] == "pre-01"
