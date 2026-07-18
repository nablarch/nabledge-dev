# task-6 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| run-1 / run-2 / run-3 の選定シナリオ全件 × 3 runに error.json が存在しないこと | OK | `find tools/benchmark/results/20260625-1711-rag-k10-filter/ -name error.json` → 0件。run-2 (20260625-1756) / run-3 (20260625-1808) も同様 0件 | OK | Independently verified via find on all three run dirs — zero error.json files, all 8 scenario subdirs present. |
| crossrun-summary.md に選定シナリオ全件のスコアが記載されている | OK | `tools/benchmark/results/rag-k10-filter/crossrun-summary.md` に 8シナリオ全件（review-06, impact-08, qa-09, qa-11, qa-20, qa-14, oos-impact-01, oos-qa-01）の mean±sd が記載されている | OK | All values independently recalculated from raw evaluation.json — exact match. |
| quality-report.md に pass rate（数値）が含まれている | OK | `tools/benchmark/results/rag-k10-filter/quality-report.md` に「23/24」「24/24」の pass率が明記されている（全体サマリー表） | OK | 23/24/24/24 RAG and 24/24/23/24 Base numerically verified against raw scores. |
| quality-report.md に現行ベースライン（20260616-1214-fullbench-classes-v6）の同シナリオとの比較が含まれている | OK | quality-report.md の「ベースラインとのスコア比較」セクションに 8シナリオ全件の RAG vs Base スコア対比表（mean±SD）と「退行」セクションを含む | OK | All Base values verified against actual run data in baseline dir. Cost/time values confirmed from 8-scenario subset. |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | Section ② traces single correctness failure (qa-20 run-2) to specific missing must-section with 0/3 evidence; faithfulness low-scorers cross-checked against actual answer content; not just pass-through. |
| Edge case coverage | OK | OOS scenarios handled as no-must-section case; oos-impact-01 relevancy variance acknowledged; all below-threshold scores discussed even when clearing 0.7; discarded intermediate runs correctly excluded. |

## Expert Reviews (code changes only)

N/A — this task produces benchmark results and reports (docs), not code changes.

## Overall Verdict

- Self-check: OK
- QA: OK
- Language expert: N/A
- Software-engineering expert: N/A
- Ready for user review: Yes
