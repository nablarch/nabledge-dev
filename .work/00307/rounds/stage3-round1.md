# Stage 3 Round 1 — Section Select + Answer + Judge (Sonnet)

**Date**: 2026-04-22
**Scenarios**: 5 (qa-v6-sample5.json)
**Prompts**:
- AI-1: `tools/benchmark/prompts/stage1_facet.md` (Round 3)
- AI-2: `tools/benchmark/prompts/stage3_section_select.md` (PE-reviewed pre-run)
- AI-3: `tools/benchmark/prompts/stage3_answer.md` (PE-reviewed pre-run)
- Judge: `tools/benchmark/prompts/judge_stage3.md` (PE-reviewed pre-run)
**Model**: Sonnet (all stages)

## Flow

```
question
  → AI-1 (facet extract)
  → facet filter
  → AI-2 (section select, title+path+section-titles only, ≤10)
  → read_sections (script)
  → AI-3 (answer, cites path:section_id)
  → judge (4-level)
```

## Results

- mean judge level:       **3.00 / 3**
- level distribution:     `{0: 0, 1: 0, 2: 0, 3: 5}`
- mean candidate count:   **76.4 rows** (filter)
- mean AI-2 sections picked: **8.6** (range 6–10)
- fallback used:          **none** for all 5
- mean cost (USD):        **$0.557** (Stage 1 + AI-2 + AI-3 + judge combined)
- mean wall (s):          **81.5s**

| id | facets (type / cat) | filter | picks | judge | reason (excerpt) | cost | wall |
|----|---------------------|--------|-------|-------|------------------|------|------|
| review-01 | processing-pattern, component / nablarch-batch, libraries | 57 | 10 | 3 | 都度起動バッチ選択理由、ハンドラキュー構成、FormとDataRecordの役割分担... | $0.723 | 93.0s |
| review-04 | component, processing-pattern / libraries, web-application | 68 | 9 | 3 | Bean Validation + ドメインBeanへのルール集約（@Domain/@Required）... | $0.519 | 96.5s |
| impact-01 | component, processing-pattern / handlers, nablarch-batch | 67 | 8 | 3 | LoopHandler（commitInterval）とTransactionManagementHandlerの役割分担... | $0.497 | 68.6s |
| req-02 | processing-pattern, component / web-application, handlers, libraries | 124 | 10 | 3 | PermissionCheckHandlerとロールチェック(@CheckPermission)の組み合わせ... | $0.551 | 79.7s |
| req-09 | component, processing-pattern / handlers, restful-web-service | 66 | 6 | 3 | 標準機能なし。ServiceAvailabilityCheckHandlerとRESTful処理パターンが最近傍。 | $0.495 | 69.9s |

Full run: `tools/benchmark/.results/20260422-135336-stage3-sonnet/`

## Prompt Engineer Review

See [review-by-prompt-engineer-stage3-round1.md](../review-by-prompt-engineer-stage3-round1.md)

Rating: 4/5 for all three prompts. Applied fixes before committing:

- **High**: judge 「Expected-core × answer sentence」マッピング anti-verbosity チェック追加
- **High**: AI-2 セクション選択の実効上限 3–6、1ファイルから6以上は禁止
- **High**: AI-3 合成根拠は全起源セクションを cite するルール追加

Medium/Low fixes は 15件ランの前に適用予定。

## Assessment

- **End-to-end recall**: 5/5 at judge=3. Filter, AI-2, AI-3, judge すべて問題なし。
- **req-09 (not-built-in)**: not-built-in ルールが正しく発動。「標準機能なし + 最近傍」形式の回答で level 3。
- **Cost**: Stage 2 ($0.27) → Stage 3 ($0.56)、AI-2 + AI-3 の分だけ増加。Stage 3 は AI-3 単体でも大半を占める。
- **Wall**: 81.5s は現行フロー（review-04: 452秒）と比べ大幅改善。

## Decision

Stage 1 → 2 → 3 すべて 5/5 judge=3。
**次: 15件中間確認** に進む。
