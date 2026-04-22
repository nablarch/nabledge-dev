# Flow Comparison — 30 Scenarios (Sonnet)

**Date**: 2026-04-22
**Model**: sonnet
**Scenarios**: `tools/benchmark/scenarios/qa-v6.json` (30)

## Results

| Metric | New (ids) | Current (BM25+AI judge) | Delta |
|--------|-----------|-------------------------|-------|
| mean judge level | 2.90 | **3.00** | -0.10 |
| level=3 rate | 29/30 (97%) | **30/30 (100%)** | -1 |
| level=0 count | 1 (req-09) | 0 | +1 |
| mean cost (USD) | $0.5106 | **$0.4270** | +19% |
| total cost 30件 (USD) | $15.32 | $12.81 | +$2.51 |
| mean wall (s) | **62.7** | 86.6 | **-27%** |

Results:
- ids: `tools/benchmark/.results/20260422-185308-stage3-ids-sonnet/`
- current: `tools/benchmark/.results/20260422-185953-stage3-current-sonnet/`

## Divergence: req-09 only

- Question: 「NablarchにREST APIのレート制限機能があるか」 (out-of-scope)
- **ids**: AI-1 returned `selections=[]` → no sections → "（参照可能なセクションがありません。）" → judge level=0
- **current**: BM25 surfaced nearby handler/adapter sections → agent wrote 結論: "標準機能なし＋最も近い代替は ..." → judge level=3

Root cause: `stage1_ids.md` out-of-scope path short-circuits to empty selections,
which disables AI-3's not-built-in template path. The current flow has BM25
ambient noise that keeps the "closest-neighbor" answer alive.

## Trade-offs

**ids advantages**:
- 27% faster wall time (no multi-turn tool loop)
- Simpler — 1 AI call per stage, no agentic branching
- More reproducible — fewer moving parts (no BM25 tokenization dependency)
- Produces clean `file_id|sid` selections, easy to audit

**current advantages**:
- 19% cheaper (no 31k-token index in every AI-1 call)
- Handles out-of-scope with closest-neighbor fallback (BM25 noise)
- 100% level=3 on this scenario set

## Recommendations

To reach parity with current (100% level=3) on the new flow, one minimal
change suffices:

1. Soften `stage1_ids.md` out-of-scope rule: require 2–3 closest-neighbor
   picks even when the question is uncertain. Hard empty-list only for
   questions that are clearly outside Nablarch entirely (e.g., Spring Boot).

Cost trade-off (+19%) and benefit (more transparent, faster wall) make
the ids flow a reasonable replacement — but the decision whether to ship
is for the user to make.
