# Task #4 Self-Check: v6 QA run-1 stability

**Date**: 2026-07-08
**Result**: OK

## Completion criteria check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| QA run-1（全シナリオ）が終了コード0で完了 | ✅ OK | 34/34 scenarios completed, 0 errors in summary.json |
| run-1の全シナリオ answer.md に bare `file.json:sN` が残っていない | ✅ OK | `grep -r "\.json:s[0-9]" .../run-1/*/answer.md` → no matches |
| run-1の全シナリオ answer.md に `#anchor` が含まれない | ✅ OK | All `#` occurrences are Java method references (e.g., `Class#method`), not URL anchors |

## Run details

- Run label: `20260708-1153-section-links-v6`
- Scenarios: 34/34 completed (28 from main batch + 6 supplemental)
- Report: `tools/benchmark/results/20260708-1153-section-links-v6/run-1/report.md`
- answer_correctness avg: 0.92 (29/34 pass ≥0.99)
- answer_relevancy avg: 0.97 (29/34 pass ≥0.95)
- faithfulness avg: 0.97 (22/34 pass ≥0.99)
