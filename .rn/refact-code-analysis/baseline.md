# Baseline: code-analysis benchmark scores

**Captured**: 2026-07-01  
**Workflow**: `code-analysis.md` (current, unmodified — 685 lines)  
**Scenarios**: `tools/benchmark/scenarios/code-analysis.json` (3 scenarios)  
**Results dir**: `tools/benchmark/results/code-analysis-baseline/`

## Summary Table

| Scenario | Input class | answer_correctness | answer_relevancy | faithfulness | Format check |
|---|---|---|---|---|---|
| ca-01 | W11AC02Action | 1.000 | 0.964 | 1.000 | PASS |
| ca-02 | W11AC01Action | 1.000 | 1.000 | 1.000 | PASS |
| ca-03 | CM311AC1Component | 1.000 | 0.930 | 1.000 | PASS |

## Format Check Details

All scenarios passed all 4 format checks:
- `no_unreplaced_placeholders`: OK
- `all_sections_present`: OK (all 7 required headings present)
- `has_class_diagram`: OK
- `has_sequence_diagram`: OK

## DeepEval Score Notes

- **answer_correctness** = 1.000 for all scenarios: all expected facts are covered
- **answer_relevancy** slightly below 1.0 for ca-01 (0.964) and ca-03 (0.930): evaluator noted benchmark-mode metadata (analysis duration, output file path) as irrelevant to the question
- **faithfulness** = 1.000 for all scenarios: no contradictions with retrieval context

## Per-Scenario Details

### ca-01 (W11AC02Action)
- Turns: 16, Cost: $0.664, Duration: 181s
- Expected facts all covered: DbAccessSupport inheritance, @OnDoubleSubmission, ValidationUtil

### ca-02 (W11AC01Action)
- Turns: 27, Cost: $0.860, Duration: 199s
- Expected facts all covered: DbAccessSupport inheritance, DataRecordResponse CSV, CodeUtil

### ca-03 (CM311AC1Component)
- Turns: 13, Cost: $0.583, Duration: 157s
- Expected facts all covered: DbAccessSupport inheritance, IdGeneratorUtil, AuthenticationUtil
