"""Tests for code analysis documentation format checker."""
import pytest

from tools.benchmark.scripts.check_format_code_analysis import check_format

# A minimal well-formed documentation that passes all checks
_WELL_FORMED = """\
# Code Analysis: W11AC02Action

## Overview

W11AC02ActionはDbAccessSupportを継承した登録処理アクションクラスです。
分析時間: 不明(ベンチマークモード)

## Architecture

```mermaid
classDiagram
    class W11AC02Action {
        +register(HttpRequest, ExecutionContext) HttpResponse
    }
    W11AC02Action --|> DbAccessSupport
```

## Flow

```mermaid
sequenceDiagram
    actor User
    participant W11AC02Action
    participant CM311AC1Component
    User->>W11AC02Action: POST /register
    W11AC02Action->>CM311AC1Component: registerUser(form, ctx)
    CM311AC1Component-->>W11AC02Action: void
    W11AC02Action-->>User: redirect
```

## Components

W11AC02ActionはCM311AC1Componentを呼び出してユーザーを登録します。

## Nablarch Framework Usage

ValidationUtilで入力バリデーションを行います。
@OnDoubleSubmissionで二重送信を防止します。

## References

- DbAccessSupport
- ValidationUtil
- CM311AC1Component
"""


class TestCheckFormat:
    def test_all_checks_pass_on_well_formed_content(self):
        result = check_format(_WELL_FORMED)
        assert result["passed"] is True
        assert result["checks"]["no_unreplaced_placeholders"] is True
        assert result["checks"]["all_sections_present"] is True
        assert result["checks"]["has_class_diagram"] is True
        assert result["checks"]["has_sequence_diagram"] is True

    def test_fails_no_unreplaced_placeholders_when_placeholder_present(self):
        content = _WELL_FORMED.replace("不明(ベンチマークモード)", "{{DURATION_PLACEHOLDER}}")
        result = check_format(content)
        assert result["checks"]["no_unreplaced_placeholders"] is False
        assert result["passed"] is False

    def test_details_lists_placeholder_name_on_failure(self):
        content = _WELL_FORMED.replace("W11AC02Action", "{{CLASS_NAME}}", 1)
        result = check_format(content)
        assert "{{CLASS_NAME}}" in result["details"]["no_unreplaced_placeholders"]

    def test_fails_all_sections_present_when_section_missing(self):
        # Remove the ## Flow section heading
        content = _WELL_FORMED.replace("## Flow\n", "")
        result = check_format(content)
        assert result["checks"]["all_sections_present"] is False
        assert result["passed"] is False

    def test_details_lists_missing_section_name(self):
        content = _WELL_FORMED.replace("## Components\n", "")
        result = check_format(content)
        assert "## Components" in result["details"]["all_sections_present"]

    def test_fails_has_class_diagram_when_no_class_diagram(self):
        # Replace classDiagram with something else
        content = _WELL_FORMED.replace("classDiagram", "erDiagram")
        result = check_format(content)
        assert result["checks"]["has_class_diagram"] is False
        assert result["passed"] is False

    def test_fails_has_sequence_diagram_when_no_sequence_diagram(self):
        # Replace sequenceDiagram with something else
        content = _WELL_FORMED.replace("sequenceDiagram", "flowchart TD")
        result = check_format(content)
        assert result["checks"]["has_sequence_diagram"] is False
        assert result["passed"] is False

    def test_class_diagram_must_be_inside_mermaid_block(self):
        # classDiagram outside a mermaid fence should not count
        content = _WELL_FORMED.replace("```mermaid\nclassDiagram", "```\nclassDiagram")
        result = check_format(content)
        assert result["checks"]["has_class_diagram"] is False

    def test_sequence_diagram_must_be_inside_mermaid_block(self):
        # sequenceDiagram outside a mermaid fence should not count
        content = _WELL_FORMED.replace("```mermaid\nsequenceDiagram", "```\nsequenceDiagram")
        result = check_format(content)
        assert result["checks"]["has_sequence_diagram"] is False

    def test_passed_is_false_when_any_check_fails(self):
        # Only remove the sequence diagram
        content = _WELL_FORMED.replace("sequenceDiagram", "flowchart LR")
        result = check_format(content)
        # Some checks pass, but passed must be False because one failed
        assert result["checks"]["has_class_diagram"] is True
        assert result["checks"]["all_sections_present"] is True
        assert result["checks"]["no_unreplaced_placeholders"] is True
        assert result["passed"] is False

    def test_passed_is_true_only_when_all_checks_pass(self):
        result = check_format(_WELL_FORMED)
        assert all(result["checks"].values())
        assert result["passed"] is True

    def test_returns_ok_in_details_for_passing_checks(self):
        result = check_format(_WELL_FORMED)
        for key, val in result["details"].items():
            assert val == "OK", f"Expected OK for {key}, got {val!r}"

    def test_multiple_placeholders_all_reported(self):
        content = _WELL_FORMED + "\n{{EXTRA1}} and {{EXTRA2}}"
        result = check_format(content)
        details = result["details"]["no_unreplaced_placeholders"]
        assert "{{EXTRA1}}" in details
        assert "{{EXTRA2}}" in details

    def test_empty_content_fails_all_section_and_diagram_checks(self):
        result = check_format("")
        assert result["checks"]["all_sections_present"] is False
        assert result["checks"]["has_class_diagram"] is False
        assert result["checks"]["has_sequence_diagram"] is False
        assert result["passed"] is False

    def test_unreplaced_placeholder_check_correct_rejection(self):
        """Fixture with an unreplaced placeholder must be rejected."""
        content = "# Code Analysis: {{TARGET_CLASS}}\n\n## Overview\nTest"
        result = check_format(content)
        assert result["checks"]["no_unreplaced_placeholders"] is False
        assert result["passed"] is False
