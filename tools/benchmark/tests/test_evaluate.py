"""Tests for benchmark evaluation logic."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.benchmark.scripts.evaluate import (
    build_claim_prompt,
    build_hallucination_prompt,
    calculate_accuracy_score,
    calculate_hallucination_score,
    determine_human_review_items,
    evaluate_all,
    evaluate_scenario,
    load_runner_output,
    load_section_content,
    parse_claim_response,
    parse_hallucination_response,
    parse_section_ref,
)


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


class TestCalculateAccuracyScore:
    def test_all_present(self):
        verdicts = [
            {"verdict": "PRESENT"},
            {"verdict": "PRESENT"},
        ]
        assert calculate_accuracy_score(verdicts) == 1.0

    def test_mixed_verdicts(self):
        verdicts = [
            {"verdict": "PRESENT"},
            {"verdict": "ABSENT"},
        ]
        assert calculate_accuracy_score(verdicts) == 0.5

    def test_all_absent(self):
        verdicts = [
            {"verdict": "ABSENT"},
            {"verdict": "ABSENT"},
        ]
        assert calculate_accuracy_score(verdicts) == 0.0

    def test_uncertain_not_counted_as_present(self):
        verdicts = [
            {"verdict": "PRESENT"},
            {"verdict": "UNCERTAIN"},
        ]
        assert calculate_accuracy_score(verdicts) == 0.5

    def test_empty_returns_none(self):
        assert calculate_accuracy_score([]) is None


class TestCalculateHallucinationScore:
    def test_pass(self):
        assert calculate_hallucination_score({"verdict": "PASS"}) == 1

    def test_fail(self):
        assert calculate_hallucination_score({"verdict": "FAIL"}) == 0

    def test_uncertain(self):
        assert calculate_hallucination_score({"verdict": "UNCERTAIN"}) is None


class TestDetermineHumanReviewItems:
    def test_no_review_needed(self):
        claims = [{"fact": "f1", "verdict": "PRESENT", "reason": "ok"}]
        hallucination = {"verdict": "PASS", "claims": [], "reason": "ok"}
        items = determine_human_review_items(claims, hallucination)
        assert items == []

    def test_uncertain_claim(self):
        claims = [{"fact": "f1", "verdict": "UNCERTAIN", "reason": "unclear"}]
        hallucination = {"verdict": "PASS", "claims": [], "reason": "ok"}
        items = determine_human_review_items(claims, hallucination)
        assert len(items) == 1
        assert "UNCERTAIN" in items[0]

    def test_absent_claim(self):
        claims = [{"fact": "f1", "verdict": "ABSENT", "reason": "not found"}]
        hallucination = {"verdict": "PASS", "claims": [], "reason": "ok"}
        items = determine_human_review_items(claims, hallucination)
        assert len(items) == 1
        assert "ABSENT" in items[0]

    def test_hallucination_fail(self):
        claims = [{"fact": "f1", "verdict": "PRESENT", "reason": "ok"}]
        hallucination = {"verdict": "FAIL", "claims": [{"claim": "fake", "supported": False}], "reason": "fabricated"}
        items = determine_human_review_items(claims, hallucination)
        assert len(items) == 1
        assert "FAIL" in items[0]

    def test_hallucination_uncertain(self):
        claims = []
        hallucination = {"verdict": "UNCERTAIN", "claims": [], "reason": "unclear"}
        items = determine_human_review_items(claims, hallucination)
        assert len(items) == 1
        assert "UNCERTAIN" in items[0]

    def test_multiple_review_items(self):
        claims = [
            {"fact": "f1", "verdict": "ABSENT", "reason": "not found"},
            {"fact": "f2", "verdict": "UNCERTAIN", "reason": "unclear"},
            {"fact": "f3", "verdict": "PRESENT", "reason": "ok"},
        ]
        hallucination = {"verdict": "FAIL", "claims": [{"claim": "x", "supported": False}], "reason": "bad"}
        items = determine_human_review_items(claims, hallucination)
        assert len(items) == 3  # ABSENT + UNCERTAIN + hallucination FAIL


class TestBuildClaimPrompt:
    def test_contains_all_fields(self):
        prompt = build_claim_prompt(
            fact="テスト事実",
            answer="テスト回答",
            section_content="テストセクション内容",
        )
        assert "テスト事実" in prompt
        assert "テスト回答" in prompt
        assert "テストセクション内容" in prompt
        assert "PRESENT" in prompt
        assert "ABSENT" in prompt
        assert "UNCERTAIN" in prompt


class TestBuildHallucinationPrompt:
    def test_contains_all_fields(self):
        prompt = build_hallucination_prompt(
            answer="テスト回答",
            sections_content="セクション1\nセクション2",
        )
        assert "テスト回答" in prompt
        assert "セクション1" in prompt
        assert "ハルシネーション" in prompt
        assert "Nablarch" in prompt


class TestParseClaimResponse:
    def test_parse_present(self):
        response = {"verdict": "PRESENT", "reason": "回答に含まれている"}
        result = parse_claim_response(response)
        assert result["verdict"] == "PRESENT"
        assert result["reason"] == "回答に含まれている"

    def test_parse_absent(self):
        response = {"verdict": "ABSENT", "reason": "回答に含まれていない"}
        result = parse_claim_response(response)
        assert result["verdict"] == "ABSENT"

    def test_parse_uncertain(self):
        response = {"verdict": "UNCERTAIN", "reason": "判定困難"}
        result = parse_claim_response(response)
        assert result["verdict"] == "UNCERTAIN"

    def test_invalid_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            parse_claim_response({"verdict": "MAYBE", "reason": "x"})

    def test_missing_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            parse_claim_response({"reason": "x"})


class TestParseHallucinationResponse:
    def test_parse_pass(self):
        response = {"verdict": "PASS", "claims": [], "reason": "問題なし"}
        result = parse_hallucination_response(response)
        assert result["verdict"] == "PASS"
        assert result["claims"] == []

    def test_parse_fail_with_claims(self):
        response = {
            "verdict": "FAIL",
            "claims": [{"claim": "偽API名", "supported": False}],
            "reason": "捏造あり",
        }
        result = parse_hallucination_response(response)
        assert result["verdict"] == "FAIL"
        assert len(result["claims"]) == 1

    def test_invalid_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            parse_hallucination_response({"verdict": "BAD", "claims": [], "reason": "x"})

    def test_missing_verdict_raises(self):
        with pytest.raises(ValueError, match="verdict"):
            parse_hallucination_response({"claims": [], "reason": "x"})


class TestLoadRunnerOutput:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        scenario_dir = Path(self.tmpdir) / "pre-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("テスト回答です", encoding="utf-8")
        (scenario_dir / "hearing.json").write_text(
            json.dumps({"status": "skipped", "questions": []}), encoding="utf-8"
        )
        (scenario_dir / "search.json").write_text(
            json.dumps({"section_ids": ["a.json:s1"]}), encoding="utf-8"
        )
        (scenario_dir / "metrics.json").write_text(
            json.dumps({"duration_ms": 1000, "total_tokens": 500, "tool_uses": 3}),
            encoding="utf-8",
        )

    def test_load_all_outputs(self):
        output = load_runner_output(self.tmpdir, "pre-01")
        assert output["answer"] == "テスト回答です"
        assert output["hearing"]["status"] == "skipped"
        assert output["search"]["section_ids"] == ["a.json:s1"]
        assert output["metrics"]["duration_ms"] == 1000

    def test_missing_scenario_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_runner_output(self.tmpdir, "nonexistent")


class TestEvaluateScenario:
    def test_all_present_no_hallucination(self):
        scenario = {
            "id": "test-01",
            "then": {
                "must": [
                    {"fact": "fact1", "section": "a.json:s1"},
                    {"fact": "fact2", "section": "a.json:s2"},
                ],
                "acceptable": [{"section": "a.json:s3"}],
            },
        }
        runner_output = {"answer": "テスト回答", "hearing": {}, "search": {}, "metrics": {}}

        call_count = {"claim": 0, "hallucination": 0}

        def mock_llm(prompt, json_schema):
            if "ファクトチェック" in prompt:
                call_count["claim"] += 1
                return {"verdict": "PRESENT", "reason": "含まれている"}
            else:
                call_count["hallucination"] += 1
                return {"verdict": "PASS", "claims": [], "reason": "問題なし"}

        def mock_load_section(knowledge_dir, ref):
            return "セクション内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy/knowledge", mock_llm,
            section_loader=mock_load_section,
        )
        assert result["scenario_id"] == "test-01"
        assert result["scores"]["accuracy"] == 1.0
        assert result["scores"]["hallucination"] == 1
        assert result["needs_human_review"] is False
        assert call_count["claim"] == 2
        assert call_count["hallucination"] == 1

    def test_mixed_verdicts_with_review_needed(self):
        scenario = {
            "id": "test-02",
            "then": {
                "must": [
                    {"fact": "fact1", "section": "a.json:s1"},
                    {"fact": "fact2", "section": "a.json:s2"},
                ],
                "acceptable": [],
            },
        }
        runner_output = {"answer": "回答", "hearing": {}, "search": {}, "metrics": {}}

        responses = iter([
            {"verdict": "PRESENT", "reason": "ok"},
            {"verdict": "UNCERTAIN", "reason": "unclear"},
            {"verdict": "PASS", "claims": [], "reason": "ok"},
        ])

        def mock_llm(prompt, json_schema):
            return next(responses)

        def mock_load_section(knowledge_dir, ref):
            return "内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy", mock_llm,
            section_loader=mock_load_section,
        )
        assert result["scores"]["accuracy"] == 0.5
        assert result["needs_human_review"] is True
        assert len(result["human_review_items"]) == 1

    def test_no_must_facts(self):
        scenario = {
            "id": "test-03",
            "then": {"must": [], "acceptable": []},
        }
        runner_output = {"answer": "回答", "hearing": {}, "search": {}, "metrics": {}}

        def mock_llm(prompt, json_schema):
            return {"verdict": "PASS", "claims": [], "reason": "ok"}

        def mock_load_section(knowledge_dir, ref):
            return "内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy", mock_llm,
            section_loader=mock_load_section,
        )
        assert result["scores"]["accuracy"] is None
        assert result["scores"]["hallucination"] == 1


class TestEvaluateAll:
    def test_skips_missing_scenario_dir(self):
        tmpdir = tempfile.mkdtemp()
        # Create runner output for pre-01 only (not pre-02)
        scenario_dir = Path(tmpdir) / "pre-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("テスト回答", encoding="utf-8")
        (scenario_dir / "hearing.json").write_text(
            json.dumps({"status": "skipped", "questions": []}), encoding="utf-8"
        )
        (scenario_dir / "search.json").write_text(
            json.dumps({"section_ids": []}), encoding="utf-8"
        )
        (scenario_dir / "metrics.json").write_text(
            json.dumps({"duration_ms": 1000, "total_tokens": 500, "tool_uses": 3}),
            encoding="utf-8",
        )
        # Create minimal scenarios JSON
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

        def mock_llm(prompt, schema, model="sonnet"):
            return {"verdict": "PASS", "claims": [], "reason": "ok"}

        with patch("tools.benchmark.scripts.evaluate.call_llm", mock_llm):
            results = evaluate_all(tmpdir, str(scenarios_path), "/dummy", "sonnet")

        assert len(results) == 1
        assert results[0]["scenario_id"] == "pre-01"
        # Verify evaluation.json was written
        eval_path = scenario_dir / "evaluation.json"
        assert eval_path.exists()

    def test_writes_evaluation_json(self):
        tmpdir = tempfile.mkdtemp()
        scenario_dir = Path(tmpdir) / "test-01"
        scenario_dir.mkdir()
        (scenario_dir / "answer.md").write_text("回答テキスト", encoding="utf-8")
        (scenario_dir / "hearing.json").write_text(
            json.dumps({"status": "skipped", "questions": []}), encoding="utf-8"
        )
        (scenario_dir / "search.json").write_text(
            json.dumps({"section_ids": []}), encoding="utf-8"
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

        def mock_llm(prompt, schema, model="sonnet"):
            return {"verdict": "PASS", "claims": [], "reason": "ok"}

        with patch("tools.benchmark.scripts.evaluate.call_llm", mock_llm):
            evaluate_all(tmpdir, str(scenarios_path), "/dummy", "sonnet")

        eval_path = scenario_dir / "evaluation.json"
        with open(eval_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["scenario_id"] == "test-01"
        assert "scores" in data
