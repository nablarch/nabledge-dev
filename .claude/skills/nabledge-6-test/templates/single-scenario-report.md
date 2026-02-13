# Test Scenario Evaluation: {{scenario_id}}

**Date**: {{date}}
**Category**: {{category}}
**Status**: {{status}}

## Scenario Details

**Question**: {{question}}

**Expected Keywords**: {{expected_keywords}}
**Expected Sections**: {{expected_sections}}

## Execution Summary

**Duration**: {{duration}}
**Token Usage**: {{token_usage}}
**Tool Calls**: {{tool_call_count}}

## Evaluation Results

### 1. Workflow Execution: {{workflow_status}}

- {{workflow_keyword_search}} keyword-search workflow executed
- {{workflow_section_judgement}} section-judgement workflow executed
- {{workflow_tools}} Appropriate tools used

**Observations**: {{workflow_observations}}

### 2. Keyword Matching: {{keyword_score}}% ({{keyword_status}})

**Matched Keywords** ({{matched_count}}/{{total_count}}):
{{matched_keywords_list}}

**Observations**: {{keyword_observations}}

### 3. Section Relevance: {{section_status}}

**Sections Identified**:
{{sections_identified_list}}

**Expected Sections**:
{{expected_sections_list}}

**Observations**: {{section_observations}}

### 4. Knowledge File Only: {{knowledge_only_status}}

**Observations**: {{knowledge_only_observations}}

### 5. Token Efficiency: {{token_efficiency_status}}

**Target**: 5,000-15,000 tokens
**Actual**: {{actual_tokens}} tokens

**Observations**: {{token_efficiency_observations}}

### 6. Tool Call Efficiency: {{tool_efficiency_status}}

**Target**: 10-20 calls
**Actual**: {{actual_tool_calls}} calls

**Tool Call Breakdown**:
{{tool_call_breakdown}}

**Observations**: {{tool_efficiency_observations}}

## Response Analysis

**Response Length**: {{response_length}} characters

**Key Points from Response**:
{{response_key_points}}

## Improvement Suggestions

{{improvement_suggestions}}

## Overall Assessment

**Summary**: {{overall_summary}}

**Next Steps**: {{next_steps}}
