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
    call_llm,
    determine_human_review_items,
    evaluate_all,
    evaluate_scenario,
    extract_json_from_result,
    load_page_content,
    load_runner_output,
    load_section_content,
    parse_claim_response,
    parse_hallucination_response,
    parse_section_ref,
)

DUMMY_METRICS = {
    "duration_ms": 100,
    "duration_api_ms": 90,
    "total_cost_usd": 0.001,
    "usage": {"input_tokens": 500, "output_tokens": 50},
}


def _wrap_llm_response(result, metrics=None):
    return {"result": result, "metrics": metrics or DUMMY_METRICS}


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

    def test_uncertain_returns_none(self):
        # Design spec: UNCERTAIN-containing scenarios are excluded from aggregation (score=None)
        verdicts = [
            {"verdict": "PRESENT"},
            {"verdict": "UNCERTAIN"},
        ]
        assert calculate_accuracy_score(verdicts) is None

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
        assert "hallucination" in prompt
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
            if "fact-check judge" in prompt:
                call_count["claim"] += 1
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "含まれている"})
            else:
                call_count["hallucination"] += 1
                return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "問題なし"})

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
            _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"}),
            _wrap_llm_response({"verdict": "UNCERTAIN", "reason": "unclear"}),
            _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"}),
        ])

        def mock_llm(prompt, json_schema):
            return next(responses)

        def mock_load_section(knowledge_dir, ref):
            return "内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy", mock_llm,
            section_loader=mock_load_section,
        )
        # UNCERTAIN present → score is None (excluded from aggregation per design spec)
        assert result["scores"]["accuracy"] is None
        assert result["needs_human_review"] is True
        assert len(result["human_review_items"]) == 1

    def test_no_must_facts(self):
        scenario = {
            "id": "test-03",
            "then": {"must": [], "acceptable": []},
        }
        runner_output = {"answer": "回答", "hearing": {}, "search": {}, "metrics": {}}

        def mock_llm(prompt, json_schema):
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            return "内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy", mock_llm,
            section_loader=mock_load_section,
        )
        assert result["scores"]["accuracy"] is None
        assert result["scores"]["hallucination"] == 1


    def test_out_of_scope_fact_without_section(self):
        # out-of-scope scenarios have must facts with no section reference
        scenario = {
            "id": "oos-01",
            "then": {
                "must": [{"fact": "NablarchにはOAuth2認証の組み込み機能がないと回答している"}],
                "acceptable": [],
            },
        }
        runner_output = {"answer": "NablarchにOAuth2の機能はありません", "hearing": {}, "search": {}, "metrics": {}}

        section_loader_called_with = []

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "回答に含まれている"})
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            section_loader_called_with.append(ref)
            return "内容"

        result = evaluate_scenario(
            scenario, runner_output, "/dummy", mock_llm,
            section_loader=mock_load_section,
        )
        # section_loader must not be called (no section reference)
        assert section_loader_called_with == []
        assert result["scores"]["accuracy"] == 1.0

    def test_search_sections_eliminate_false_positive(self):
        # Claim supported by a non-retrieved section of a retrieved page → should PASS
        # (page-level loading: all sections of b.json are passed to hallucination judge)
        scenario = {
            "id": "fp-01",
            "then": {
                "must": [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }
        runner_output = {
            "answer": "回答",
            "hearing": {},
            "search": {"section_ids": ["b.json:s2"]},
            "metrics": {},
        }

        loaded_pages = []

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"})
            # hallucination judge: full page content of b.json should be in prompt
            assert "b.jsonの全内容" in prompt
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            return f"{ref}の内容"

        def mock_load_page(knowledge_dir, file_path):
            loaded_pages.append(file_path)
            return f"{file_path}の全内容"

        evaluate_scenario(scenario, runner_output, "/dummy", mock_llm,
                          section_loader=mock_load_section, page_loader=mock_load_page)
        assert "b.json" in loaded_pages

    def test_search_sections_true_hallucination_still_caught(self):
        # Claim unsupported by both must_facts and search_sections → should FAIL
        scenario = {
            "id": "th-01",
            "then": {
                "must": [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }
        runner_output = {
            "answer": "回答",
            "hearing": {},
            "search": {"section_ids": ["b.json:s2"]},
            "metrics": {},
        }

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"})
            return _wrap_llm_response({
                "verdict": "FAIL",
                "claims": [{"claim": "捏造事実", "supported": False}],
                "reason": "裏付けなし",
            })

        def mock_load_section(knowledge_dir, ref):
            return f"{ref}の内容"

        result = evaluate_scenario(scenario, runner_output, "/dummy", mock_llm,
                                   section_loader=mock_load_section)
        assert result["scores"]["hallucination"] == 0

    def test_search_sections_deduplication(self):
        # A section in both must_facts and search_sections → loaded exactly once
        scenario = {
            "id": "dup-01",
            "then": {
                "must": [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }
        runner_output = {
            "answer": "回答",
            "hearing": {},
            "search": {"section_ids": ["a.json:s1"]},  # duplicate
            "metrics": {},
        }

        load_count = {"a.json:s1": 0}

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"})
            # content should appear exactly once (no duplicate --- block)
            count = prompt.count("a.json:s1の内容")
            assert count == 1, f"Section content duplicated {count} times"
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            load_count[ref] = load_count.get(ref, 0) + 1
            return f"{ref}の内容"

        evaluate_scenario(scenario, runner_output, "/dummy", mock_llm,
                          section_loader=mock_load_section)
        # The in-prompt assertion in mock_llm verifies deduplication

    def test_search_sections_empty(self):
        # Empty search_sections → behavior identical to current (no crash)
        scenario = {
            "id": "empty-01",
            "then": {
                "must": [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }
        runner_output = {
            "answer": "回答",
            "hearing": {},
            "search": {"section_ids": []},
            "metrics": {},
        }

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"})
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            return f"{ref}の内容"

        result = evaluate_scenario(scenario, runner_output, "/dummy", mock_llm,
                                   section_loader=mock_load_section)
        assert result["scores"]["hallucination"] == 1

    def test_search_sections_unresolvable_ref_skipped(self):
        # Unresolvable search_section ref → silently skipped, no crash
        scenario = {
            "id": "skip-01",
            "then": {
                "must": [{"fact": "fact1", "section": "a.json:s1"}],
                "acceptable": [],
            },
        }
        runner_output = {
            "answer": "回答",
            "hearing": {},
            "search": {"section_ids": ["nonexistent.json:s99"]},
            "metrics": {},
        }

        def mock_llm(prompt, json_schema):
            if "fact-check judge" in prompt:
                return _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"})
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        def mock_load_section(knowledge_dir, ref):
            if ref == "nonexistent.json:s99":
                raise FileNotFoundError(f"not found: {ref}")
            return f"{ref}の内容"

        result = evaluate_scenario(scenario, runner_output, "/dummy", mock_llm,
                                   section_loader=mock_load_section)
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
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        with patch("tools.benchmark.scripts.evaluate.call_llm", mock_llm):
            results = evaluate_all(tmpdir, str(scenarios_path), "/dummy")

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
            return _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"})

        with patch("tools.benchmark.scripts.evaluate.call_llm", mock_llm):
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

        # full_prompt must NOT appear in the command list
        assert not any("test prompt" in str(arg) for arg in captured["cmd"]), (
            "full_prompt must not be passed as a CLI argument (causes OSError on long prompts)"
        )
        # full_prompt must be passed via stdin
        assert captured["input"] is not None, "prompt must be passed via stdin (input=)"
        assert "test prompt" in captured["input"]
