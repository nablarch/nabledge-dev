# Expert Review: Prompt Engineer (Stage 1 Round 1)

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Target**: `tools/benchmark/prompts/stage1_extract.md` + execution options + judging method
**Rating**: 3/5

## Overall Assessment

The prompt is minimal and runs cleanly, but it under-specifies the target vocabulary (Nablarch document terms) and leaves granularity up to the model, which drove review-01 to 0.40 recall. The judging method amplifies the problem by rewarding literal substring hits over semantic coverage, so the recall number understates actual keyword quality (e.g., req-02 "permission" mismatch is judge-side, not agent-side). Fixable with targeted prompt additions and a tighter judging contract — no architectural change needed.

## Key Issues

### H1. [High] Prompt does not anchor keywords to Nablarch document vocabulary

**Description**: Prompt gives no guidance on what terminology the knowledge base actually uses. Model picks specific implementation names (`DataReader`, `UniversalDao`) when docs use abstract headings (`ファイル入出力`, `データバインド`). BM25 then misses relevant sections.

**Proposed fix**: Add guidance block:
```
## Guidance
Nablarch documentation is organized around these axes. For each relevant axis,
include the abstract axis term AND one concrete implementation term:
- 機能カテゴリ (例: ファイル入出力, データベースアクセス, バリデーション, 認可, トランザクション制御)
- 実行形態 (例: 都度起動バッチ, 常駐バッチ, ウェブ, RESTfulウェブサービス)
- 具象クラス/アノテーション (例: UniversalDao, @UseToken, Permission)
- 対概念があれば両方 (コミット↔ロールバック, 認証↔認可, 開始↔終了)
```

Addresses review-01 (granularity mismatch) and impact-01 (missed paired concept ロールバック) in one change.

### H2. [High] Judging method confuses "prompt quality" with "judge lexical rigidity"

**Description**: Bidirectional substring, lowercased, rejects `Permission` vs `permission` semantic match. req-02's "missed permission" is a judge artifact, not agent failure. Makes recall unreliable.

**Proposed fix (prioritized)**:
1. **Cheapest**: normalize `expected_keywords` at scenario-definition time to lowercase ASCII + NFKC → keep bidirectional substring. Fixes req-02 for free.
2. **Next**: per-scenario synonym map (`expected_keywords_synonyms: {"RESTfulウェブサービス": ["REST API", "REST"]}`) — deterministic, cheap, no LLM call.
3. Only if still under-reports: LLM-judge fallback for failed keywords only, cached.

### M1. [Medium] Schema allows unbounded-length output; precision ~0.4 is the symptom

**Description**: No `maxItems`, prompt says 3-10 but unenforced. Agent emits ~10, padding with speculative terms (BM25 token dilution).

**Proposed fix**: Split schema into primary + synonyms:
```json
{
  "primary_keywords": {"type": "array", "minItems": 2, "maxItems": 5},
  "synonyms": {"type": "array", "maxItems": 5}
}
```

### M2. [Medium] No instruction to include paired/antonym concepts

**Description**: impact-01 missed ロールバック despite コミット present.

**Proposed fix**: Covered by H1 guidance block; standalone fallback: `- 対になる概念が存在する場合は両方含めること (例: コミット/ロールバック, 認証/認可)`.

### L1. [Low] `--max-turns 2` is slightly generous for tool-less extraction

**Proposed fix**: Set `--max-turns 1`. Measure; if schema failures appear, revert.

### L2. [Low] Prompt allows "Japanese or English" as optional

**Proposed fix**: Require both when both are in common documentation use.

### L3. [Low] No explicit instruction that keywords feed BM25

**Proposed fix**: Add `Keywords are passed directly to BM25 full-text search — prefer terms likely to appear verbatim in framework reference documents over natural-language paraphrases.`

## Positive Aspects

- Minimal prompt, no bloat
- Tools disabled + schema-constrained output is right shape for Stage 1
- `{{question}}` template placeholder clean and reusable
- review-04 at 1.00 confirms baseline prompt works when vocabulary aligns
- Scenario design exposes real failure modes

## Recommendations

1. Apply H1 + H2.1 together as Round 2. Expected: review-01 0.40 → ≥0.80, req-02 0.80 → 1.00, no regression.
2. Before adding LLM-judge: normalize expected_keywords and add synonym lists.
3. Split `primary_keywords` / `synonyms` (M1) only if Stage 2 BM25 shows precision hurting retrieval.
4. Track semantic recall (LLM-judge / embedding) offline to calibrate lexical-judge artifact.
5. Confirm impact-01 fix empirically; if ロールバック still missed, add few-shot example.
