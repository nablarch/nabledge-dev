# Stage 2 Round 1 — Facet Filter + LLM Judge (Sonnet)

**Date**: 2026-04-22
**Scenarios**: 5 (qa-v6-sample5.json)
**AI-1 prompt**: `tools/benchmark/prompts/stage1_facet.md` (Round 3 version)
**Judge prompt**: `tools/benchmark/prompts/judge_stage2.md`
**Model**: Sonnet (both AI-1 and judge)
**Filter**: `tools/benchmark/filter/facet_filter.py`

## Flow

```
question
  → AI-1 (facet extract: type / category / coverage)
  → facet_filter.filter_with_fallback(rows, want_type, want_category)
  → judge (title + path only, 4-level rubric)
```

## Results

- mean judge level:       **3.00 / 3**
- level distribution:     `{0: 0, 1: 0, 2: 0, 3: 5}`
- mean candidate count:   **76.4 rows**  (min 57, max 124)
- fallback used:          **none** (all 5 primary AND-filter hit)
- mean cost (USD):        **$0.081** (Stage 1 + filter + judge combined)
- mean wall (s):          **27.7s**

| id | facets (type / cat) | filter | judge | reason (excerpt) | cost | wall |
|----|---------------------|--------|-------|------------------|------|------|
| review-01 | processing-pattern, component / nablarch-batch, libraries | 57 (none) | 3 | 「ファイルをDBに登録するバッチの作成」が質問に直接対応する一次ファイル。アーキテクチャ概要・責務配置・機能詳細でNablarchバッチの推奨構成を網羅。 | $0.159 | 24.0s |
| review-04 | component, processing-pattern / libraries, web-application | 68 (none) | 3 | Primary files present: 入力値のチェック (libraries-validation), Bean Validation, Nablarch Validation, and comparison file. Error display and implementation examples also included. | $0.061 | 28.5s |
| impact-01 | component, processing-pattern / handlers, nablarch-batch | 67 (none) | 3 | Two primary files for this question are both present: transaction_management_handler and database_connection_management_handler. | $0.060 | 25.5s |
| req-02 | processing-pattern, component / web-application, handlers, libraries | 124 (none) | 3 | All primary files are present: 認可チェックハンドラ (handlers-permission_check_handler), plus web-application pattern details and libraries support. | $0.063 | 26.5s |
| req-09 | component, processing-pattern / handlers, restful-web-service | 66 (none) | 3 | Rate limiting is not a Nablarch built-in. Per the not-built-in rule, near-neighbor files (handlers, REST) are sufficient — judge accepts the list. | $0.064 | 34.0s |

Full run: `tools/benchmark/.results/20260422-123225-stage2-sonnet/`

## Technical notes (run.py fix)

During the first run (`20260422-122904-stage2-sonnet`), 3/5 scenarios (review-04,
impact-01, req-09) reported `judge=None` with `claude exited 1`.

**Root cause**: Claude CLI returned `subtype=error_max_turns` with `is_error=true`
after the model emitted a valid `StructuredOutput` tool_use, because the schema
re-validation on the following turn produced the max_turns limit. The `result`
envelope did not include a `structured_output` field even though the stream
contained the correct JSON.

**Fix**: `invoke_claude_stream` now:
1. Parses `assistant` events for `StructuredOutput` tool_use blocks and
   captures their `input` as a fallback source.
2. Reports success when structured output was captured, even if the CLI
   exited non-zero with `subtype=error_max_turns`.

Committed as `96402a071 fix(benchmark): recover structured output on error_max_turns`.

Re-run confirmed all 5 scenarios return valid levels.

## Assessment

- **Recall**: 100% (every scenario's required files are in the filter output).
- **Judge calibration**: Matches expected outcomes — the 4-level rubric's
  not-built-in directive correctly handled req-09 (rate limiting) as level 3
  on near-neighbors, per the prompt rule.
- **Filter efficiency**: 57–124 rows out of 295 (19%–42% of index). No
  scenario triggered fallback — primary AND-filter was adequate on all 5.
- **Cost**: Mean $0.081 end-to-end (AI-1 + judge). Judge-only cost ≈ $0.05.

## Prompt Engineer Review

See [review-by-prompt-engineer-stage2-round1.md](../review-by-prompt-engineer-stage2-round1.md)

Rating: 4/5. Applied fixes:

- **High**: Added "primary file" definition (expert's first-opened file, not context).
- **High**: Required reason format `Expected primaries: [...]. Present: [...]. {verdict}.`
- **Medium**: Added title-fit bar — surface-keyword overlap alone does not qualify.
- **Low**: Reason must match question language (JP→JP / EN→EN).
- **Low**: Added a worked not-built-in example inline.

### Re-run after prompt hardening

Full run: `tools/benchmark/.results/20260422-123658-stage2-sonnet/`

- mean judge level: **3.00**, distribution `{3: 5}` (unchanged — no regression)
- mean cost: **$0.268** (up from $0.081 due to format compliance turns)
- mean wall: **30.2s**
- Reasons now uniformly follow the required "Expected primaries / Present" shape,
  in the question's language. Audit trail greatly improved.

## Decision

Proceed to **Stage 3** (AI-2 section select + final answer + judge).
