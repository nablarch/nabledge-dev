# Test Review: {scenario-file-name}

## Test Session Metadata

| Item | Value |
|------|-------|
| Test Date | {date} |
| Test Time | {time} |
| Test Directory | scenario-test-{hhmm} |
| Total Scenarios | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Partial | {partial} |

## Summary

### Overall Assessment

{overall_assessment_summary}

### Pass Rate

| Category | Pass Rate | Status |
|----------|-----------|--------|
| Workflow Execution | {percentage}% | {pass/warning/fail} |
| Output Quality | {percentage}% | {pass/warning/fail} |
| Knowledge Integration | {percentage}% | {pass/warning/fail} |
| Resource Efficiency | {percentage}% | {pass/warning/fail} |

## Detailed Results by Scenario

### {scenario-id-1}

**Status**: {PASS/FAIL/PARTIAL}

**Strengths**:
- {strength_1}
- {strength_2}

**Issues**:
- {issue_1}
- {issue_2}

**Metrics**:
- Tokens: {tokens} ({target_range})
- Tool Calls: {calls} ({target_range})

---

### {scenario-id-2}

{repeat for each scenario}

---

## Common Issues

### High Priority

1. **Issue**: {issue_description}
   - **Scenarios Affected**: {scenario_ids}
   - **Impact**: {impact_description}
   - **Recommendation**: {recommendation}

2. **Issue**: {issue_description}
   - **Scenarios Affected**: {scenario_ids}
   - **Impact**: {impact_description}
   - **Recommendation**: {recommendation}

### Medium Priority

{repeat structure}

### Low Priority

{repeat structure}

## Improvement Recommendations

### スキル構造の改善

#### 1. {improvement_area_1}

**現状の問題**:
{problem_description}

**改善案**:
{improvement_suggestion}

**期待される効果**:
{expected_benefit}

**実装優先度**: {High/Medium/Low}

---

#### 2. {improvement_area_2}

{repeat structure}

---

### ワークフローの改善

#### 1. {workflow_improvement_1}

**現状の問題**:
{problem_description}

**改善案**:
{improvement_suggestion}

**期待される効果**:
{expected_benefit}

**実装優先度**: {High/Medium/Low}

---

### 知識ファイルの改善

#### 1. {knowledge_improvement_1}

**対象ファイル**: {file_path}

**現状の問題**:
{problem_description}

**改善案**:
{improvement_suggestion}

**期待される効果**:
{expected_benefit}

**実装優先度**: {High/Medium/Low}

---

### パフォーマンス最適化

#### Token Usage

**現状**:
- 平均: {average} tokens
- 最大: {max} tokens
- 目標範囲: {target_range}

**改善案**:
{optimization_suggestions}

---

#### Tool Call Efficiency

**現状**:
- 平均: {average} calls
- 最大: {max} calls
- 目標範囲: {target_range}

**改善案**:
{optimization_suggestions}

---

## Action Items

### Immediate (実装必須)

- [ ] {action_item_1}
- [ ] {action_item_2}

### Short-term (1週間以内)

- [ ] {action_item_1}
- [ ] {action_item_2}

### Long-term (1ヶ月以内)

- [ ] {action_item_1}
- [ ] {action_item_2}

## Next Steps

1. {next_step_1}
2. {next_step_2}
3. {next_step_3}

## Appendix

### Test Environment

- Claude Model: {model_version}
- Skill Version: {skill_version}
- Test Framework Version: {framework_version}

### Reference

- Test Scenarios: `{scenario_file_path}`
- Test Results: `scenario-test-{hhmm}/`
- Previous Review: `{previous_review_path}` (if applicable)
